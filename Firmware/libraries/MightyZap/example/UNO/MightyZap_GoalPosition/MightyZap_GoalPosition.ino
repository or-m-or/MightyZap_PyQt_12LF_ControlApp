#include <MightyZap.h>
#define ID_NUM 0

MightyZap m_zap(&Serial1, 2);

void setup() {
  // Initialize the MightyZap bus:
  // Baudrate -> 128: 9600, 32: 57600, 16: 115200 
  m_zap.begin(32);  
}

void loop() {
  m_zap.GoalPosition(ID_NUM, 0); //ID 0 MightZap moves to position 0
  delay(1000);
  m_zap.GoalPosition(ID_NUM, 4095);//ID 0 MightZap moves to position 4095
  delay(1000);
}



