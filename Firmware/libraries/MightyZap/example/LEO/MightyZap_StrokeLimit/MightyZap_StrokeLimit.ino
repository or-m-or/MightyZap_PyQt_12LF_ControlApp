#include <MightyZap.h>
#define ID_NUM 0

MightyZap m_zap(&Serial1, 2);

void setup() { 
  m_zap.begin(32);  
}

void loop() {
  m_zap.LongStrokeLimit(ID_NUM,3095);  
  m_zap.GoalPosition(ID_NUM,4095);      
  delay(5000);
   
  m_zap.ShortStrokeLimit(ID_NUM,100);  
  m_zap.GoalPosition(ID_NUM,0);         
  delay(5000);   
}