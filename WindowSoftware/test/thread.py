import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Worker(QThread):
    def __init__(self, name):
        super().__init__()
        self.running = True
        self.name = name  # 각 스레드에 이름을 부여해 구별

    def run(self):
        while self.running:
            print(f"{self.name} 안녕하세요")  # 각 스레드별로 이름을 출력
            self.sleep(1)  # 1초마다 출력

    def resume(self):
        self.running = True

    def pause(self):
        self.running = False


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 두 개의 독립적인 Worker 스레드를 생성
        self.worker1 = Worker("스레드 1")
        self.worker2 = Worker("스레드 2")
        
        self.worker1.start()
        self.worker2.start()

        # 각 스레드를 제어할 버튼을 추가
        btn1_resume = QPushButton("스레드 1 Resume", self)
        btn1_resume.move(10, 10)
        btn1_pause = QPushButton("스레드 1 Pause", self)
        btn1_pause.move(10, 50)

        btn2_resume = QPushButton("스레드 2 Resume", self)
        btn2_resume.move(10, 90)
        btn2_pause = QPushButton("스레드 2 Pause", self)
        btn2_pause.move(10, 130)

        # 버튼 클릭 시 스레드를 제어하는 슬롯 연결
        btn1_resume.clicked.connect(self.resume_worker1)
        btn1_pause.clicked.connect(self.pause_worker1)

        btn2_resume.clicked.connect(self.resume_worker2)
        btn2_pause.clicked.connect(self.pause_worker2)

    def resume_worker1(self):
        self.worker1.resume()
        self.worker1.start()  # 스레드 1을 다시 시작

    def pause_worker1(self):
        self.worker1.pause()  # 스레드 1을 일시 정지

    def resume_worker2(self):
        self.worker2.resume()
        self.worker2.start()  # 스레드 2를 다시 시작

    def pause_worker2(self):
        self.worker2.pause()  # 스레드 2를 일시 정지


app = QApplication(sys.argv)
mywindow = MyWindow()
mywindow.show()
app.exec_()
