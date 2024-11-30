#include <MightyZap.h>
#define ID_NUM 0

MightyZap m_zap(&Serial1, 2);

void setup() {
  m_zap.begin(32);  
}

void loop() {    
  m_zap.ledOn(ID_NUM,RED);
  delay(1000);  
  m_zap.ledOn(ID_NUM,GREEN);  
  delay(1000);
}