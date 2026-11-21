/* AVIVA | Simulação do monitor de enchentes no ESP32.
   Combina nível da água e chuva simulada para exibir alertas experimentais locais. */
#include <Arduino.h>
#include <DHTesp.h>
#include <math.h>

constexpr int PIN_TRIG = 5;
constexpr int PIN_ECHO = 18;
constexpr int PIN_CHUVA = 34;      
constexpr int PIN_DHT = 4;         
constexpr int LED_NORMAL = 23;    
constexpr int LED_ATENCAO = 22;   
constexpr int LED_CRITICO = 21;   
constexpr int PIN_BUZZER = 19;

constexpr float ALTURA_REFERENCIA_CM = 300.0f;  
constexpr unsigned long INTERVALO_MS = 2000UL;
constexpr unsigned long TIMEOUT_ECHO_US = 30000UL;

unsigned long ultimaLeitura = 0;
DHTesp sensorAmbiente;

enum Nivel { NORMAL = 0, ATENCAO = 1, CRITICO = 2 };
const char* rotuloNivel(Nivel n) {
  switch (n) {
    case NORMAL: return "NORMAL";
    case ATENCAO: return "ATENCAO";
    default: return "CRITICO";
  }
}
Nivel classificarEvento(float nivelAguaCm, float chuvaMmH) {
  
  
  bool aguaCritica = nivelAguaCm >= 200.0f;
  bool chuvaCritica = chuvaMmH >= 50.0f;
  if (aguaCritica || chuvaCritica) return CRITICO;
  bool aguaAtencao = nivelAguaCm >= 120.0f;
  bool chuvaAtencao = chuvaMmH >= 25.0f;
  if (aguaAtencao && chuvaAtencao) return CRITICO;
  if (aguaAtencao || chuvaAtencao) return ATENCAO;
  return NORMAL;
}

bool lerNivelAgua(float &nivelAguaCm) {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  unsigned long duracaoUs = pulseIn(PIN_ECHO, HIGH, TIMEOUT_ECHO_US);
  if (duracaoUs == 0) {
    Serial.println("DIAGNOSTICO;HC-SR04;SEM_ECHO;VERIFICAR_FIO_AZUL_ECHO_GPIO18");
    return false;  
  }

  float distanciaCm = duracaoUs / 58.0f;
  if (distanciaCm < 2.0f || distanciaCm > 400.0f) return false;
  nivelAguaCm = constrain(ALTURA_REFERENCIA_CM - distanciaCm, 0.0f,
                         ALTURA_REFERENCIA_CM);
  return true;
}

float lerChuvaSimulada() {
  int leituraAdc = analogRead(PIN_CHUVA);  
  leituraAdc = constrain(leituraAdc, 0, 4095);
  return 200.0f * leituraAdc / 4095.0f;
}


void avisoSonoro(uint16_t frequenciaHz, uint16_t duracaoMs) {
  if (frequenciaHz == 0) return;
  const uint32_t meioPeriodoUs = 500000UL / frequenciaHz;
  const uint32_t ciclos = (uint32_t)frequenciaHz * duracaoMs / 1000UL;
  for (uint32_t i = 0; i < ciclos; i++) {
    digitalWrite(PIN_BUZZER, HIGH);
    delayMicroseconds(meioPeriodoUs);
    digitalWrite(PIN_BUZZER, LOW);
    delayMicroseconds(meioPeriodoUs);
  }
  digitalWrite(PIN_BUZZER, LOW);
}

void sinalizar(Nivel nivel) {
  digitalWrite(LED_NORMAL, nivel == NORMAL ? HIGH : LOW);
  digitalWrite(LED_ATENCAO, nivel == ATENCAO ? HIGH : LOW);
  digitalWrite(LED_CRITICO, nivel == CRITICO ? HIGH : LOW);
  if (nivel == CRITICO) {
    avisoSonoro(1800, 220);  
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_CHUVA, INPUT);
  sensorAmbiente.setup(PIN_DHT, DHTesp::DHT22);
  pinMode(LED_NORMAL, OUTPUT);
  pinMode(LED_ATENCAO, OUTPUT);
  pinMode(LED_CRITICO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);
  digitalWrite(PIN_TRIG, LOW);
  sinalizar(NORMAL);
  Serial.println("AVIVA | TESTE DE LABORATORIO - NUNCA UTILIZE PARA ALERTA REAL");
  Serial.println("origem;tempo_s;nivel_agua_cm;chuva_mm_h;umidade_pct;classificacao;qualidade");
}

void loop() {
  unsigned long agora = millis();
  if (agora - ultimaLeitura < INTERVALO_MS) return;
  ultimaLeitura = agora;

  float nivelAguaCm = 0.0f;
  bool leituraValida = lerNivelAgua(nivelAguaCm);
  float chuvaMmH = lerChuvaSimulada();
  TempAndHumidity ambiente = sensorAmbiente.getTempAndHumidity();
  bool ambienteValido = !isnan(ambiente.humidity) &&
                        ambiente.humidity >= 0.0f && ambiente.humidity <= 100.0f;

  
  
  if (!leituraValida) {
    digitalWrite(LED_NORMAL, LOW);
    digitalWrite(LED_ATENCAO, LOW);
    digitalWrite(LED_CRITICO, HIGH);
    avisoSonoro(1000, 160);
    Serial.printf("AVIVA_IOT;%lu;NA;%.1f;NA;INDETERMINADO;FALHA_SENSOR_NIVEL\n",
                  agora / 1000UL, chuvaMmH);
    return;
  }

  Nivel estado = classificarEvento(nivelAguaCm, chuvaMmH);
  sinalizar(estado);
  if (ambienteValido) {
    Serial.printf("AVIVA_IOT;%lu;%.1f;%.1f;%.1f;%s;SIMULADO\n", agora / 1000UL,
                  nivelAguaCm, chuvaMmH, ambiente.humidity, rotuloNivel(estado));
  } else {
    Serial.printf("AVIVA_IOT;%lu;%.1f;%.1f;NA;%s;SIMULADO_DHT22_INDISPONIVEL\n",
                  agora / 1000UL, nivelAguaCm, chuvaMmH, rotuloNivel(estado));
  }

}

