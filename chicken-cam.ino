#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2 
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);

// inside
const uint8_t insideId[8] = {0x28, 0xFF, 0x69, 0xD6, 0x63, 0x15, 0x02, 0x4C};
// outside
const uint8_t outsideId[8] = {0x28, 0xFF, 0x3F, 0xBF, 0x14, 0x14, 0x00, 0xAB};

// normally closed
bool on = true;

const float targetTemperature = 85.0;

void setup(void) 
{ 
 Serial.begin(9600);
 pinMode(4, OUTPUT);
 sensors.begin(); 
} 
void loop(void) 
{ 
 sensors.requestTemperatures();
 float inside = sensors.getTempF(insideId); 
 float outside = sensors.getTempF(outsideId);
 if ((inside > targetTemperature + 2.0) && on) {
  digitalWrite(4, HIGH);
  on = false;
 } else if ((inside < targetTemperature - 2.0) && !on) {
  digitalWrite(4, LOW);
  on = true;
 }
 Serial.print(inside);
 Serial.print(',');
 Serial.print(outside);
 Serial.print(',');
 Serial.println(on);
 delay(1000); 
}
