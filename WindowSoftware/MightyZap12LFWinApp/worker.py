from PyQt5.QtCore import QThread, pyqtSignal
from config import setup_logger

_logger = setup_logger(name="TestWorker", level='DEBUG')

class TestWorker(QThread):
    """ 테스트 실행 워커 """
    test_complete = pyqtSignal()  # 테스트 완료 시그널

    def __init__(self, actuator, position1, position2, push_counts):
        super().__init__()
        self.actuator = actuator
        self.position1 = position1
        self.position2 = position2
        self.push_counts = push_counts

    def run(self):
        self.actuator.send_command(f"SET_POSITION {self.actuator.servo_id} {self.position1}")
        self.msleep(1000)  # 1초 대기
        for _ in range(self.push_counts):
            self.actuator.send_command(f"SET_POSITION {self.actuator.servo_id} {self.position2}")
            self.msleep(300)  # 0.3초 대기
            self.actuator.send_command(f"SET_POSITION {self.actuator.servo_id} {self.position1}")
            self.msleep(500)  # 0.5초 대기
        self.actuator.send_command(f"SET_POSITION {self.actuator.servo_id} 0")
        self.msleep(1000)  # 1초 대기
        self.test_complete.emit()  # 테스트 완료 시그널 방출
