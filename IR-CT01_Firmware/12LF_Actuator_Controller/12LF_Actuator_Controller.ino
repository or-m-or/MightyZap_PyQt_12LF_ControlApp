#include <MightyZap.h>
#define RS485_PIN 2
#define SERVO_ID_1 1
#define SERVO_ID_2 2

MightyZap m_zap(&Serial1, RS485_PIN); // RS485 통신을 위한 MightyZap 객체 생성 (통신설정)

/* 초기 실행 (첫 전원공급 시, 리셋 버튼 누를 시 실행) */
void setup() {
  Serial.begin(9600); // 시리얼 모니터 초기화
  m_zap.begin(32);    // MightyZap 통신 속도 초기화 
  // (128: 9600 baudrate, 64: 19200 baudrate, 32: 57600 baudrate, 16: 115200 baudrate)

  // 액추에이터 위치 0 지점으로 초기화
  m_zap.GoalPosition(SERVO_ID_1, 0); 
  m_zap.GoalPosition(SERVO_ID_2, 0);
}

void loop() {
  // 시리얼 데이터 수신 대기, handleCommand()으로 명령어 전달
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
  }
  
  
  int param = paramStr.toInt();
  if (cmd == "SET_POSITION") {
    m_zap.GoalPosition(id, param);
    Serial.println("Position set to: " + String(param));
  } else if (cmd == "SET_SPEEDLIMIT") {
    m_zap.SpeedLimit(id, param);
  } else if (cmd == "SET_SPEED") {
    m_zap.GoalSpeed(id, param); // 빈번한 변경 시 사용
  } else if (cmd == "SET_CURRENTLIMIT") {
    m_zap.CurrentLimit(id, param);
  } else if (cmd == "SET_CURRENT") {
    m_zap.GoalCurrent(id, param); // 빈번한 변경 시 사용
  } else if (cmd == "SET_SHORTLIMIT") {
    m_zap.ShortStrokeLimit(id, param);
  } else if (cmd == "SET_LONGLIMIT") {
    m_zap.LongStrokeLimit(id, param);
  } else if (cmd == "SET_ACCEL") {
    m_zap.Acceleration(id, param);
  } else if (cmd == "SET_DECEL") {
    m_zap.Deceleration(id, param);
  } else if (cmd == "SET_FORCE") {
    m_zap.forceEnable(id, param);
  }
  
}



