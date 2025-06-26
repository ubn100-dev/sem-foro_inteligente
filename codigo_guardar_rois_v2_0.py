import cv2              # Librería para procesamiento de imágenes y video
import numpy as np      # Librería para cálculos numéricos y matrices
import json             # Para guardar los datos en formato JSON
from shapely.geometry import Polygon  # Para manejar polígonos (zonas dibujadas)


# Configuración inicial

video_path = ("")  # Ruta del video o cámara. Se debe modificar con la ruta correcta

# Abrir el video

cap = cv2.VideoCapture(video_path)  # Abre el archivo de video o la cámara

if not cap.isOpened():
    print("No se pudo abrir el video.")  # Verifica si se abrió correctamente
    exit()

print("Usa D para avanzar frame. ENTER para seleccionar el frame que quieras usar.")

frame = None
# Reproduce frame por frame hasta que el usuario presione ENTER para seleccionar uno
while True:
    ret, frame = cap.read()
    if not ret:
        print("Fin del video.")
        cap.release()
        exit()

    cv2.imshow("Selecciona frame (D: avanzar, ENTER: elegir)", frame)
    key = cv2.waitKey(0)

    if key == ord('d'):
        continue  # Avanza al siguiente frame
    elif key == 13:  # ENTER
        break       # Selecciona este frame
    elif key == 27:  # ESC
        cap.release()
        cv2.destroyAllWindows()
        exit()

cv2.destroyAllWindows()  # Cierra la ventana de selección de frame

# DIBUJAR ZONAS (ROIs)

drawing = False
current_roi = []   # Zona actual en dibujo
all_rois = []      # Lista de todas las zonas finalizadas

# Función para manejar eventos del mouse
def draw_roi(event, x, y, flags, param):
    global drawing, current_roi

    if event == cv2.EVENT_LBUTTONDOWN:
        # Click izquierdo: agregar punto a la zona actual
        drawing = True
        current_roi.append((x, y))

    elif event == cv2.EVENT_RBUTTONDOWN:
        # Click derecho: cerrar la zona si tiene al menos 3 puntos
        if len(current_roi) >= 3:
            all_rois.append(Polygon(current_roi.copy()))  # Guarda la zona como polígono
            current_roi.clear()  # Limpia para empezar otra zona

# Configura la ventana y asigna la función del mouse
cv2.namedWindow("Dibuja ROIs (Click izq: agregar punto, Click der: cerrar ROI)")
cv2.setMouseCallback("Dibuja ROIs (Click izq: agregar punto, Click der: cerrar ROI)", draw_roi)

# Bucle para mostrar y dibujar las zonas
while True:
    temp_frame = frame.copy()  # Copia del frame seleccionado

    # Dibuja las zonas ya cerradas en verde
    for roi in all_rois:
        pts = np.array(list(roi.exterior.coords), np.int32).reshape((-1, 1, 2))
        cv2.polylines(temp_frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

    # Dibuja la zona actual en azul (en construcción)
    if len(current_roi) >= 1:
        for pt in current_roi:
            cv2.circle(temp_frame, pt, 5, (255, 0, 0), -1)  # Puntos azules
        cv2.polylines(temp_frame, [np.array(current_roi, np.int32)], False, (255, 0, 0), 1)

    # Texto con instrucciones
    cv2.putText(temp_frame, "ENTER: guardar zonas - ESC: cancelar", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Dibuja ROIs (Click izq: agregar punto, Click der: cerrar ROI)", temp_frame)

    key = cv2.waitKey(1)
    if key == 13:  # ENTER
        break  # Guarda y termina
    elif key == 27:  # ESC
        cap.release()
        cv2.destroyAllWindows()
        exit()

cv2.destroyAllWindows()  # Cierra ventana de dibujo

# GUARDAR ZONAS EN ARCHIVO JSON

# Serializa cada zona (lista de puntos) para poder guardarla en un archivo JSON
rois_serialized = [list(roi.exterior.coords) for roi in all_rois]

# Guarda las zonas en un archivo llamado zonas_rois.json
with open("zonas_rois.json", "w") as f:
    json.dump(rois_serialized, f)

print("Zonas guardadas exitosamente en zonas_rois.json ✅")
