#include <WiFi.h>  // Librería para manejar conexión WiFi en el ESP32

// Definición de pines para los LEDs de los semáforos
const int verde1 = 4;
const int amarillo1 = 21;
const int rojo1 = 16;
const int verde2 = 17;
const int amarillo2 = 18;
const int rojo2 = 5;

// Datos de red WiFi a la que se conectará el ESP32
const char* ssid = "";     // Nombre de la red WiFi
const char* password = "";         // Contraseña de la red

WiFiServer server(80);  // Se crea un servidor web en el puerto 80
String ultimo_comando = "";  // Variable para almacenar el último comando recibido y evitar repeticiones

void setup() {
  Serial.begin(115200);  // Inicia la comunicación serie para depuración

  // Configuración de pines como salidas (para controlar los LEDs)
  pinMode(verde1, OUTPUT);
  pinMode(amarillo1, OUTPUT);
  pinMode(rojo1, OUTPUT);
  pinMode(verde2, OUTPUT);
  pinMode(amarillo2, OUTPUT);
  pinMode(rojo2, OUTPUT);

  apagarSemaforos();  // Apaga todos los LEDs al iniciar

  // Conexión a la red WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {  // Espera hasta que se conecte
    delay(500);
    Serial.print(".");
  }

  // Muestra información de conexión en el monitor serie
  Serial.println("\nConectado a WiFi");
  Serial.print("Dirección IP local: ");
  Serial.println(WiFi.localIP());  // Imprime la IP local del ESP32

  server.begin();  // Inicia el servidor web
}

void loop() {
  // Espera a que un cliente (como una app o navegador) se conecte
  WiFiClient client = server.available();
  if (client) {
    // Lee la línea enviada por el cliente
    String comando = client.readStringUntil('\n');
    comando.trim();  // Elimina espacios o saltos de línea innecesarios
    Serial.println("Comando recibido: " + comando);

    // Solo ejecuta si el comando es diferente al anterior
    if (comando != ultimo_comando) {
      // Según el comando recibido, cambia el estado de los semáforos
      if (comando == "GR") {              // Verde en cruce 1, Rojo en cruce 2
        setSemaforo(true, false, false, false, false, true);
      }
      else if (comando == "RG") {         // Rojo en cruce 1, Verde en cruce 2
        setSemaforo(false, false, true, true, false, false);
      }
      else if (comando == "YR") {         // Amarillo en cruce 1, Rojo en cruce 2
        setSemaforo(false, true, false, false, false, true);
      }
      else if (comando == "RY") {         // Rojo en cruce 1, Amarillo en cruce 2
        setSemaforo(false, false, true, false, true, false);
      }
      else if (comando == "RR") {         // Rojo en ambos cruces
        setSemaforo(false, false, true, false, false, true);
      }
      else if (comando == "RESET") {      // Apaga todos los LEDs
        apagarSemaforos();
      } else {
        Serial.println("⚠️ Comando no reconocido.");
      }

      // Actualiza el último comando recibido
      ultimo_comando = comando;
    }

    client.println("OK");  // Envía confirmación al cliente
    client.stop();         // Cierra la conexión con el cliente
  }
}

// Función para encender/apagar cada LED de los dos semáforos
void setSemaforo(bool v1, bool a1, bool r1, bool v2, bool a2, bool r2) {
  Serial.println("Actualizando semáforo:");
  Serial.printf("Cruce 1 -> Verde: %d, Amarillo: %d, Rojo: %d\n", v1, a1, r1);
  Serial.printf("Cruce 2 -> Verde: %d, Amarillo: %d, Rojo: %d\n", v2, a2, r2);

  // Semáforo del cruce 1
  digitalWrite(verde1, v1);
  digitalWrite(amarillo1, a1);
  digitalWrite(rojo1, r1);

  // Semáforo del cruce 2
  digitalWrite(verde2, v2);
  digitalWrite(amarillo2, a2);
  digitalWrite(rojo2, r2);
}

// Apaga todos los LEDs de los dos semáforos
void apagarSemaforos() {
  Serial.println("Apagando todos los semáforos.");
  digitalWrite(verde1, LOW);
  digitalWrite(amarillo1, LOW);
  digitalWrite(rojo1, LOW);
  digitalWrite(verde2, LOW);
  digitalWrite(amarillo2, LOW);
  digitalWrite(rojo2, LOW);
}
