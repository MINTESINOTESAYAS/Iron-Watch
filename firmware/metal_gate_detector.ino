/*
  IronWatch — Factory ferrous-theft gate
  ======================================
  FIX: A0 = 0 IS THE TRIGGER.

  Why the old sketch never alarmed
  --------------------------------
  analogRead(A0) is stuck at 0 because 4046 pin 10 (DEMOD) is an
  internal source-follower of pin 9 (VCOIN). VCOIN was left floating,
  so DEMOD sits at 0 V and analogRead returns 0.

  The previous logic was:

      metalDetected = (sensorValue > 600);

  0 is never greater than 600, so the alarm could not fire.

  This sketch inverts that: a collapsed / zero demod voltage means
  ferrous metal is in the coil field (PLL unlocked / amplitude dump).

      metalDetected = (sensorValue <= METAL_THRESHOLD);   // default 40

  Proteus wiring that actually lets A0 CHANGE (do this or A0 stays 0):
      RV1 wiper  ->  4046 pin 9 (VCOIN)
      4046 pin 10 (DEMOD) ->  Arduino A0     (already wired)

  Fast Proteus demo (skip the 4046 analog path):
      RV1 wiper  ->  Arduino A0 directly

  Pin map (matches the schematic from the Proteus build)
      A0  4046 DEMOD          ferrous discrimination voltage
      D0  RX  <- Virtual Terminal TXD
      D1  TX  -> Virtual Terminal RXD
      D2  LED-RED             alarm
      D3  LED-GREEN           clear
      D4  BUZ1                buzzer

  Virtual Terminal (9600 baud)
      Type A1B2C3 + Enter     authorized badge, 5 s window
      Type HELP               command list
      Type STATUS             one-shot dump
      Type MODE LOW           A0 near 0 = metal   (default, what you want)
      Type MODE HIGH          A0 above threshold = metal  (old behaviour)
      Type TH 40              set threshold (0-1023)
*/

const int PIN_SENSOR  = A0;
const int PIN_LED_RED = 2;
const int PIN_LED_GRN = 3;
const int PIN_BUZZER  = 4;

// A0 ADC counts. Anything AT OR BELOW this is treated as metal.
int metalThreshold = 40;
int hysteresis     = 20;

// 1 = trigger when A0 is low/zero (what you asked for)
// 0 = trigger when A0 is high     (old broken-for-you behaviour)
int detectOnLow = 1;

const char AUTHORIZED_ID[]     = "A1B2C3";
const unsigned long AUTH_MS    = 5000;
const unsigned long PRINT_MS   = 250;

String inputBuffer;
bool authorized     = false;
bool metalLatched   = false;
bool lastAlarm      = false;
unsigned long lastAuthMs  = 0;
unsigned long lastPrintMs = 0;

void setup() {
  Serial.begin(9600);

  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_LED_GRN, OUTPUT);
  pinMode(PIN_BUZZER,  OUTPUT);

  applyOutputs(false);

  Serial.println(F(""));
  Serial.println(F("=== IRONWATCH GATE ONLINE ==="));
  Serial.println(F("TRIGGER MODE: A0 LOW / ZERO = METAL"));
  Serial.println(F("If A0 stays 0, alarm WILL fire. That is intended."));
  Serial.println(F("Wire RV1 wiper -> 4046 VCOIN (pin 9) so A0 can rise."));
  Serial.println(F("Badge: type A1B2C3 then Enter. Commands: HELP"));
  Serial.println(F("-------------------------------------------"));
}

void loop() {
  handleSerial();
  expireAuth();

  int adc = analogRead(PIN_SENSOR);
  bool metal = evaluateMetal(adc);
  bool alarm = metal && !authorized;

  applyOutputs(alarm);
  printLive(adc, metal, alarm);

  delay(20);
}

bool evaluateMetal(int adc) {
  if (detectOnLow) {
    if (!metalLatched && adc <= metalThreshold) metalLatched = true;
    if ( metalLatched && adc >  metalThreshold + hysteresis) metalLatched = false;
  } else {
    if (!metalLatched && adc >= metalThreshold) metalLatched = true;
    if ( metalLatched && adc <  metalThreshold - hysteresis) metalLatched = false;
  }
  return metalLatched;
}

void applyOutputs(bool alarm) {
  digitalWrite(PIN_LED_RED, alarm ? HIGH : LOW);
  digitalWrite(PIN_LED_GRN, alarm ? LOW  : HIGH);
  digitalWrite(PIN_BUZZER,  alarm ? HIGH : LOW);
}

void printLive(int adc, bool metal, bool alarm) {
  unsigned long now = millis();
  bool changed = (alarm != lastAlarm);
  if (!changed && (now - lastPrintMs < PRINT_MS)) return;
  lastPrintMs = now;
  lastAlarm = alarm;

  float volts = adc * (5.0 / 1023.0);

  Serial.print(F("A0="));
  Serial.print(adc);
  Serial.print(F("  V="));
  Serial.print(volts, 2);
  Serial.print(F("  METAL="));
  Serial.print(metal ? F("YES") : F("no "));
  Serial.print(F("  AUTH="));
  Serial.print(authorized ? F("YES") : F("no "));
  Serial.print(F("  ALARM="));
  Serial.print(alarm ? F("ON ***") : F("off"));
  if (adc == 0 && detectOnLow) Serial.print(F("  [A0=0 TRIGGER]"));
  Serial.println();

  if (changed && alarm) {
    Serial.println(F("*** ALARM: unauthorized ferrous signature ***"));
  }
  if (changed && !alarm) {
    Serial.println(F("Clear."));
  }
}

void expireAuth() {
  if (authorized && (millis() - lastAuthMs > AUTH_MS)) {
    authorized = false;
    Serial.println(F(">> Authorization expired."));
  }
}

void handleSerial() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (inputBuffer.length() > 0) {
        inputBuffer.trim();
        runCommand(inputBuffer);
        inputBuffer = "";
      }
    } else if (inputBuffer.length() < 48) {
      inputBuffer += c;
    }
  }
}

void runCommand(String cmd) {
  cmd.toUpperCase();

  if (cmd == "HELP" || cmd == "?") {
    Serial.println(F("A1B2C3     authorize 5s"));
    Serial.println(F("STATUS     dump now"));
    Serial.println(F("MODE LOW   A0=0 triggers   (default)"));
    Serial.println(F("MODE HIGH  A0 high triggers"));
    Serial.println(F("TH 40      set ADC threshold"));
    return;
  }

  if (cmd == "STATUS") {
    lastPrintMs = 0;
    return;
  }

  if (cmd == "MODE LOW") {
    detectOnLow = 1;
    metalLatched = false;
    Serial.println(F(">> MODE=LOW  (A0 near 0 = metal = TRIGGER)"));
    return;
  }

  if (cmd == "MODE HIGH") {
    detectOnLow = 0;
    metalLatched = false;
    Serial.println(F(">> MODE=HIGH (A0 above threshold = metal)"));
    return;
  }

  if (cmd.startsWith("TH ")) {
    int v = cmd.substring(3).toInt();
    if (v < 0) v = 0;
    if (v > 1023) v = 1023;
    metalThreshold = v;
    Serial.print(F(">> threshold = "));
    Serial.println(metalThreshold);
    return;
  }

  if (cmd == AUTHORIZED_ID) {
    authorized = true;
    lastAuthMs = millis();
    Serial.println(F(">> Badge ACCEPTED. Authorized 5 seconds."));
    return;
  }

  Serial.print(F(">> Badge REJECTED: "));
  Serial.println(cmd);
}
