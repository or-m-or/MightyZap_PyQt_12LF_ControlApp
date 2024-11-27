"""
Test 1: CT01보드 - 윈도우 애플리케이션 간 시리얼 통신 테스트
"""
import serial
import time

py_serial = serial.Serial(
    # Window
    port='COM3',
    # 보드 레이트 (통신 속도)
    baudrate=9600,
    timeout=1,  # 읽기 대기 시간 설정 (1초)
)

while True:
    commend = input('아두이노에게 내릴 명령:') + '\n'
    py_serial.write(commend.encode())  # 인코딩: 자연어 -> 시리얼 통신 데이터
    time.sleep(0.5)  # 아두이노 응답 대기 시간
    
    print('-------------------')
    if py_serial.in_waiting > 0:  # 읽을 데이터가 있는지 확인
        # 들어온 값이 있으면 값을 한 줄 읽음 (BYTE 단위로 받은 상태)
        response = py_serial.readline()  # BYTE 단위로 받은 응답
        try:
            # 디코딩 후, 출력 (가장 끝의 \n을 없애주기 위해 슬라이싱 사용)
            print(response[:len(response) - 1].decode())
        except UnicodeDecodeError:
            print("[에러] 디코딩 실패: 수신된 데이터가 유효하지 않습니다.")
    else:
        print("[경고] 아두이노 응답 없음")
    print('-------------------')
