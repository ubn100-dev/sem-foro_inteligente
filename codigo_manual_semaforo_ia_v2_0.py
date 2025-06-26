import tkinter as tk
import time
import threading
import serial

# Configuración puerto Arduino
arduino = serial.Serial('COM7', 9600, timeout=1)
time.sleep(2)

# Parámetros semáforo
segundos_por_auto = 3
amarillo_duracion = 3
min_verde = 5
max_verde = 30

# Variables globales con valores iniciales
autos_cruce1 = 3
autos_cruce2 = 4

autos_lock = threading.Lock()  # Para sincronizar acceso a autos

def calcular_verde(autos):
    return max(min_verde, min(autos * segundos_por_auto, max_verde))

class SemaforoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modo Manual Semáforo")

        self.fase = 0  # 0 para cruce1, 1 para cruce2
        self.estado = 'VERDE'
        self.tiempo_inicio = time.time()
        self.duracion_verde = calcular_verde(autos_cruce1)

        # Etiquetas para mostrar info
        self.label_cruce = tk.Label(root, text="Cruce: 1", font=("Arial", 24))
        self.label_cruce.pack(pady=10)

        self.label_estado = tk.Label(root, text="Estado: VERDE", font=("Arial", 24))
        self.label_estado.pack(pady=10)

        self.label_tiempo = tk.Label(root, text="Tiempo restante: 0 s", font=("Arial", 24))
        self.label_tiempo.pack(pady=10)

        # NUEVAS etiquetas para cantidad de autos
        self.label_autos1 = tk.Label(root, text=f"Autos Cruce 1: {autos_cruce1}", font=("Arial", 20))
        self.label_autos1.pack(pady=5)

        self.label_autos2 = tk.Label(root, text=f"Autos Cruce 2: {autos_cruce2}", font=("Arial", 20))
        self.label_autos2.pack(pady=5)

        self.boton_salir = tk.Button(root, text="Salir", command=self.salir, font=("Arial", 14))
        self.boton_salir.pack(pady=10)

        self.running = True

        self.actualizar()

    def enviar_comando(self):
        if self.estado == 'VERDE':
            comando = 'GR' if self.fase == 0 else 'RG'
        elif self.estado == 'AMARILLO':
            comando = 'YR' if self.fase == 0 else 'RY'
        else:
            comando = 'RR'
        arduino.write(f"{comando}\n".encode())

    def actualizar(self):
        tiempo_actual = time.time()
        duracion = tiempo_actual - self.tiempo_inicio

        global autos_cruce1, autos_cruce2

        if self.estado == 'VERDE':
            if duracion >= self.duracion_verde:
                self.estado = 'AMARILLO'
                self.tiempo_inicio = tiempo_actual
                self.enviar_comando()

        elif self.estado == 'AMARILLO':
            if duracion >= amarillo_duracion:
                self.estado = 'ROJO'
                self.tiempo_inicio = tiempo_actual
                self.enviar_comando()

        elif self.estado == 'ROJO':
            if duracion >= 1:
                self.fase = 1 - self.fase
                with autos_lock:
                    autos = autos_cruce1 if self.fase == 0 else autos_cruce2
                self.duracion_verde = calcular_verde(autos)
                self.estado = 'VERDE'
                self.tiempo_inicio = tiempo_actual
                self.enviar_comando()

        tiempo_restante = 0
        if self.estado == 'VERDE':
            tiempo_restante = int(self.duracion_verde - duracion)
        elif self.estado == 'AMARILLO':
            tiempo_restante = int(amarillo_duracion - duracion)
        elif self.estado == 'ROJO':
            tiempo_restante = int(1 - duracion)

        self.label_cruce.config(text=f"Cruce: {self.fase + 1}")
        self.label_estado.config(text=f"Estado: {self.estado}")
        self.label_tiempo.config(text=f"Tiempo restante: {max(tiempo_restante,0)} s")

        with autos_lock:
            self.label_autos1.config(text=f"Autos Cruce 1: {autos_cruce1}")
            self.label_autos2.config(text=f"Autos Cruce 2: {autos_cruce2}")

        if self.running:
            self.root.after(200, self.actualizar)

    def salir(self):
        self.running = False
        arduino.close()
        self.root.destroy()

def consola_lectura():
    global autos_cruce1, autos_cruce2
    while True:
        try:
            entrada = input("Ingrese '1 <num>' para cruce 1 o '2 <num>' para cruce 2 (ej: '1 5'):\n").strip()
            if not entrada:
                continue
            if entrada.lower() in ['exit', 'salir', 'quit']:
                print("Saliendo...")
                break
            partes = entrada.split()
            if len(partes) != 2:
                print("Formato incorrecto.")
                continue
            cruce, valor = partes
            if cruce not in ['1', '2']:
                print("Cruce debe ser 1 o 2.")
                continue
            try:
                valor_int = int(valor)
                if valor_int < 0:
                    print("Número debe ser positivo.")
                    continue
            except:
                print("Valor no es un número válido.")
                continue
            with autos_lock:
                if cruce == '1':
                    autos_cruce1 = valor_int
                    print(f"Actualizado autos cruce 1: {autos_cruce1}")
                else:
                    autos_cruce2 = valor_int
                    print(f"Actualizado autos cruce 2: {autos_cruce2}")
        except EOFError:
            break

if __name__ == "__main__":
    root = tk.Tk()
    app = SemaforoApp(root)

    hilo_consola = threading.Thread(target=consola_lectura, daemon=True)
    hilo_consola.start()

    root.mainloop()
