from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
import time


# QThread를 상속받아 작업 스레드를 구현
class WorkerThread(QThread):
    # 작업 상태를 업데이트하기 위한 시그널 정의
    update_status = pyqtSignal(str)

    def __init__(self, worker_name, total_tasks):
        super().__init__()
        self.worker_name = worker_name  # 작업자 이름
        self.total_tasks = total_tasks  # 총 작업 개수
        self.completed_tasks = 0        # 완료된 작업 개수 (초기값: 0)
        self.running = False            # 스레드 실행 상태 관리 (초기값: False)

    def run(self):
        # 스레드 실행 시 호출되는 메서드
        self.running = True  # 스레드가 실행 중임을 표시
        while self.running and self.completed_tasks < self.total_tasks:
            # 작업 중 상태로, 완료된 작업 수를 1씩 증가시키고 상태 업데이트
            self.completed_tasks += 1
            self.update_status.emit(f"{self.worker_name} is working... ({self.completed_tasks}/{self.total_tasks})")
            time.sleep(1)  # 작업을 1초간 대기하며 시뮬레이션
        if self.completed_tasks >= self.total_tasks:
            # 작업 완료 시 상태 표시
            self.update_status.emit(f"{self.worker_name} completed all tasks.")
        else:
            # 작업이 중지된 경우 상태 표시
            self.update_status.emit(f"{self.worker_name} stopped.")  

    def stop(self):
        # 스레드 종료를 위한 메서드
        self.running = False  # running 상태를 False로 설정하여 while 루프 종료
        self.update_status.emit(f"{self.worker_name} stopped.")  # 상태 업데이트 전송

    def reset(self):
        """ 작업 기록을 초기화하고 상태를 리셋 """
        self.completed_tasks = 0  # 완료된 작업 개수를 0으로 초기화
        self.running = False      # 스레드 실행 상태를 False로 초기화


