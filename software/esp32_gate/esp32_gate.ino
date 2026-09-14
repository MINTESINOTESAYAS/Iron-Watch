/*  Iron-Watch gate controller  (ESP32, Arduino framework)
 *  Simulate free in Wokwi: paste this sketch + diagram.json.
 *
 *  Inputs :  METAL_PIN  <- metal detector relay contact (or a button in Wokwi)
 *            LIMIT_OPEN / LIMIT_CLOSED  <- gate end-stop switches
 *  Outputs:  BUZZER, LED_ALERT, LED_OK, motor driver (BTS7960: RPWM/LPWM)
 *  Serial  :  sends  METAL:1 / METAL:0        to the PC (attendance.py)
 *             receives OPEN / DENY / CLOSE    from the PC
 */
const int METAL_PIN     = 34;   // input only pin, active LOW with pull-up button in Wokwi
const int LIMIT_OPEN    = 32;
const int LIMIT_CLOSED  = 33;
const int BUZZER        = 25;
const int LED_ALERT     = 26;
const int LED_OK        = 27;
const int RPWM          = 18;   // BTS7960 forward PWM  (open)
const int LPWM          = 19;   // BTS7960 reverse PWM  (close)

const unsigned long AUTO_CLOSE_MS = 6000;   // gate stays open this long
const int  PWM_DUTY = 180;                  // 0-255

enum GateState { CLOSED, OPENING, OPEN, CLOSING };
GateState state = CLOSED;
unsigned long openedAt = 0;
bool lastMetal = false;
String rx;

void motor(int fwd, int rev) { analogWrite(RPWM, fwd); analogWrite(LPWM, rev); }

void setup() {
  Serial.begin(115200);
  pinMode(METAL_PIN, INPUT_PULLUP);
  pinMode(LIMIT_OPEN, INPUT_PULLUP);
  pinMode(LIMIT_CLOSED, INPUT_PULLUP);
  pinMode(BUZZER, OUTPUT); pinMode(LED_ALERT, OUTPUT); pinMode(LED_OK, OUTPUT);
  pinMode(RPWM, OUTPUT);   pinMode(LPWM, OUTPUT);
  motor(0, 0);
  Serial.println("IRONWATCH:READY");
}

void handleCommand(const String& cmd) {
  if (cmd == "OPEN" && state == CLOSED) {
    state = OPENING; motor(PWM_DUTY, 0);
    digitalWrite(LED_OK, HIGH);
  } else if (cmd == "DENY") {
    for (int i = 0; i < 3; i++) { tone(BUZZER, 1500, 120); delay(200); }
  } else if (cmd == "CLOSE" && state == OPEN) {
    state = CLOSING; motor(0, PWM_DUTY);
  }
}

void loop() {
  // --- metal detector edge -> tell the PC, sound local alarm ---
  bool metal = digitalRead(METAL_PIN) == LOW;
  if (metal != lastMetal) {
    Serial.println(metal ? "METAL:1" : "METAL:0");
    digitalWrite(LED_ALERT, metal);
    if (metal) tone(BUZZER, 2000, 400);
    lastMetal = metal;
  }

  // --- commands from the PC ---
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') { rx.trim(); handleCommand(rx); rx = ""; }
    else rx += c;
  }

  // --- gate state machine ---
  switch (state) {
    case OPENING:
      if (digitalRead(LIMIT_OPEN) == LOW) { motor(0, 0); state = OPEN; openedAt = millis(); Serial.println("GATE:OPEN"); }
      break;
    case OPEN:
      if (millis() - openedAt > AUTO_CLOSE_MS) { state = CLOSING; motor(0, PWM_DUTY); }
      break;
    case CLOSING:
      if (digitalRead(LIMIT_CLOSED) == LOW) { motor(0, 0); state = CLOSED; digitalWrite(LED_OK, LOW); Serial.println("GATE:CLOSED"); }
      break;
    default: break;
  }
}
