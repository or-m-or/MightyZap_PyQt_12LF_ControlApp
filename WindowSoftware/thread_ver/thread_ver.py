import sys
import serial
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication, 
    QDialog, 
    QVBoxLayout, 
    QPushButton, 
    QLabel, 
    QComboBox, 
    QLineEdit, 
    QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal
import time
import glob


class WorkerThread(QThread):
    update_status = pyqtSignal(str)  # 작업 상태를 업데이트하기 위한 시그널 정의 : 완료된 테스트 수

    def __init__(self, worker_id, test_counts_total, position1, position2, serial_obj):
        super().__init__()
        self.worker_id = worker_id                 # 작업자 ID
        self.test_counts_total = test_counts_total # 전체 작업 개수
        self.comp_test_counts = 0                  # 완료된 작업 개수
        self.position1 = position1                 # 포지션 1 위치
        self.position2 = position2                 # 포지션 2 위치
        self.serial_obj = serial_obj # 시리얼 연결 객체
        self.running = False                       # 스레드 실행 상태 관리 (초기값: False)

    def run(self):
        """ 스레드 실행 시 호출되는 메서드 """
        self.running = True # 스레드가 실행 중임을 표시
        while self.running and self.comp_test_counts < self.test_counts_total:
            self.execute_template_action() # 작업 1회 실행
            self.comp_test_counts += 1     # 완료된 작업 수 1씩 증가
            self.update_status.emit(f'{self.comp_test_counts} (작업 중)') # 상태 업데이트
            time.sleep(1) # 작업을 1초간 대기하며 시뮬레이션
        if self.comp_test_counts >= self.test_counts_total:
            # 작업 완료 시 상태 표시
            self.update_status.emit(f'{self.comp_test_counts} (작업 완료)')
        else:
            # 작업이 중지된 경우 상태 표시
            self.update_status.emit(f'{self.comp_test_counts} (작업 정지)')
            
    def stop(self):
        """ 스레드 종료 """
        self.running = False # running 상태를 False로 설정하여 while 루프 종료
        self.update_status.emit(f"{self.worker_id} (작업 정지)")  # 상태 업데이트 전송

    def reset(self):
        """ 작업 기록 초기화, 상태 리셋 """
        self.comp_test_counts = 0 # 완료된 작업 개수 0으로 초기화
        self.running = False      # 스레드 실행 상태를 False로 초기화
    
    def execute_template_action(self):
        """ 작업 1회 실행을 위한 템플릿 """
        self.move_to_position(self.position1)
        self.move_to_position(self.position2)
        self.move_to_position(self.position1)

    def move_to_position(self, position):
        command = f"SET_POSITION {self.worker_id} {position}"
        print(command)
        self.post_command(command)
        time.sleep(0.5)
    
    def post_command(self, command):
        """ 보드에 시리얼 통신 명령어 전송 """
        print('---postcommanad')
        print(command)
        print(self.serial_obj) # 시리얼 객체 없음
        print('*******')
        print(self.serial_obj.is_open)
        if self.serial_obj and self.serial_obj.is_open:
            self.serial_obj.write(f"{command}\n".encode())
            time.sleep(0.5)

                    


