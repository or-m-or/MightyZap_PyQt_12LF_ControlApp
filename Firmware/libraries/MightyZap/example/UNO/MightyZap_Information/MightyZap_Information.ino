#include <MightyZap.h>

#define ID_NUM 0

MightyZap m_zap(&Serial1, 2);


void setup() {
  Serial.begin(9600);    
  m_zap.begin(32);  
  while (! Serial);    
}

void loop() {     
  if(Serial.available())  {    
    char ch = Serial.read();
    if(ch=='d')    {
      Serial.print("Model Number        : ");  Serial.println((unsigned int)m_zap.getModelNumber(ID_NUM));
      Serial.print("Firmware Version    : ");  Serial.println(m_zap.Version(ID_NUM)*0.1);           
      Serial.print("Present Temperature : ");  Serial.println(m_zap.presentTemperature(ID_NUM));
    }
  }
}