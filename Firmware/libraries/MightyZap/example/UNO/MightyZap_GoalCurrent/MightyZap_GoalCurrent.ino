#include <MightyZap.h>
#define ID_NUM 0

MightyZap m_zap(&Serial1, 2);

int Current, Display=1;

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
    Serial.print("New Current[0~1023] : ");
    Display=0;
  }  
  if(Serial.available()) {
    Current = Serial.parseInt();
    m_zap.GoalCurrent(ID_NUM,Current);
    Serial.println(m_zap.GoalCurrent(ID_NUM));
    delay(500);
    Display=1;
  }
}
