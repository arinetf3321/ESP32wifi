#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
 
// ================== WIFI SETTINGS ==================
const char* ssid = "VIP Authur 2"; 
const char* password = "0774560547";

// Define static IP configuration (adjust to your Wi-Fi subnet)
//IPAddress local_IP(192, 168, 17, 150);  // <-- pick unused IP in 192.168.0.x
//IPAddress gateway(192, 168, 16, 1);      // <-- your Wi-Fi router
//IPAddress subnet(255, 255, 254, 0);  // <-- typical subnet mask
//IPAddress primaryDNS(8, 8, 8, 8);    // optional
//IPAddress secondaryDNS(8, 8, 4, 4);  // optional

// Initialize servers
WiFiServer tcpServer(5000);      // For Python client
WebServer httpServer(80);        // For the browser

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 4);  // Adjust address if needed

// Pin definitions
const int blinkLedPin = 14;     // LED pin for blinking
const int nirLedPin = 23;       // NIR LED (PWM controlled)
const int photodiodePin = 34;   // Analog pin for photodiode input

// PWM setup
const int pwmChannel = 0;       // PWM channel
const int pwmFreq = 5000;       // 5 kHz frequency
const int pwmResolution = 8;    // 8-bit resolution (0–255 duty)

float OD = 0.0;
int dutyCycle = 0;

// Timing variables
unsigned long pulseTime;
unsigned long returnTime;
unsigned long roundTripTime;

// TCP Client
WiFiClient tcpClient; // global
const char* FLASK_IP = "192.168.17.133"; // Replace with your Flask PC IP
const int FLASK_TCP_PORT = 5001;

// Number of sensor positions (10x10 grid)
const int gridSize = 10;
int sensorGrid[gridSize][gridSize];  // A 2D array to represent sensor positions

void handleSensorData() {
  String json = "{";
  json += "\"od\":" + String(OD, 4) + ",";
  json += "\"pwm\":" + String(dutyCycle) + ",";
  json += "\"raw\":\"" + String(analogRead(photodiodePin)) + "\"";
  json += "}";
  httpServer.send(200, "application/json", json);
}

// Send data to Flask TCP server
void sendToFlask() {
  if (!tcpClient.connected()) {
    if (!tcpClient.connect(FLASK_IP, FLASK_TCP_PORT)) {
      Serial.println("Failed to connect to Flask TCP server");
      return;
    } else {
      Serial.println("Connected to Flask TCP server!");
    }
  }

  // Send OD, PWM, and raw photodiode value
  tcpClient.printf("OD:%.4f,PWM:%d\n,RAW:%d\n", OD, dutyCycle, analogRead(photodiodePin));
  //tcpClient.printf("%d\n", analogRead(photodiodePin));
}

void setup() {
  pinMode(blinkLedPin, OUTPUT);
  pinMode(photodiodePin, INPUT);

  // Setup PWM for NIR LED
  ledcSetup(pwmChannel, pwmFreq, pwmResolution);
  ledcAttachPin(nirLedPin, pwmChannel);

  Serial.begin(115200);
  Serial.println("System started...");

  WiFi.begin(ssid, password); 
  Serial.print("Connecting to Wi-Fi");
  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 30000) { 
    Serial.print(".");
    delay(500);   
  }
  if (WiFi.status() != WL_CONNECTED) {
  Serial.println("Failed to connect!");
  } else {
  Serial.println("\nConnected!"); 
  Serial.print("Connected to SSID: "); 
  Serial.println(WiFi.SSID());
  Serial.print("ESP32 IP Address: "); 
  Serial.println(WiFi.localIP()); 
  tcpServer.begin();  // Start TCP server for Python client
  //httpServer.on("/", handleRoot);  // HTTP server root
  httpServer.on("/sensor-data", handleSensorData);  // JSON endpoint
  httpServer.begin();  // Start WebServer for browser
  Serial.println("Server started on port 5000");
  Serial.println("HTTP server started on port 80");
  }

  // Initialize I2C on custom pins
  Wire.begin(25, 26);

  // Initialize LCD
  lcd.init();
  lcd.backlight();
}


void loop() {
  // Blink status LED
  digitalWrite(blinkLedPin, HIGH);
  delay(2000);
  digitalWrite(blinkLedPin, LOW);
  delay(20);

  // Emit pulse time reference
  pulseTime = micros();

  // Wait for reflection (with timeout)
  unsigned long startWait = millis();
  while (analogRead(photodiodePin) < 100) {
    if (millis() - startWait > 1000) {
      Serial.println("⚠ No reflection detected within 1s");
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("No reflection");
      lcd.setCursor(0, 1);
      lcd.print("within 1s ⚠");
	  
	  // Mirror to Serial Monitor 
	  Serial.printf("LCD: No reflection within 1s ⚠\n");
	  
      delay(1500);
      return;
    }
  }

  int photodiodeValue = analogRead(photodiodePin);
  if (photodiodeValue >= 100) {
    returnTime = micros();
    roundTripTime = returnTime - pulseTime;

    // Calculate optical density (OD,1023.0)
    float I0 = 4095.0;  
    float I = (float)photodiodeValue;  
    OD = log(I0 / I);

    // Map OD to PWM duty cycle (scale 0.0–1.0 OD → 0–255)
    dutyCycle = constrain((int)(OD * 255), 0, 255);
    ledcWrite(pwmChannel, dutyCycle);
	
	// Convert to percentage
    float dutyPercent = (dutyCycle / 255.0) * 100.0;
	//float dutyPercent = (OD / maxOD) * 100.0;
    if (dutyPercent > 100.0) dutyPercent = 100.0;
    
    // Handle HTTP server
    httpServer.handleClient();

    delay(50); // small non-blocking delay	
	
    // Print grid sensor values
    for (int x = 0; x < gridSize; x++) {
      for (int y = 0; y < gridSize; y++) {
        // Serial output
        Serial.print("photo diode sensor reading: ");
        Serial.print(x);
        Serial.print("_");
        Serial.print(y);
        Serial.print(": ");
        Serial.print(OD, 4);
        Serial.print("V");
        Serial.print(", PWM=");
        Serial.println(dutyCycle);
		
		//percent
		Serial.print(dutyPercent, 1); // 1 decimal place
        Serial.println("%");

        // LCD output (scroll vertically)
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Sensor ");
        lcd.print(x);
        lcd.print("_");
        lcd.print(y);

        lcd.setCursor(0, 1);
        lcd.print("Volts:");
        lcd.print(OD, 2);
        lcd.print(" PWM:");
        lcd.print(dutyCycle);
		
		//percent
		//lcd.print(dutyPercent, 1); // 1 decimal place
		//lcd.print("%");
		lcd.print(String(dutyPercent, 1) + "%");
       
	    // Mirror to Serial Monitor 
		Serial.printf("LCD: Sensor %d_%d | Volts: %.2f | PWM: %d\n", x, y, OD, dutyCycle);
		
		// percent
		Serial.printf("%.1f%%\n", dutyPercent, 1); // 1 decimal place
		Serial.printf("%d\n", photodiodeValue);
		
		// Send to Flask
        sendToFlask();
		
		// ---- SEND DATA OVER WIFI ----
        if (tcpClient) {
          if (tcpClient.connected()) {
			tcpClient.println(String("Volts: ") + String(OD, 4) + ",PWM:" + String(dutyCycle));	
            tcpClient.println(String(photodiodeValue)); // send as a line			

          }
        }
		
        delay(500); // adjust scroll speed
      }
    }
  }
  httpServer.handleClient();  // Handle incoming HTTP requests (from browser)
  delay(500);
}
