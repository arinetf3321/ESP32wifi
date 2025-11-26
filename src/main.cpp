#include <Arduino.h>

// Pin definitions
const int blinkLedPin = 14;     // LED pin for blinking
const int nirLedPin = 23;       // NIR LED (PWM controlled)
const int photodiodePin = 34;   // Analog pin for photodiode input

// PWM setup
const int pwmChannel = 0;       // PWM channel
const int pwmFreq = 5000;       // 5 kHz frequency
const int pwmResolution = 8;    // 8-bit resolution (0–255 duty)
 
// Timing variables
unsigned long pulseTime;
unsigned long returnTime;
unsigned long roundTripTime;

// Number of sensor positions (10x10 grid)
const int gridSize = 10;
int sensorGrid[gridSize][gridSize];  // A 2D array to represent sensor positions

void setup() {
  pinMode(blinkLedPin, OUTPUT);
  pinMode(photodiodePin, INPUT);

  // Setup PWM for NIR LED
  ledcSetup(pwmChannel, pwmFreq, pwmResolution);
  ledcAttachPin(nirLedPin, pwmChannel);

  Serial.begin(115200);
  Serial.println("System started...");
}

void loop() {
  // Blink status LED
  digitalWrite(blinkLedPin, HIGH);
  delay(2000);
  digitalWrite(blinkLedPin, LOW);
  delay(1000);

  // Emit pulse time reference
  pulseTime = micros();

  // Wait for reflection (with timeout)
  unsigned long startWait = millis();
  while (analogRead(photodiodePin) < 100) {
    if (millis() - startWait > 1000) {
      Serial.println("⚠ No reflection detected within 1s");
      return;
    }
  }

  int photodiodeValue = analogRead(photodiodePin);
  if (photodiodeValue >= 100) {
    returnTime = micros();
    roundTripTime = returnTime - pulseTime;

    // Calculate optical density (OD)
    float I0 = 1023.0;  
    float I = (float)photodiodeValue;  
    float OD = log(I0 / I);

    // Map OD to PWM duty cycle (scale 0.0–1.0 OD → 0–255)
    int dutyCycle = constrain((int)(OD * 255), 0, 255);
    ledcWrite(pwmChannel, dutyCycle);

    // Print grid sensor values
    for (int x = 0; x < gridSize; x++) {
      for (int y = 0; y < gridSize; y++) {
        Serial.print("photo diode sensor reading: ");
        Serial.print(x);
        Serial.print("_");
        Serial.print(y);
        Serial.print(": ");
        Serial.print(OD, 4);
        Serial.print("V");
        Serial.print(", PWM=");
        Serial.println(dutyCycle);
        delay(10);
      }
    }
  }

  delay(500);
}
