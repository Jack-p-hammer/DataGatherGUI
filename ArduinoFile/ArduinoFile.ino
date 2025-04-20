unsigned long startTime;
int sensor1Pin = A0;
int sensor2Pin = A1;

void setup() {
  Serial.begin(9600); // match baud from GUI dropdown
  while (!Serial); // wait for serial port to connect
  startTime = millis();
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    if (command == 'i') {
      // Send header sample format (used for GUI setup)
      Serial.println("Time:0,Sensor1:0.0,Sensor2:0.0");

    } else if (command == 'g') {
      // Read sensors
      unsigned long currentTime = millis() - startTime;
      int sensor1 = analogRead(sensor1Pin);
      int sensor2 = analogRead(sensor2Pin);

      // Convert to voltage for example (assuming 5V and 10-bit ADC)
      float sensor1Val = sensor1 * (5.0 / 1023.0);
      float sensor2Val = sensor2 * (5.0 / 1023.0);

      // Print in format expected by Python: key:value,...
      Serial.print("Time:");
      Serial.print(currentTime);
      Serial.print(",Sensor1:");
      Serial.print(sensor1Val, 2);
      Serial.print(",Sensor2:");
      Serial.println(sensor2Val, 2);
    }
  }
}
