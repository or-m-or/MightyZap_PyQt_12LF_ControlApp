#include <MightyZap.h>

// MightyZap 객체 생성 (Serial1 사용)
MightyZap m_zap(&Serial1, 2);

// 최대 서보 ID 설정 (변경 가능)
const int MAX_SERVO_ID = 10;

void setup() {   
  Serial.begin(9600);       // PC와 통신을 위한 시리얼 초기화
  m_zap.begin(32);          // MightyZap 초기화, 32는 통신 속도
  while (!Serial);          // Serial 포트가 준비될 때까지 대기

  Serial.println("=== 서보 액츄에이터 ID 출력 ===");
  Serial.println("d를 입력하여 연결된 서보 ID를 출력하세요.");
}

void loop() {
  // PC로부터 입력 확인
  if (Serial.available()) {
    char input = Serial.read();

    // d를 입력하면 서보 ID 출력
    if (input == 'd') {
      Serial.println("연결된 서보 ID 검색 중...");
      
      // 0부터 MAX_SERVO_ID까지 확인
      for (int id = 0; id <= MAX_SERVO_ID; id++) {
        if (m_zap.ping(id)) { // 서보 모터가 응답하면
          Serial.print("응답 ID: ");
          Serial.println(id);
        }
      }

      Serial.println("검색 완료.");
    }
  }
}
