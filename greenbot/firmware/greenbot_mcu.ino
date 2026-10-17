// GreenBot real-time MCU (ESP32-S3). The Pi sends velocity commands over UART;
// this board owns motors, cliff, bumpers and the watchdog so safety never depends on Linux.
// Protocol (115200 8N1, newline-terminated):  V <left_mm_s> <right_mm_s> <fan_pct> <brush_pct>
// Telemetry (50 Hz):                          T <batt_mv> <cliffMask> <bumpMask> <ampsL> <ampsR> <encL> <encR>
#include <Wire.h>
#include <Adafruit_VL53L1X.h>

const int PIN_L_PWM = 4, PIN_L_DIR = 5, PIN_R_PWM = 6, PIN_R_DIR = 7;
const int PIN_FAN = 15, PIN_BRUSH = 16, PIN_BUMP[3] = {8, 9, 10};
const int CLIFF_XSHUT[4] = {11, 12, 13, 14};
const uint16_t CLIFF_MM = 60;
const uint32_t WATCHDOG_MS = 500;

Adafruit_VL53L1X tof[4];
volatile long encL = 0, encR = 0;
uint32_t lastCmd = 0;
int tgtL = 0, tgtR = 0, fan = 0, brush = 0;

void drive(int pwmPin, int dirPin, int mmps) {
  digitalWrite(dirPin, mmps >= 0);
  analogWrite(pwmPin, min(255, abs(mmps) * 255 / 300));  // 300 mm/s = full scale
}

void stopAll() { tgtL = tgtR = fan = brush = 0; }

void setup() {
  Serial.begin(115200);  // UART to Pi
  Wire.begin();
  for (int p : {PIN_L_PWM, PIN_L_DIR, PIN_R_PWM, PIN_R_DIR, PIN_FAN, PIN_BRUSH}) pinMode(p, OUTPUT);
  for (int p : PIN_BUMP) pinMode(p, INPUT_PULLUP);
  for (int i = 0; i < 4; i++) {  // bring up ToF sensors one at a time to assign addresses
    pinMode(CLIFF_XSHUT[i], OUTPUT); digitalWrite(CLIFF_XSHUT[i], LOW);
  }
  for (int i = 0; i < 4; i++) {
    digitalWrite(CLIFF_XSHUT[i], HIGH); delay(10);
    tof[i].begin(0x30 + i, &Wire); tof[i].startRanging();
  }
}

void loop() {
  while (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    if (line.startsWith("V ")) {
      sscanf(line.c_str(), "V %d %d %d %d", &tgtL, &tgtR, &fan, &brush);
      lastCmd = millis();
    }
  }
  uint8_t cliff = 0, bump = 0;
  for (int i = 0; i < 4; i++)
    if (tof[i].dataReady() && tof[i].distance() > CLIFF_MM) cliff |= 1 << i;
  for (int i = 0; i < 3; i++) if (!digitalRead(PIN_BUMP[i])) bump |= 1 << i;

  // Hard safety, independent of the Pi: cliff / lost heartbeat => stop immediately.
  if (cliff || millis() - lastCmd > WATCHDOG_MS) stopAll();
  if (bump) { tgtL = min(tgtL, 0); tgtR = min(tgtR, 0); }  // only allow reverse after contact

  drive(PIN_L_PWM, PIN_L_DIR, tgtL);
  drive(PIN_R_PWM, PIN_R_DIR, tgtR);
  analogWrite(PIN_FAN, fan * 255 / 100);
  analogWrite(PIN_BRUSH, brush * 255 / 100);

  static uint32_t t = 0;
  if (millis() - t >= 20) {
    t = millis();
    Serial.printf("T 0 %u %u 0 0 %ld %ld\n", cliff, bump, encL, encR);  // TODO: wire ADC + INA226
  }
}