class ActuatorControlApp(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("thread_ver.ui") # pyuic5 your_ui_file.ui -o your_ui_file.py

        self.serial_obj = None      # 시리얼 객체
        self.is_serial_open = False # 시리얼 포트 연결 상태
        self.servoid1 = 1           # 액추에이터1의 Servo ID
        self.servoid2 = 2           # 액추에이터2의 Servo ID
        self.position1 = 0          # 포지션 1 위치
        self.position2 = 0          # 포지션 2 위치
        self.total_test1_counts = 0  # 전체 테스트 횟수
        self.one_test1_counts = 0    # 테스트 1회당 액추에이터 왕복 횟수
        self.total_test2_counts = 0
        self.one_test2_counts = 0
        
        self.comp_test1_counts = 0   # 완료된 테스트 횟수
        self.comp_test2_counts = 0
        
        ######################## [Setup] ###############################
        # [Board Setting]
        self.ui.PortComboBox.addItem("")                 
        self.ui.BaudrateComboBox.addItem("9600")
        self.ui.BaudrateComboBox.addItem("19200")
        self.ui.BaudrateComboBox.addItem("57600")
        self.ui.BaudrateComboBox.addItem("115200")                     # Baudrate 선택 옵션 추가
        self.init_serial_ports()                                       # 윈도우 애플리케이션 - CT01 보드간 연결 및 Port, Baudrate 자동 탐지 
        self.ui.ConnectPushBtn.clicked.connect(self.set_board_connect) # 보드 연결 버튼
        self.ui.StatusLabel.setText("Disconnected")                    # 보드 연결 상태 라벨
        
        # [JOG Setting]
        self.ui.CurLocLabel.setText("0")                             # 설정용 액추에이터 현재 위치 라벨
        self.post_actuator_curloc()                                  # 설정용 액추에이터 현재 위치 계산 
        self.ui.FwdPushBtn.clicked.connect(self.post_actuator_fwd)   # 설정용 액추에이터 전진(증가) 버튼
        self.ui.BwdPushBtn.clicked.connect(self.post_actuator_bwd)   # 설정용 액추에이터 후진(감소) 버튼
        self.ui.HomePushBtn.clicked.connect(self.post_actuator_home) # 설정용 액추에이터 원점 이동 버튼
        self.ui.Pos1LineEdit.setText("")                             # 포지션1 위치 입력 라인 텍스트 박스
        self.ui.Pos2LineEdit.setText("")                             # 포지션2 위치 입력 라인 텍스트 박스
        
        # [Test Setting]
        self.ui.S1TotalLineEdit.setText("")                            # 전체 목표 테스트 횟수 입력 라인 텍스트 박스
        self.ui.S1CountLineEdit.setText("")                            # 1회당 목표 왕복 횟수 입력 라인 텍스트 박스
        self.ui.S2TotalLineEdit.setText("")
        self.ui.S2CountLineEdit.setText("")
            
        # [Setup]
        self.ui.SaveStatusLabel.setText("--")                       # 저장 성공 유무 표시 라벨
        self.ui.SavePushBtn.clicked.connect(self.init_setup)        # 전체 설정 저장 버튼
        self.ui.SetupResetPushBtn.clicked.connect(self.reset_setup) # 전체 설정 초기화 버튼
        self.ui.SetupExitPushBtn.clicked.connect(self.close_window) # 프로그램 종료 버튼
        
        ######################## [Run] ###############################
        self.ui.S1TotalLabel.setText(f"{self.total_test1_counts}")  # 전체 테스트 목표 횟수
        self.ui.S1CompLabel.setText(f"{self.comp_test1_counts}")    # 완료된 테스트 횟수
        self.ui.S1StartBtn.clicked.connect(self.start_worker1) # 테스트 시작 버튼
        self.ui.S1StopBtn.clicked.connect(self.stop_worker1)  # 테스트 일시 정지 버튼
        self.ui.S1ResetBtn.clicked.connect(self.reset_worker1) # 테스트 초기화 버튼
        # self.ui.S1OnBtn.clicked.connect()    # 액추에이터 1 사용
        # self.ui.S1OffBtn.clicked.connect()   # 액추에이터 1 절전모드
        
        self.ui.S2TotalLabel.setText(f"{self.total_test2_counts}")  # 전체 테스트 목표 횟수
        self.ui.S2CompLabel.setText(f"{self.comp_test2_counts}")    # 완료된 테스트 횟수
        self.ui.S2StartBtn.clicked.connect(self.start_worker2)
        self.ui.S2StopBtn.clicked.connect(self.stop_worker2)
        self.ui.S2ResetBtn.clicked.connect(self.reset_worker2)
        # self.ui.S2OnBtn.clicked.connect()
        # self.ui.S2OffBtn.clicked.connect()
        
        ######################## Worker ###############################
        # 두 개 작업자 스레드 기본값으로 생성
        self.worker1 = WorkerThread(self.servoid1, test_counts_total=10, position1=100, position2=500, serial_obj=self.serial_obj)
        self.worker2 = WorkerThread(self.servoid2, test_counts_total=10, position1=100, position2=500, serial_obj=self.serial_obj)
        
        # 스레드의 시그널을 상태 업데이트 메서드와 연결
        self.worker1.update_status.connect(self.update_worker1_status)
        self.worker2.update_status.connect(self.update_worker2_status)
        
        self.ui.RunExitPushBtn.clicked.connect(self.close_window)      # 프로그램 종료
        self.ui.show()
        
        
    ######################## [Setup] ###############################
    def init_serial_ports(self):
        """ 
        시스템에 연결된 직렬 포트를 탐지 및 유효한 포트를 반환함.
        탐지된 포트는 UI의 'Port', 'Baudrate'컴보박스에 추가됨.
        프로그래 첫 시작 시 매번 실행됨.
        """
        # 운영체제 별로 구분
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]    
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'): 
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'): 
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = [] 
        for port in ports:
            try:
                # 포트를 열어 사용 가능한지 확인
                s = serial.Serial(port)   
                s.close()
                self.ui.PortComboBox.addItem(port)
                result.append(port)   
            except (OSError, serial.SerialException) as e:  
                print(f"Error with port {port}: {e}")
            
        return result # 유효한 포트 리스트 반환

    def set_board_connect(self):
        """ Connect 버튼: 보드 연결/해제 """
        # 시리얼 연결 X 일때,
        if not self.is_serial_open:
            # 콤보박스에서 선택된 값 가져오기
            com = self.ui.PortComboBox.currentText()
            baud = self.ui.BaudrateComboBox.currentText()
            try:
                self.serial_obj = serial.Serial(com, baud, timeout=1) # 시리얼 포트 연결 시도
                self.ui.ConnectPushBtn.setText("DisConnect")          # 버튼 텍스트 DisConnect으로 변경
                self.ui.StatusLabel.setText("Connected")                # 상태 라벨 Connected로 변경
                self.is_serial_open = True                            # 연결 상태 True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not connect: {str(e)}")
        # 시리얼 이미 연결된 상태
        else:
            if self.serial_obj:
                self.serial_obj.close()                # 시리얼 객체 닫기 
            self.ui.ConnectPushBtn.setText("Connect")  # 버튼 텍스트 Connect로 변경
            self.ui.StatusLabel.setText("Disconnected")   # 상태 라벨 Disconnected로 변경
            self.is_serial_open = False                # 연결 상태 False

    def post_command(self, command, expect_response=False):
        """ 보드에 시리얼 통신 명령어 전송 """
        print('===')
        if self.serial_obj and self.serial_obj.is_open:
            print(self.serial_obj)
            print('----------')
            print(command)
            self.serial_obj.write(f"{command}\n".encode())
            time.sleep(0.5)
            if expect_response:
                response = self.serial_obj.readline()
                response[:len(response)-1].decode().strip()
                return response
        return None
    
    def get_position(self, servoid):
        """ 지정된 액추에이터 서보 ID의 현재 위치 가져오기 """
        command = f"GET_POSITION {servoid}"
        print(command)
        response = self.post_command(command=command, expect_response=True)
        print('res : ',response)
        if response:
            try:
                return int(response)
            except ValueError:
                return None
        return None
    
    def post_actuator_curloc(self):
        """ 설정용 액추에이터(servoid1)의 현재 위치를 라벨에 업데이트 """
        cur_position = self.get_position(self.servoid1)
        if cur_position is not None:
            self.ui.CurLocLabel.setText(f"{cur_position}")
        else:
            self.ui.CurLocLabel.setText("Error")
    
    def post_actuator_fwd(self):
        """ 설정용 액추에이터(servoid1) 위치 증가 """
        current_position = self.get_position(self.servoid1)  # 현재 위치 읽기
        print(current_position)
        if current_position is not None:
            temp = int(current_position) + 100 # 설정값 100 (추후 수정가능하게 변경)
            new_position = temp if temp <= 4090 else 4090  
            command = f"SET_POSITION {self.servoid1} {new_position}"
            self.post_command(command)
            self.post_actuator_curloc() # 현재 위치 라벨 업데이트
    
    def post_actuator_bwd(self):
        """ 설정용 액추에이터(servoid1) 위치 감소 """
        current_position = self.get_position(self.servoid1)  # 현재 위치 읽기
        if current_position is not None:
            temp = int(current_position) - 100
            new_position = temp if temp >= 1 else 0 
            command = f"SET_POSITION {self.servoid1} {new_position}"
            self.post_command(command)
            self.post_actuator_curloc()  # 현재 위치 라벨 업데이트

    def post_actuator_home(self):
        """ 설정용 액추에이터(servoid1)을 0 위치로 이동 """
        command = f"SET_POSITION {self.servoid1} 0"
        self.post_command(command)
        self.post_actuator_curloc()  # 현재 위치 라벨 업데이트
    
    def init_setup(self):
        """ 전체 설정 저장 """
        try:
            # 각 텍스트 박스 입력 값 멤버 변수에 저장
            self.position1 = int(self.ui.Pos1LineEdit.text()) 
            self.position2 = int(self.ui.Pos2LineEdit.text()) 
            self.total_test1_counts = int(self.ui.S1TotalLineEdit.text())
            self.one_test1_counts = int(self.ui.S1CountLineEdit.text())   
            self.total_test2_counts = int(self.ui.S2TotalLineEdit.text())
            self.one_test2_counts = int(self.ui.S2CountLineEdit.text())
            
            # 저장 상태 성공 유무 상태 메시지 표시
            self.ui.SaveStatusLabel.setText("Success!!")
        except ValueError:
            # 입력값이 유효하지 않을 때 오류 메시지 표시
            self.ui.StatusLabel.setText("Error: Invalid Input")
            
    # def reset_setup(self):
    #     """ 전체 설정 초기화 """
    #     self.position1, self.position2, self.total_test1_counts, self.one_test1_counts, self.comp_test1_counts = 0, 0, 0, 0, 0
    #     self.worker1, self.worker2 = None, None
    #     self.ui.Pos1LineEdit.clear()
    #     self.ui.Pos2LineEdit.clear()
    #     self.ui.S1TotalLineEdit.clear()
    #     self.ui.S1CountLineEdit.clear()
    #     self.ui.S2TotalLineEdit.clear()
    #     self.ui.S2CountLineEdit.clear()
    #     self.ui.SaveStatusLabel.setText("Settings reset")
    
    def reset_setup(self):
        """ 전체 설정 초기화 """
        print("reset_setup 호출")
        self.position1, self.position2, self.total_test1_counts, self.one_test1_counts, self.comp_test1_counts = 0, 0, 0, 0, 0
        self.total_test2_counts, self.one_test2_counts, self.comp_test2_counts = 0, 0, 0
        # 기존 스레드를 중지하고 새로 생성
        if self.worker1 and self.worker1.isRunning():
            self.worker1.stop()
            self.worker1.wait()
        if self.worker2 and self.worker2.isRunning():
            self.worker2.stop()
            self.worker2.wait()
        self.worker1 = WorkerThread(self.servoid1, test_counts_total=10, position1=100, position2=500, serial_obj=self.serial_obj)
        self.worker2 = WorkerThread(self.servoid2, test_counts_total=10, position1=100, position2=500, serial_obj=self.serial_obj)
        self.worker1.update_status.connect(self.update_worker1_status)
        self.worker2.update_status.connect(self.update_worker2_status)
        self.ui.Pos1LineEdit.clear()
        self.ui.Pos2LineEdit.clear()
        self.ui.S1TotalLineEdit.clear()
        self.ui.S1CountLineEdit.clear()
        self.ui.S2TotalLineEdit.clear()
        self.ui.S2CountLineEdit.clear()
        self.ui.SaveStatusLabel.setText("Settings reset")
        self.ui.S1CompLabel.setText(f"{self.comp_test1_counts}")
        self.ui.S2CompLabel.setText(f"{self.comp_test2_counts}")
        print("설정 초기화 완료")

    
    ######################## [Run] ###############################
    def start_worker1(self):
        """ Worker 1 스레드 시작 """
        try:
            # 입력된 작업 개수 가져오고, 정수로 변환
            total_tasks = self.total_test1_counts
            if total_tasks <= 0:
                raise ValueError("Total tasks must be a positive integer.")
            if not self.worker1.isRunning(): # 스레드가 실행 중이 아닐 때만 시작
                self.worker1.test_counts_total = total_tasks # 총 작업 개수 업데이트
                self.worker1.start() # 기존 스레드 계속 사용
        except ValueError as e:
            self.ui.S1CompLabel.setText(f"Error: {str(e)}")
    
    def stop_worker1(self):
        """ Worker 1 스레드 중지 """
        self.worker1.stop()
        
    def reset_worker1(self):
        """ Worker 1 리셋 """
        self.worker1.reset() # 작업 기록 초기화
        self.ui.S1CompLabel.setText(f"{self.comp_test1_counts}")
    
    def start_worker2(self):
        """ Woker 2 스레드 시작 """
        try:
            # 입력된 작업 개수 가져오고, 정수로 변환
            total_tasks = self.total_test2_counts
            if total_tasks <= 0:
                raise ValueError("Total tasks must be a positive integer.")
            if not self.worker2.isRunning(): # 스레드가 실행 중이 아닐 때만 시작
                self.worker2.test_counts_total = total_tasks # 총 작업 개수 업데이트
                self.worker2.start() # 기존 스레드 계속 사용
        except ValueError as e:
            self.ui.S2CompLabel.setText(f"Error: {str(e)}")
            
    def stop_worker2(self):
        """ Worker 2 스레드 중지 """
        self.worker2.stop()
            
    def reset_worker2(self):
        """ Worker 2 리셋 """
        self.worker2.reset() # 작업 기록 초기화
        self.ui.S2CompLabel.setText(f"{self.comp_test2_counts}")
        
    def update_worker1_status(self, completed):
        """ Worker 1의 상태를 업데이트 """
        self.ui.S1CompLabel.setText(f"{completed}")  # Worker 1의 라벨 텍스트를 상태로 업데이트
    
    def update_worker2_status(self, completed):
        """ Worker 2의 상태를 업데이트 """
        self.ui.S2CompLabel.setText(f"{completed}")  # Worker 2의 라벨 텍스트를 상태로 업데이트
    
    def close_window(self):    
        """ 프로그램 종료 """
        sys.exit(app.exec())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ActuatorControlApp()
    sys.exit(app.exec_())
