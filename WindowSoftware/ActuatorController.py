"""

"""
import sys
import serial
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
import time
import glob


class ActuatorControlApp(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("ActuatorController.ui")
        
        self.serial_obj = None       # 시리얼 객체
        self.is_serial_open = False  # 시리얼 포트 연결 상태
        self.servo_id = 1            # 액추에이터의 Servo ID
        
        ######################## [Setup] ###############################
        # [Board Setting]
        self.ui.PortComboBox.addItem("")                               # Port 콤보 박스
        self.ui.BaudrateComboBox.addItem("9600")                       # Baudrate 콤보 박스
        self.ui.BaudrateComboBox.addItem("19200")
        self.ui.BaudrateComboBox.addItem("57600")
        self.ui.BaudrateComboBox.addItem("115200")                     # Baudrate 선택 옵션 추가
        self.init_serial_ports()                                      # 윈도우 애플리케이션 - CT01 보드간 연결 및 Port, Baudrate 자동 탐지 
        self.ui.ServoIDLineEdit.setPlaceholderText("1")               # 서보 id 라인박스 
        self.ui.ConnectPushBtn.clicked.connect(self.set_board_connect) # 보드 연결 버튼
        self.ui.StatusLabel.setText("Disconnected")                    # 보드 연결 상태 표시 라벨
        
        self.ui.SetupExitPushBtn.clicked.connect(self.close_window) # 프로그램 종료 버튼
        self.ui.show()
        
        
    def init_serial_ports(self):
        """ 
        시스템에 연결된 직렬 포트를 탐지 및 유효한 포트를 반환.
        탐지된 포트는 UI의 'Port', 'Baudrate'컴보박스에 추가됨.
        프로그래 첫 시작 시 매번 실행됨.
        """
        print("Initializing serial ports...")
        # 운영체제 별로 구분
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]    
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'): 
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'): 
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        print(f"Found ports: {ports}")
        result = [] 
        for port in ports:
            try:
                print(f"Checking port: {port}")
                # 포트를 열어 사용 가능한지 확인
                s = serial.Serial(port)   
                s.close()
                self.ui.PortComboBox.addItem(port)
                result.append(port)   
            except (OSError, serial.SerialException) as e:  
                print(f"Error with port {port}: {e}")
        print("Ports initialization completed.")
        return result 
    
    def set_board_connect(self):
        """ Connect 버튼: 보드 연결/해제 """
        print("Trying to connect to the board...")
        # 시리얼 연결 X 일때,
        if not self.is_serial_open:
            # 콤보박스에서 선택된 값 가져오기
            com = self.ui.PortComboBox.currentText()
            baud = self.ui.BaudrateComboBox.currentText()
            servo_id = self.ui.ServoIDLineEdit.text()
            try:
                self.serial_obj = serial.Serial(com, baud, timeout=1) # 시리얼 포트 연결 시도
                self.servo_id = servo_id
                self.ui.ConnectPushBtn.setText("DisConnect")          # 버튼 텍스트 DisConnect으로 변경
                self.ui.StatusLabel.setText("Connected")              # 상태 라벨 Connected로 변경
                self.is_serial_open = True                            # 연결 상태 True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not connect: {str(e)}")
        # 시리얼 이미 연결된 상태
        else:
            if self.serial_obj:
                self.serial_obj.close()                # 시리얼 객체 닫기 
            self.ui.ConnectPushBtn.setText("Connect")  # 버튼 텍스트 Connect로 변경
            self.ui.StatusLabel.setText("Disconnected")# 상태 라벨 Disconnected로 변경
            self.is_serial_open = False                # 연결 상태 False
        
        
    def close_window(self):    
        """ 프로그램 종료 """
        sys.exit(app.exec())
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ActuatorControlApp()
    sys.exit(app.exec_())