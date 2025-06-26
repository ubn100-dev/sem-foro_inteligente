import cv2
import numpy as np
import json
from shapely.geometry import Polygon

#  Configuración 
video_path = ("") #Ahí va la ruta del video para simular o la cam

#  Abrir video 
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("No se pudo abrir el video.")
    exit()

print("Usa D para avanzar frame. ENTER para seleccionar el frame que quieras usar.")

frame = None
while True:
    ret, frame = cap.read()
    if not ret:
        print("Fin del video.")
        cap.release()
        exit()

    cv2.imshow("Selecciona frame (D: avanzar, ENTER: elegir)", frame)
    key = cv2.waitKey(0)

    if key == ord('d'):
        continue
    elif key == 13:  # ENTER
        break
    elif key == 27:  # ESC
        cap.release()
        cv2.destroyAllWindows()
        exit()

cv2.destroyAllWindows()

# Dibujar ROIs 
drawing = False
current_roi = []
all_rois = []

def draw_roi(event, x, y, flags, param):
    global drawing, current_roi

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        current_roi.append((x, y))

    elif event == cv2.EVENT_RBUTTONDOWN:
        if len(current_roi) >= 3:
            all_rois.append(Polygon(current_roi.copy()))
            current_roi.clear()

cv2.namedWindow("Dibuja ROIs (Click izq: agregar punto, Click der: cerrar ROI)")
cv2.setMouseCallback("Dibuja ROIs (Click izq: agregar punto, Click der: cerrar ROI)", draw_roi)

while True:
    temp_frame = frame.copy()

    for roi in all_rois:
        pts = np.array(list(roi.exterior.coords), np.int32).reshape((-1, 1, 2))
        cv2.polylines(temp_frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

    if len(current_roi) >= 1:
        for pt in current_roi:
            cv2.circle(temp_frame, pt, 5, (255, 0, 0), -1)
        cv2.polylines(temp_frame, [np.array(current_roi, np.int32)], False, (255, 0, 0), 1)

    cv2.putText(temp_frame, "ENTER: guardar zonas - ESC: cancelar", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Dibuja ROIs (Click izq: agregar punto, Click der: cerrar ROI)", temp_frame)

    key = cv2.waitKey(1)
    if key == 13:  # ENTER
        break
    elif key == 27:  # ESC
        cap.release()
        cv2.destroyAllWindows()
        exit()

cv2.destroyAllWindows()

# Guardar ROIs 
rois_serialized = [list(roi.exterior.coords) for roi in all_rois]
with open("zonas_rois.json", "w") as f:
    json.dump(rois_serialized, f)

print("Zonas guardadas exitosamente en zonas_rois.json ✅")
