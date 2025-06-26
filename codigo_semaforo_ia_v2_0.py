# IMPORTACIÓN DE LIBRERÍAS

import cv2                    # OpenCV para procesamiento de video
import numpy as np            # Operaciones matemáticas
import json                   # Lectura y escritura de archivos JSON
import socket                 # Comunicación con el ESP32 vía TCP
import time                   # Control de tiempo y temporizadores
from shapely.geometry import Polygon, Point  # Para trabajar con zonas (polígonos)
from ultralytics import YOLO  # YOLOv8 para detección de objetos

# CARGA DEL MODELO YOLO

model = YOLO('yolov8n.pt')  # Se carga el modelo YOLOv8 versión "nano"

# PARÁMETROS DE CONFIGURACIÓN

modo_manual = False  # Si es True, el conteo se ingresa manualmente
ESP32_IP = ''  # IP del ESP32 (debe estar en la misma red)
ESP32_PORT = 80             # Puerto TCP del ESP32

# CARGA DE ZONAS (ROIs)

with open("zonas_rois.json", "r") as f:
    rois_data = json.load(f)
all_rois = [Polygon(roi) for roi in rois_data]  # Se convierten en objetos de tipo polígono

# PARÁMETROS DEL SEMÁFORO

segundos_por_auto = 3        # Cada auto representa esta cantidad de segundos en verde
amarillo_duracion = 3        # Duración fija de la luz amarilla
min_verde = 5                # Duración mínima del verde
max_verde = 30               # Duración máxima del verde
retardo_interseccion = 1     # Tiempo de espera entre cambios de cruce

# CAPTURA DE VIDEO

cap = cv2.VideoCapture(0)  # Usa la cámara principal (puedes cambiar por archivo de video)
if not cap.isOpened():
    print("No se pudo abrir el video.")
    exit()

# ESTADO INICIAL DE SEMÁFOROS

estado_s1 = 'VERDE'
estado_s2 = 'ROJO'
inicio_s1 = time.time()
inicio_s2 = time.time()

# Conteo de autos por zona
conteo_actual = [0 for _ in all_rois]

# FUNCIÓN PARA CALCULAR DURACIÓN VERDE

def calcular_verde(autos):
    return max(min_verde, min(autos * segundos_por_auto, max_verde))

verde_duracion_s1 = min_verde
verde_duracion_s2 = min_verde

# Variables para controlar retardo entre cruces
esperando_s2 = False
inicio_espera_s2 = None
esperando_s1 = False
inicio_espera_s1 = None

# FUNCIÓN PARA ENVIAR COMANDOS AL ESP32

ultimo_comando = ""

def enviar_comando_esp32(comando):
    global ultimo_comando
    if comando != ultimo_comando:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ESP32_IP, ESP32_PORT))
                s.sendall(f"{comando}\n".encode())  # Envío del comando
                s.recv(1024)  # Recibe confirmación del ESP32
                print("Comando enviado al ESP32:", comando)
                ultimo_comando = comando
        except Exception as e:
            print("Error al enviar comando:", e)

# BUCLE PRINCIPAL

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # DETECCIÓN DE VEHÍCULOS

    if not modo_manual:
        conteo_actual = [0 for _ in all_rois]  # Reinicia conteo
        results = model(frame, verbose=False)[0]
        for box in results.boxes:
            cls = int(box.cls[0])
            # Solo cuenta autos, motos, buses y camiones
            if cls in [2, 3, 5, 7]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                point = Point(cx, cy)
                # Verifica si el centro del vehículo está dentro de una zona
                for idx, roi in enumerate(all_rois):
                    if roi.contains(point):
                        conteo_actual[idx] += 1
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                        break
    else:
        # Entrada manual de conteo por consola
        try:
            conteo_actual[0] = int(input("Vehículos en Cruce 1: "))
            conteo_actual[1] = int(input("Vehículos en Cruce 2: "))
        except:
            conteo_actual = [0, 0]

    # CONTROL DE ESTADO DE SEMÁFOROS

    tiempo_actual = time.time()
    verde_duracion_s1 = calcular_verde(conteo_actual[0])
    verde_duracion_s2 = calcular_verde(conteo_actual[1])

    # Cambios de estado para Semáforo 1
    duracion_fase_s1 = tiempo_actual - inicio_s1
    if estado_s1 == 'VERDE' and duracion_fase_s1 >= verde_duracion_s1:
        estado_s1 = 'AMARILLO'
        inicio_s1 = tiempo_actual
    elif estado_s1 == 'AMARILLO' and duracion_fase_s1 >= amarillo_duracion:
        estado_s1 = 'ROJO'
        inicio_s1 = tiempo_actual
        esperando_s2 = True
        inicio_espera_s2 = tiempo_actual

    # Cambios de estado para Semáforo 2
    duracion_fase_s2 = tiempo_actual - inicio_s2
    if estado_s2 == 'ROJO' and esperando_s2:
        if tiempo_actual - inicio_espera_s2 >= retardo_interseccion:
            estado_s2 = 'VERDE'
            inicio_s2 = tiempo_actual
            esperando_s2 = False
    else:
        if estado_s2 == 'VERDE' and duracion_fase_s2 >= verde_duracion_s2:
            estado_s2 = 'AMARILLO'
            inicio_s2 = tiempo_actual
        elif estado_s2 == 'AMARILLO' and duracion_fase_s2 >= amarillo_duracion:
            estado_s2 = 'ROJO'
            inicio_s2 = tiempo_actual
            esperando_s1 = True
            inicio_espera_s1 = tiempo_actual

    if estado_s1 == 'ROJO' and esperando_s1:
        if tiempo_actual - inicio_espera_s1 >= retardo_interseccion:
            estado_s1 = 'VERDE'
            inicio_s1 = tiempo_actual
            esperando_s1 = False

    # FUNCIÓN PARA TIEMPO RESTANTE

    def tiempo_restante(estado, duracion_fase, verde_duracion):
        if estado == 'VERDE':
            return int(max(verde_duracion - duracion_fase, 0))
        elif estado == 'AMARILLO':
            return int(max(amarillo_duracion - duracion_fase, 0))
        else:
            return int(max(verde_duracion + amarillo_duracion + retardo_interseccion - duracion_fase, 0))

    # ENVÍO DE COMANDOS AL ESP32
    
    tiempo_rest_s1 = tiempo_restante(estado_s1, tiempo_actual - inicio_s1, verde_duracion_s1)
    tiempo_rest_s2 = tiempo_restante(estado_s2, tiempo_actual - inicio_s2, verde_duracion_s2)

    comando_s1 = 'G' if estado_s1 == 'VERDE' else ('Y' if estado_s1 == 'AMARILLO' else 'R')
    comando_s2 = 'G' if estado_s2 == 'VERDE' else ('Y' if estado_s2 == 'AMARILLO' else 'R')
    comando = comando_s1 + comando_s2  # Ejemplo: 'GR', 'RY', etc.

    enviar_comando_esp32(comando)

    # VISUALIZACIÓN

    for idx, roi in enumerate(all_rois):
        pts = np.array(list(roi.exterior.coords), np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
        cv2.putText(frame, f"Cruce {idx+1}: {conteo_actual[idx]} autos", (10, 30 + idx * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

    # Mostrar estado de semáforos en pantalla
    cv2.putText(frame, f"Semaforo 1: {estado_s1}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.putText(frame, f"Semaforo 2: {estado_s2}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Semaforo y Conteo", frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
