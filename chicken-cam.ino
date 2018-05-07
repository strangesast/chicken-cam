#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2 
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);

// inside
const uint8_t id1[8] = {0x28, 0xFF, 0x69, 0xD6, 0x63, 0x15, 0x02, 0x4C};
// outside
const uint8_t id2[8] = {0x28, 0xFF, 0x3F, 0xBF, 0x14, 0x14, 0x00, 0xAB};

void setup(void) 
{ 
 Serial.begin(9600);
 sensors.begin(); 
} 
void loop(void) 
{ 
 sensors.requestTemperatures();
 Serial.print(sensors.getTempF(id1));
 Serial.print(',');
 Serial.println(sensors.getTempF(id2));
 delay(1000); 
}
