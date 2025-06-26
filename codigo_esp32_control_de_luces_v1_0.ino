#include <WiFi.h>

// Pines 
const int verde1 = 4;
const int amarillo1 =21;
const int rojo1 = 16;
const int verde2 = 17;
const int amarillo2 = 18;
const int rojo2 = 5;

// WiFi config
const char* ssid = "HUAWEI-2.4G-R7aP";
const char* password = "cYn452Ep";

WiFiServer server(80);
String ultimo_comando = "";  // Para evitar repetir acciones

void setup() {
  Serial.begin(115200);

  pinMode(verde1, OUTPUT);
  pinMode(amarillo1, OUTPUT);
  pinMode(rojo1, OUTPUT);
  pinMode(verde2, OUTPUT);
  pinMode(amarillo2, OUTPUT);
  pinMode(rojo2, OUTPUT);
  apagarSemaforos();

  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConectado a WiFi");
  Serial.print("Dirección IP local: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    String comando = client.readStringUntil('\n');
    comando.trim();
    Serial.println("Comando recibido: " + comando);

    if (comando != ultimo_comando) {
      if (comando == "GR") {
        setSemaforo(true, false, false, false, false, true);
      }
      else if (comando == "RG") {
        setSemaforo(false, false, true, true, false, false);
      }
      else if (comando == "YR") {
        setSemaforo(false, true, false, false, false, true);
      }
      else if (comando == "RY") {
        setSemaforo(false, false, true, false, true, false);
      }
      else if (comando == "RR") {
        setSemaforo(false, false, true, false, false, true);
      }
      else if (comando == "RESET") {
        apagarSemaforos();
      } else {
        Serial.println("⚠️ Comando no reconocido.");
      }

      ultimo_comando = comando;
    }

    client.println("OK");
    client.stop();
  }
}

void setSemaforo(bool v1, bool a1, bool r1, bool v2, bool a2, bool r2) {
  Serial.println("Actualizando semáforo:");
  Serial.printf("Cruce 1 -> Verde: %d, Amarillo: %d, Rojo: %d\n", v1, a1, r1);
  Serial.printf("Cruce 2 -> Verde: %d, Amarillo: %d, Rojo: %d\n", v2, a2, r2);

  digitalWrite(verde1, v1);
  digitalWrite(amarillo1, a1);
  digitalWrite(rojo1, r1);

  digitalWrite(verde2, v2);
  digitalWrite(amarillo2, a2);
  digitalWrite(rojo2, r2);
}

void apagarSemaforos() {
  Serial.println("Apagando todos los semáforos.");
  digitalWrite(verde1, LOW);
  digitalWrite(amarillo1, LOW);
  digitalWrite(rojo1, LOW);
  digitalWrite(verde2, LOW);
  digitalWrite(amarillo2, LOW);
  digitalWrite(rojo2, LOW);
}
