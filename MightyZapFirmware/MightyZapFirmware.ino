#include <MightyZap.h>

#define RS485_PIN 2
#define SERVO_ID 0
#define SWITCH_PIN 10
#define TEST_CMD "TEST"

MightyZap m_zap(&Serial1, RS485_PIN);
bool test_triggered = false; // 테스트 트리거 상태 플래그


void setup() {
  Serial.begin(9600);
  pinMode(SWITCH_PIN, INPUT_PULLUP);
  m_zap.begin(32);    // MightyZap-액추에이터간 통신 속도 (128: 9600 baud, 64: 19200 baud, 32: 57600 baud, 16: 115200 baud)
  m_zap.GoalPosition(SERVO_ID, 0); // 액추에이터 위치 0으로 초기화
  while (!Serial);
}


void loop() {
  // 스위치 누르면 테스트 명령 전송
  if (digitalRead(SWITCH_PIN) == LOW && !test_triggered) {
    test_triggered = true;
    Serial.println(TEST_CMD); // 시리얼 테스트 명령어 전송
    delay(100);
  }

  // 스위치 안누르면 트리거 상태 초기화
  if (digitalRead(SWITCH_PIN) == HIGH) {
    test_triggered = false;
  }

  // 시리얼 명령 수신 대기
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();       
    parseCommand(command);  // 명령어 처리 함수 호출
  }
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////

/* 명령어 파싱 및 처리 함수 */
void parseCommand(String command) {

  // 공백 기준으로 명령어와 파라미터 분리
  int spacePos = command.indexOf(' ');  // 첫 번째 공백의 위치 찾기
  String cmd = command.substring(0, spacePos);  // 명령어 추출
  String params = command.substring(spacePos + 1);  // 파라미터들 추출
  
  // 파라미터들을 공백 기준으로 분리
  int firstSpace = params.indexOf(' ');
  String servoID = params.substring(0, firstSpace == -1 ? params.length() : firstSpace); // 첫 번째 파라미터
  String paramStr = "";
  if (firstSpace != -1) {
    paramStr = params.substring(firstSpace + 1); // 두 번째 파라미터 (있다면)
  }

  // 명령어에 따라 적절한 라이브러리 함수 호출
  int id = servoID.toInt();

  if (cmd == "GET_TEMP") {
    float temperature = m_zap.presentTemperature(id);
    Serial.println(temperature);
  } else if (cmd == "GET_POSITION") {
    int location = m_zap.presentPosition(id);
    Serial.println(location);
  } else if (cmd == "GET_MOVING") {
    int state = m_zap.Moving(id);
    Serial.println(state);
  } else if (cmd == "GET_MODEL") {
    Serial.println(id);
    Serial.println(m_zap.getModelNumber(id));
  } else if (cmd == "GET_INFO") {
    // Speed Limit 속도 제한값
    Serial.print("SPL ");
    Serial.print(m_zap.readint(id, 0x15));
    Serial.print(",");

    // Current Limit 전류 제한값
    Serial.print("CRL ");
    Serial.print(m_zap.readint(id, 0x34));
    Serial.print(",");

    // Short Stroke Limit 최소 위치 한계값
    Serial.print("SSL ");
    Serial.print(m_zap.readint(id, 0x06)); 
    Serial.print(",");

    // Long Stroke Limit 최대 위치 한계값
    Serial.print("LSL ");
    Serial.print(m_zap.readint(id, 0x08));
    Serial.print(",");

    // Acceleration Ratio 가속률
    Serial.print("ACC ");
    Serial.print(m_zap.readByte(id, 0x21));
    Serial.print(",");

    // Deceleration Ratio 감속률
    Serial.print("DEC ");
    Serial.print(m_zap.readByte(id, 0x22));
    Serial.print(",");
  }
  
  
  int param = paramStr.toInt();
  if (cmd == "SET_POSITION") {
    m_zap.GoalPosition(id, param);
    // Serial.println(param);  
  } else if (cmd == "SET_SPEEDLIMIT") {
    m_zap.SpeedLimit(id, param);
    // Serial.println(param);
  } else if (cmd == "SET_SPEED") {
    m_zap.GoalSpeed(id, param); // 빈번한 변경 시 사용
    // Serial.println(param);
  } else if (cmd == "SET_CURRENTLIMIT") {
    m_zap.CurrentLimit(id, param);
    // Serial.println(param);
  } else if (cmd == "SET_CURRENT") {
    m_zap.GoalCurrent(id, param); // 빈번한 변경 시 사용
    // Serial.println(param);
  } else if (cmd == "SET_SHORTLIMIT") {
    m_zap.ShortStrokeLimit(id, param);
    // Serial.println(param);
  } else if (cmd == "SET_LONGLIMIT") {
    m_zap.LongStrokeLimit(id, param);
    // Serial.println(param);
  } else if (cmd == "SET_ACCEL") {
    m_zap.Acceleration(id, param);
    // Serial.println(param);
  } else if (cmd == "SET_DECEL") {
    m_zap.Deceleration(id, param);
    // Serial.println(param);
  } else if (cmd == "SET_FORCE") {
    m_zap.forceEnable(id, param);
    // Serial.println(param);
  }
}



