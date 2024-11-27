import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox


class PositionUpdater(QThread):
    position_updated = pyqtSignal(int)  # 위치 업데이트 시그널 (int: 현재 위치)

    def __init__(self, actuators):
        super().__init__()
        self.actuators = actuators
        self.target_port = None
        self.running = False  # 시작 시 실행되지 않음
        print("[PositionUpdater] PositionUpdater 초기화 완료")

    def set_target_port(self, port):
        """ 업데이트할 대상 포트 설정 """
        self.target_port = port
        print(f"[PositionUpdater] 대상 포트 설정: {port}" if port else "[PositionUpdater] 대상 포트 해제")

    def run(self):
        """ 실시간으로 위치를 폴링하여 업데이트 """
        print("[PositionUpdater] PositionUpdater 쓰레드 시작")
        while self.running:
            if self.target_port:
                print(f"[PositionUpdater] 대상 포트 폴링: {self.target_port}")
                actuator = next((act for act in self.actuators if act.port == self.target_port), None)
                if actuator and actuator.serial_obj and actuator.serial_obj.is_open:
                    print(f"[PositionUpdater] 포트 {self.target_port}에 연결된 액추에이터 상태 확인 중")
                    # start_time = time.time() # 응답시간 측정
                    response = actuator.send_command(f"GET_POSITION {actuator.servo_id}", expect_response=True)
                    if response:
                        try:
                            current_position = int(response)
                            print(f"[PositionUpdater] 현재 위치: {current_position}")
                            self.position_updated.emit(current_position)  # 위치 업데이트 시그널 방출
                        except ValueError:
                            print("[PositionUpdater] 위치 값을 정수로 변환하는 데 실패")
                            pass
                    # else:
                    #     # 응답이 1초를 초과한 경우
                    #     if time.time() - start_time > 1:
                    #         print(f"[PositionUpdater] 응답 없음: 포트={self.target_port}, Servo ID={actuator.servo_id}")
                    #         self._show_error_message(actuator.port, actuator.servo_id)
                    #         self.set_target_port(None)  # 대상 포트 해제
                    #         continue
                else:
                    print(f"[PositionUpdater] 대상 포트 {self.target_port}에 해당하는 액추에이터가 없음")
            else:
                print("[PositionUpdater] 대상 포트가 설정되지 않음")
            time.sleep(0.1)  # 100ms 대기 (폴링 주기)
        print("[PositionUpdater] PositionUpdater 쓰레드 종료")

    # def _show_error_message(self, port, servo_id):
    #     """ 경고 메시지 표시 """
    #     error_message = (f"Failed to communicate with the actuator.\n"
    #                      f"Port: {port}\n"
    #                      f"Servo ID: {servo_id}\n"
    #                      "Please check the Servo ID and reconfigure.")
    #     QMessageBox.critical(None, "Communication Error", error_message)
    
    def stop(self):
        """ 쓰레드 중지 """
        print("[PositionUpdater] PositionUpdater 쓰레드 중지 요청")
        self.running = False
        self.quit()
        self.wait()
        print("[PositionUpdater] PositionUpdater 쓰레드 중지 완료")

    def start(self):
        """쓰레드 시작"""
        if not self.isRunning():
            print("[PositionUpdater] PositionUpdater 쓰레드 시작 요청")
            self.running = True  # 실행 가능 상태로 설정
            super().start()  # QThread의 start 호출