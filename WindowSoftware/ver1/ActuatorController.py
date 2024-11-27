"""

"""
import sys
import serial
from serial.tools import list_ports
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
import time, re
import glob


class ActuatorControlApp(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("ActuatorController.ui")
        
        self.serial_obj = None       # 시리얼 객체
        self.is_serial_open = False  # 시리얼 포트 연결 상태
        self.servo_id = 0            # 액추에이터의 Servo ID
        self.position1 = 0          # 포지션 1 위치
        self.position2 = 0          # 포지션 2 위치
        self.test_counts = 0  # 전체 테스트 횟수
        self.push_counts = 0    # 테스트 1회당 액추에이터 왕복 횟수
        self.complete_counts = 0   # 완료된 테스트 횟수
        self.test_running = False  # 테스트 진행 유무
        
        ######################## [Setup] ###############################
        # [Board Setting]
        self.ui.PortComboBox.addItem("")                                        # Port
        self.ui.BaudrateComboBox.addItems(["9600", "19200", "57600", "115200"]) # Baudrate
        self.ui.ServoIDLineEdit.setPlaceholderText("0")                          # Servo id
        self.ui.SearchPushBtn.clicked.connect(self.display_serial_ports)   # 시리얼 포트 탐색 버튼
        self.ui.ConnectPushBtn.clicked.connect(self.setup_board_connect) # 보드 연결 버튼
        self.ui.StatusLabel.setText("Disconnected")                    # 보드 연결 상태 표시 라벨
        
        # [JOG Setting]
        self.ui.JoglocLabel.setText("0")                             # 설정용 액추에이터 현재 위치 라벨 
        self.ui.HomePushBtn.clicked.connect(self.actuator_home) # 설정용 액추에이터 원점 이동 버튼
        self.ui.FwdPushBtn.clicked.connect(self.actuator_fwd)   # 설정용 액추에이터 전진(증가) 버튼
        self.ui.BwdPushBtn.clicked.connect(self.actuator_bwd)   # 설정용 액추에이터 후진(감소) 버튼
        self.ui.Pos1LineEdit.setText("")                             # 포지션1 위치 입력 라인 텍스트 박스
        self.ui.Pos2LineEdit.setText("")                             # 포지션2 위치 입력 라인 텍스트 박스
        
        # [Test Setting]  
        self.ui.TotalCountLineEdit.setText("")                            # 전체 목표 테스트 횟수 입력 라인 텍스트 박스
        self.ui.PushCountLineEdit.setText("")                            # 1회당 목표 왕복 횟수 입력 라인 텍스트 박스
        
        self.ui.SetupSavePushBtn.clicked.connect(self.save_setup)        # 전체 설정 저장 버튼
        self.ui.SetupResetPushBtn.clicked.connect(self.reset_setup) # 전체 설정 초기화 버튼
        
        
        ######################## [Setup] ###############################
        self.ui.TotalCountLabel.setText(f"{self.test_counts}")  # 전체 테스트 목표 횟수
        self.ui.CompleteCountLabel.setText(f"{self.complete_counts}")    # 완료된 테스트 횟수
        self.ui.TestStartBtn.clicked.connect(self.test_start) # 테스트 시작 버튼
        self.ui.TestStopBtn.clicked.connect(self.test_stop)  # 테스트 일시 정지 버튼
        self.ui.TestResetBtn.clicked.connect(self.test_reset) # 테스트 초기화 버튼
        
        self.ui.SetupExitPushBtn.clicked.connect(self.close_window)    # 프로그램 종료 버튼
        self.ui.show() # UI 화면 출력
        
        
    #################################################################################
    # [Common Setting Fuction]
    
    def _send_command(self, command, expect_response=False):
        """ 보드에 시리얼 통신 명령어 전송 """
        if self.serial_obj and self.serial_obj.is_open:
            print(f'[post_command] 명령어 전송: {command}')
            self.serial_obj.write(f"{command}\n".encode())
            time.sleep(0.1)
            if expect_response:
                response = self.serial_obj.readline()
                response[:len(response)-1].decode().strip()
                return response
        return None
        
    ################################################################################
    # [Port Setting Fuction]
    
    def display_serial_ports(self):
        """ 
        시스템에 연결된 직렬 포트를 탐지하고 유효한 포트와 해당 정보를 UI에 표시.
        탐지된 포트는 UI의 Port 콤보박스에 추가됨.
        """
        print("[get_serial_ports] 연결된 직렬 포트 탐색 중...")
        self.ui.PortComboBox.clear()  # 기존 항목 초기화
        self.ui.PortComboBox.addItem("")  # 빈 항목 추가
        
        ports = list_ports.comports()  # 연결된 모든 포트와 상세 정보 가져오기
        port_list = []  # 탐색된 포트 저장
        
        for port in ports:
            port_name = port.device            # 예: "COM3"
            port_desc = port.description       # 예: "USB-SERIAL CH340 (COM3)"
            
            # 포트 이름과 Description을 콤보박스에 추가
            self.ui.PortComboBox.addItem(f"{port_desc}")
            port_list.append(port_name)
        
        print(f"[get_serial_ports] 직렬 포트 탐색 완료: {port_list}")
        return port_list
    
    
    def setup_board_connect(self):
        """ Connect 버튼: 보드 연결/해제 """
        print("[set_board_connect] 보드 연결/연결해제 시도 중...")
        
        if not self.is_serial_open:
            selected = self.ui.PortComboBox.currentText()
            
            # 괄호 안의 COM 포트 추출 (정규식 사용)
            match = re.search(r'\((.*?)\)', selected)
            if match:
                com = match.group(1)  # 예: "COM3"
            else:
                QMessageBox.warning(self, "Alert", "The port is not selected.")
                return
            
            baud = self.ui.BaudrateComboBox.currentText()
            servo_id = self.ui.ServoIDLineEdit.text()
            
            try:
                self.serial_obj = serial.Serial(com, baud, timeout=1)  
                self.servo_id = int(servo_id)
                self.is_serial_open = True
                self.ui.ConnectPushBtn.setText("DisConnect")           
                self.ui.StatusLabel.setText(f"Connected ({com})")               
                QMessageBox.information(self, "Alert", f"Connection Successful!\nYou are connected to {com}.")                       
                self._post_actuator_curloc() # 현재 위치 출력 라벨 업데이트 
                print("[set_board_connect] 보드 연결 성공")
            except Exception as e:
                print(e)
                QMessageBox.critical(self, "Alert", f"Connection Failed. \nUnable to connect to port {com}.\nError: {str(e)}")
                self.ui.StatusLabel.setText("Disconnected")
        else:
            if self.serial_obj:
                self.serial_obj.close()                 
            self.is_serial_open = False
            self.ui.ConnectPushBtn.setText("Connect")   
            self.ui.StatusLabel.setText("Disconnected")
            print("[set_board_connect] 보드 연결 해제 성공")
            QMessageBox.information(self, "Alert", "Disconnected.")
            
    ################################################################################
    # [JOG Setting Fuction]
    
    def _get_position(self, servo_id):
        """ 지정된 액추에이터 서보 ID의 현재 위치 가져오기 """
        command = f"GET_POSITION {servo_id}"
        location = self._send_command(command=command, expect_response=True)
        print('[get_position] 액추에이터 현재 위치 명령어 반환값 : ',location)
        if location:
            try:
                return int(location)
            except ValueError:
                return None
        return None
    
    def _post_actuator_curloc(self):
        """ 설정용 액추에이터(servoid1)의 현재 위치를 라벨에 업데이트 """
        cur_position = self._get_position(self.servo_id)
        if cur_position is not None:
            self.ui.JoglocLabel.setText(f"{cur_position}")
        else:
            self.ui.JoblocLabel.setText("0")
    
    def actuator_fwd(self):
        """ 설정용 액추에이터(servoid1) 위치 증가 """
        print(f'[actuator_fwd] 액추에이터 위치 증가 버튼 클릭')
        current_position = self._get_position(self.servo_id)  # 현재 위치 읽기
        if current_position is not None:
            temp = int(current_position) + 300 # 설정값 100 (추후 수정가능하게 변경)
            new_position = temp if temp <= 4090 else 4090  
            command = f"SET_POSITION {self.servo_id} {new_position}"
            self._send_command(command)
            self._post_actuator_curloc() # 현재 위치 라벨 업데이트
    
    def actuator_bwd(self):
        """ 설정용 액추에이터(servoid1) 위치 감소 """
        print(f'[actuator_bwd] 액추에이터 위치 감소 버튼 클릭')
        current_position = self._get_position(self.servo_id)  # 현재 위치 읽기
        if current_position is not None:
            temp = int(current_position) - 300
            new_position = temp if temp >= 1 else 0 
            command = f"SET_POSITION {self.servo_id} {new_position}"
            self._send_command(command)
            self._post_actuator_curloc()  # 현재 위치 라벨 업데이트
            
    def actuator_home(self):
        """ 설정용 액추에이터(servoid1)을 0 위치로 이동 """
        print(f'[actuator_home] 액추에이터 위치 초기화 버튼 클릭')
        command = f"SET_POSITION {self.servo_id} 0"
        self._send_command(command)
        while True:
            if self._get_position(self.servo_id) < 30:
                self._post_actuator_curloc()  # 현재 위치 라벨 업데이트
                break                
    ################################################################################
    # [Test Setting Fuction]
    
    def save_setup(self):
        """ 전체 설정 저장 """
        print(f'[save_setup] 전체 설정 저장 버튼 클릭')
        try:
            # 각 텍스트 박스 입력 값 멤버 변수에 저장
            self.position1 = int(self.ui.Pos1LineEdit.text()) 
            self.position2 = int(self.ui.Pos2LineEdit.text()) 
            self.test_counts = int(self.ui.TotalCountLineEdit.text())
            self.push_counts = int(self.ui.PushCountLineEdit.text())
            
            self.ui.TotalCountLabel.setText(f"{self.test_counts}")
            QMessageBox.information(self, "Alert", "Success! The settings have been saved.")
        except ValueError:
            QMessageBox.critical(self, "Alert", f"Failed. \nAn invalid value was entered.")

    def reset_setup(self):
        """ 전체 설정 초기화 """
        print(f'[reset_setup] 전체 설정 초기화 버튼 클릭')
        self.position1, self.position2, self.test_counts, self.push_counts, self.complete_counts = 0, 0, 0, 0, 0
        self.ui.Pos1LineEdit.clear()
        self.ui.Pos2LineEdit.clear()
        self.ui.TotalCountLineEdit.clear()
        self.ui.PushCountLineEdit.clear()
        QMessageBox.warning(self, "Alert", "All settings have been reset.")
    
    ################################################################################
    # [Run]
    def test_start(self):
        """ 테스트 시작 """
        print("[test_start] 테스트 시작 버튼 클릭")
        self.test_running = True # 플래그
        self._send_command(f"SET_POSITION {self.servo_id} 0")        
        time.sleep(1)
        
        while self.complete_counts < self.test_counts and self.test_running:
            print(f"[test_start] 테스트 {self.complete_counts + 1}회 시작")
            push = self.push_counts
            self._send_command(f"SET_POSITION {self.servo_id} {self.position1}")
            time.sleep(1)
            
            while 0 < push and self.test_running:
                self._send_command(f"SET_POSITION {self.servo_id} {self.position2}")
                time.sleep(0.3)
                self._send_command(f"SET_POSITION {self.servo_id} {self.position1}")
                time.sleep(0.5)
                push -= 1
                print(f"[test_start] 남은 왕복 횟수: {push}")
            
            # 테스트 완료 후 0으로 복귀
            self._send_command(f"SET_POSITION {self.servo_id} 0")            
            time.sleep(1)
            
            self.complete_counts += 1
            self.ui.CompleteCountLabel.setText(f"{self.complete_counts}")
            print(f"[test_start] 테스트 {self.complete_counts}회 완료")
        
        
        # 테스트 종료 처리
        if not self.test_running:
            print("[test_start] 테스트가 중단되었습니다.")
        else:
            print("[test_start] 모든 테스트가 완료되었습니다.")
        self.test_running = False
        QMessageBox.information(self, "Test Complete", "All tests are complete.")
                
    def test_stop(self):
        """ 테스트 중지 """
        print("[test_stop] 테스트 중지 버튼 클릭")
        self.test_running = False
        self._send_command(f"SET_POSITION {self.servo_id} 0")
        self.ui.CompleteCountLabel.setText(f"{self.complete_counts}")
        time.sleep(0.3)
        QMessageBox.information(self, "Test Stopped", "The test has been stopped and the actuator is returned to position 0.")
        print("[test_stop] 테스트가 중단되고 0으로 복귀합니다.")
        
    def test_reset(self):
        """ 테스트 초기화 """
        self.complete_counts = 0
        self.ui.CompleteCountLabel.setText(f"{self.complete_counts}")
        QMessageBox.warning(self, "Alert", "Test has been reset.")
    
    
    
    
    
    
    def close_window(self):    
        """ 프로그램 종료 """
        sys.exit(app.exec())
    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ActuatorControlApp()
    sys.exit(app.exec_())
    