import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from config import setup_logger

_logger = setup_logger(name='Position', level='DEBUG')


class PositionUpdater(QThread):
    position_updated = pyqtSignal(int)  # 위치 업데이트 시그널 (int: 현재 위치)

    def __init__(self, actuators):
        super().__init__()
        self.actuators = actuators
        self.target_port = None
        self.running = False  # 시작 시 실행되지 않음
        
    def set_target_port(self, port):
        """ 업데이트할 대상 포트 설정 """
        self.target_port = port
        _logger.info(f'position 실시간 업데이트할 타겟 보드(포트) : {port}')

    def run(self):
        """ 실시간으로 위치를 폴링하여 업데이트 """
        _logger.info('Position 쓰래드 시작')
        while self.running:
            if self.target_port:
                actuator = next((act for act in self.actuators if act.port == self.target_port), None)
                if actuator and actuator.serial_obj and actuator.serial_obj.is_open:
                    try:
                        response = actuator.send_command(f"GET_POSITION {actuator.servo_id}", expect_response=True)
                        if response:
                            # _logger.info(f'현재 위치: {int(response)}')
                            self.position_updated.emit(int(response))  # 위치 업데이트 시그널 방출
                    except Exception as e:
                        _logger.error(f"위치 업데이트 실패: {e}")
                else:
                    _logger.error(f'타겟 포트 {self.target_port}에 해당하는 액추에이터가 없음')
            else:
                _logger.error('타겟 포트가 설정되지 않음')
            QThread.msleep(20)
            # time.sleep(0.1)  # 100ms 대기 (폴링 주기)
        print("[PositionUpdater] PositionUpdater 쓰레드 종료")
    
    def stop(self):
        """ 쓰레드 중지 """
        self.running = False
        self.quit()
        self.wait()
        _logger.info('Position 쓰래드 중지 완료')

    def start(self):
        """쓰레드 시작"""
        if not self.isRunning():
            _logger.info('Position 쓰래드 시작')
            self.running = True  # 실행 가능 상태로 설정
            super().start()      # QThread의 start 호출