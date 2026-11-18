#include <Arduino.h>

void setup()
{
    Serial.begin(115200);
    Serial.println("ESP32 started!");
}

void loop()
{
    Serial.println("ESP32 is running...");
    delay(10000);
}