# 메인 GUI 클래스 정의
class ActuatorControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()  # UI 초기화 메서드 호출

    def init_ui(self):
        # 레이아웃 설정
        self.layout = QVBoxLayout()

        # 첫 번째 작업자 관련 위젯
        self.worker1_label = QLabel("Worker 1: Idle")  # 작업자 1의 상태 라벨 초기화 (Idle 상태)
        self.worker1_start_btn = QPushButton("Start Worker 1")  # 시작 버튼
        self.worker1_stop_btn = QPushButton("Stop Worker 1")   # 중지 버튼
        self.worker1_reset_btn = QPushButton("Reset Worker 1")  # 리셋 버튼
        self.worker1_tasks_input = QLineEdit()  # 총 작업 개수를 입력받을 QLineEdit
        self.worker1_tasks_input.setPlaceholderText("Enter total tasks for Worker 1")  # 플레이스홀더 텍스트

        # 두 번째 작업자 관련 위젯
        self.worker2_label = QLabel("Worker 2: Idle")  # 작업자 2의 상태 라벨 초기화 (Idle 상태)
        self.worker2_start_btn = QPushButton("Start Worker 2")  # 시작 버튼
        self.worker2_stop_btn = QPushButton("Stop Worker 2")   # 중지 버튼
        self.worker2_reset_btn = QPushButton("Reset Worker 2")  # 리셋 버튼
        self.worker2_tasks_input = QLineEdit()  # 총 작업 개수를 입력받을 QLineEdit
        self.worker2_tasks_input.setPlaceholderText("Enter total tasks for Worker 2")  # 플레이스홀더 텍스트

        # 레이아웃에 위젯 추가
        self.layout.addWidget(self.worker1_label)
        self.layout.addWidget(self.worker1_tasks_input)  # 작업 개수 입력 필드 추가
        self.layout.addWidget(self.worker1_start_btn)
        self.layout.addWidget(self.worker1_stop_btn)
        self.layout.addWidget(self.worker1_reset_btn)
        self.layout.addWidget(self.worker2_label)
        self.layout.addWidget(self.worker2_tasks_input)  # 작업 개수 입력 필드 추가
        self.layout.addWidget(self.worker2_start_btn)
        self.layout.addWidget(self.worker2_stop_btn)
        self.layout.addWidget(self.worker2_reset_btn)

        # 레이아웃을 메인 윈도우에 설정
        self.setLayout(self.layout)

        # 두 개의 작업자 스레드 생성 (기본적으로 작업 개수 100개로 설정)
        self.worker1 = WorkerThread("Worker 1", total_tasks=100)
        self.worker2 = WorkerThread("Worker 2", total_tasks=100)

        # 스레드의 시그널을 상태 업데이트 메서드와 연결
        self.worker1.update_status.connect(self.update_worker1_status)
        self.worker2.update_status.connect(self.update_worker2_status)

        # 버튼 클릭 이벤트와 메서드 연결
        self.worker1_start_btn.clicked.connect(self.start_worker1)
        self.worker1_stop_btn.clicked.connect(self.stop_worker1)
        self.worker1_reset_btn.clicked.connect(self.reset_worker1)  # 리셋 버튼 연결
        self.worker2_start_btn.clicked.connect(self.start_worker2)
        self.worker2_stop_btn.clicked.connect(self.stop_worker2)
        self.worker2_reset_btn.clicked.connect(self.reset_worker2)  # 리셋 버튼 연결

    # Worker 1 스레드 시작
    def start_worker1(self):
        try:
            # 입력된 작업 개수를 가져오고, 정수로 변환
            total_tasks = int(self.worker1_tasks_input.text())
            if total_tasks <= 0:
                raise ValueError("Total tasks must be a positive integer.")
            if not self.worker1.isRunning():  # 스레드가 실행 중이 아닐 때만 시작
                self.worker1.total_tasks = total_tasks  # 총 작업 개수 업데이트
                self.worker1.start()  # 기존 스레드 계속 사용
        except ValueError as e:
            self.worker1_label.setText(f"Error: {str(e)}")

    # Worker 1 스레드 중지
    def stop_worker1(self):
        self.worker1.stop()

    # Worker 1 리셋
    def reset_worker1(self):
        self.worker1.reset()  # 작업 기록 초기화
        self.worker1_label.setText("Worker 1: Idle")  # 라벨 텍스트 초기화
        print("Worker 1 reset.")  # 터미널에 출력

    # Worker 2 스레드 시작
    def start_worker2(self):
        try:
            # 입력된 작업 개수를 가져오고, 정수로 변환
            total_tasks = int(self.worker2_tasks_input.text())
            if total_tasks <= 0:
                raise ValueError("Total tasks must be a positive integer.")
            if not self.worker2.isRunning():  # 스레드가 실행 중이 아닐 때만 시작
                self.worker2.total_tasks = total_tasks  # 총 작업 개수 업데이트
                self.worker2.start()  # 기존 스레드 계속 사용
        except ValueError as e:
            self.worker2_label.setText(f"Error: {str(e)}")

    # Worker 2 스레드 중지
    def stop_worker2(self):
        self.worker2.stop()

    # Worker 2 리셋
    def reset_worker2(self):
        self.worker2.reset()  # 작업 기록 초기화
        self.worker2_label.setText("Worker 2: Idle")  # 라벨 텍스트 초기화
        print("Worker 2 reset.")  # 터미널에 출력

    # Worker 1의 상태를 업데이트
    def update_worker1_status(self, status):
        self.worker1_label.setText(f"Worker 1: {status}")  # Worker 1의 라벨 텍스트를 상태로 업데이트

    # Worker 2의 상태를 업데이트
    def update_worker2_status(self, status):
        self.worker2_label.setText(f"Worker 2: {status}")  # Worker 2의 라벨 텍스트를 상태로 업데이트


if __name__ == "__main__":
    app = QApplication([])  # PyQt 애플리케이션 인스턴스 생성
    window = ActuatorControlApp()  # 애플리케이션 윈도우 생성
    window.show()  # 윈도우 표시
    app.exec_()  # 애플리케이션 실행
