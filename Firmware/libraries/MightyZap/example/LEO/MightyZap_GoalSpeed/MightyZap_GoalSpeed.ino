#include <MightyZap.h>
#define ID_NUM 0

MightyZap m_zap(&Serial1, 2);

int Speed, Display=1;

void setup() {
  Serial.begin(9600); 
  m_zap.begin(32);  
  while (! Serial);
}

void loop() {  
  if(Display ==1) {                  
    m_zap.GoalPosition(ID_NUM,0);
    delay(500);
    while(m_zap.Moving(ID_NUM));  
    
    m_zap.GoalPosition(ID_NUM,4095);
    delay(50);
    while(m_zap.Moving(ID_NUM));
    Serial.print("New Speed[0~1023] : ");
    Display=0;
  }  
  if(Serial.available()) {
    Speed = Serial.parseInt();
    m_zap.GoalSpeed(ID_NUM,Speed);
    Serial.println(m_zap.GoalSpeed(ID_NUM));
    delay(500);
    Display=1;
  }
}
