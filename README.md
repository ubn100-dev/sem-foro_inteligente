# 🚦 Proyecto: Semáforo Automatizado con Detección en Tiempo Real

## 🎯 Objetivo
Optimizar el flujo vehicular en intersecciones congestionadas mediante un sistema de semáforos inteligente que ajusta dinámicamente los tiempos de luces (verde/rojo) basado en el volumen de tráfico detectado por IA (OpenCV + Roboflow). Desarrollado para la intersección crítica de *Av. 28 de Julio con Paseo de la República en Lima*.

## 👥 Integrantes
- **Añazco Urcia Jorge Arturo** – Rol: Hardware (Diseño electrónico y montaje)
- **Carrasco Nuñez Axl Gabriel** – Rol: Software (Programación Arduino + Python)
- **Chavez Pacherre Jhoswin Wilder** – Rol: IA/ML (Entrenamiento modelo Roboflow)
- **Alva Huaman Geiner Steve** – Rol: Simulación (Proteus/Tinkercad)
- **Velarde Cristóbal Elvis Mervin** – Rol: Documentación y pruebas

## 📁 Estructura del proyecto
https://utpedupe-my.sharepoint.com/:f:/g/personal/u21322528_utp_edu_pe/EtikuJpp6EBAkdOij-xqh_oBvnbyOeyloDZmsH7t-3uDNA?e=1P3YCz 

## 📊 Métricas Clave
| Variable | Resultado | Mejora vs Sistema Tradicional |
|----------|-----------|-------------------------------|
| Tiempo de espera promedio | 38 segundos | ↓ 36.6% |
| Precisión de detección | 92% | ↑ 15% |
| Eficiencia energética | 75% | ↑ 20% |


## 📦 Requisitos del Sistema

### Python

- Python 3.8 o superior
- Sistema operativo Windows, Linux o macOS

## 📚 Librerías necesarias

### 1. Instalación de dependencias

```bash
pip install opencv-python
pip install numpy
pip install pyserial
pip install shapely
pip install ultralytics

2. Pasos
a. Conectar el sistema
b. Compilar el codigo codigo_esp32_control_de_luces_v1_0.ino en el esp32
c. Ejecutar el codigo codigo_guardar_rois_v2_0.py
d. Seleccionar y guardar la zona de interés
e. Abrir el codigo del semaforo codigo_semaforo_ia_v2_0.py

## 🔗 Enlaces relevantes
- [📂 Carpeta compartida en Drive](https://utpedupe-my.sharepoint.com/personal/u21322528_utp_edu_pe/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fu21322528_utp_edu_pe%2FDocuments%2FEstructura%20del%20proyecto&ga=1)

## 💡 Cómo contribuir
1. Clona el repositorio:  
   ```bash
   git clone https://github.com/ubn100-dev/sem-foro_inteligente.git
