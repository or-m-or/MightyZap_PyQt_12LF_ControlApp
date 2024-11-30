#include <MightyZap.h>

MightyZap m_zap(&Serial1, 2);

int ID_Sel =0;

void setup() {   
  Serial.begin(9600);
  m_zap.begin(32);  
  while (! Serial);  
  Serial.print("Input ID : ");  
}

void loop() {    
  m_zap.ledOn(1,RED);
  m_zap.ledOn(2,GREEN);
  
  if(Serial.available()) {  
    ID_Sel = Serial.parseInt();
    Serial.println(ID_Sel);
    Serial.print("Input_ID [0~2] : ");
    m_zap.ServoID(0,ID_Sel);
    m_zap.ServoID(1,ID_Sel);
    m_zap.ServoID(2,ID_Sel);
  }
}