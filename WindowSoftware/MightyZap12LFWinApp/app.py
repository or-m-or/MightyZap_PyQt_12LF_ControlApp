"""
[ PyQt5기반 메인 데스크톱 애플리케이션 ]
"""
import sys
import re
import serial
from serial.tools import list_ports
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QVBoxLayout, QLabel, QPushButton
from actuator import Actuator
from position import PositionUpdater
from worker import TestWorker


class ActuatorControlApp(QDialog):
    def __init__(self):
        super().__init__()
        print("[디버깅] ActuatorControlApp 초기화 시작")
        self.ui = uic.loadUi("ui/app.ui")

        self.actuators = []   # 액추에이터 리스트
        self.actuator_ui_map = {}  # 액추에이터와 UI 매핑
        self.workers = {}  # 액추에이터별 작업자(QThread) 관리
        self.is_testing = False  # 테스트 실행 상태 플래그
        self.position_updater = None  # 설정 화면 액추에이터 실시간 위치 업데이트를 위한 쓰레드
        self.position1 = 0    # 포지션 1
        self.position2 = 0    # 포지션 2
        self.push_counts = 0  # 왕복 횟수
        self._initialize_ui() # UI 피처 초기화
        self.ui.TabWidget.currentChanged.connect(self.on_tab_changed) # TabWidget 탭 변경 시그널 연결
        
        print("[디버깅] UI 초기화 완료")
        self.ui.show()        

    def _initialize_ui(self):
        """ UI 요소 초기화 및 이벤트 연결 """
        print("[디버깅] UI 요소 초기화 중")
        # 보드 설정
        self.ui.PortComboBox.addItem("")
        self.ui.BaudrateComboBox.addItems(["9600", "19200", "57600", "115200"])
        self.ui.ServoIDLineEdit.setPlaceholderText("0")
        self.ui.SearchPushBtn.clicked.connect(self.display_serial_ports)
        self.ui.ConnectPushBtn.clicked.connect(self.setup_board_connect)
        self.ui.DisconnectPushBtn.clicked.connect(self.setup_board_disconnect)
        
        # JOG 설정
        self.ui.HomePushBtn.clicked.connect(self.actuator_home)
        self.ui.FwdPushBtn.clicked.connect(self.actuator_fwd)
        self.ui.BwdPushBtn.clicked.connect(self.actuator_bwd)
        self.ui.JoglocLabel.setText("board is not connected")
        self.ui.BoardComboBox.currentIndexChanged.connect(self.on_board_selected)
        
        # 테스트 설정
        self.ui.SetupSavePushBtn.clicked.connect(self.save_setup)
        self.ui.SetupResetPushBtn.clicked.connect(self.reset_setup)
        # self.ui.TestStartBtn.clicked.connect(self.test_start)
        # self.ui.TestResetBtn.clicked.connect(self.test_reset)
        self.ui.SetupExitPushBtn.clicked.connect(self.close_window)

    def display_serial_ports(self):
        """ 연결된 직렬 포트 탐지 및 UI 표시 """
        print("[디버깅] 사용 가능한 직렬 포트 탐색 중")
        self.ui.PortComboBox.clear()
        self.ui.PortComboBox.addItem("")
        ports = list_ports.comports() # 연결된 모든 포트와 상세 정보 가져오기
        valid_ports = [] # 유효한 포트 저장
        for port in ports:
            print(f"[디버깅] 발견된 포트: {port.device}, {port.description}")
            self.ui.PortComboBox.addItem(f"{port.description}") # 콤보박스에 포트 설명 추가 예) "USB-SERIAL CH340 (COM3)"
            valid_ports.append(port.device) # 포트 이름 리스트에 추가 예) "COM3"
        return valid_ports

    def setup_board_connect(self):
        """ 보드 연결 """
        print("[디버깅] 보드 연결 시도 중")
        selected = self.ui.PortComboBox.currentText()
        match = re.search(r'\((.*?)\)', selected)
        # 예외처리: 포트 선택 X
        if not match:
            print("[디버깅] 선택된 포트 없음")
            QMessageBox.warning(self, "Alert", "The port is not selected.")
            return
        port = match.group(1) # 예) "COM3"
        print(f"[디버깅] 선택된 포트: {port}")

        # 예외처리: 이미 연결된 포트
        if any(act.port == port for act in self.actuators):
            print(f"[디버깅] 포트 {port}는 이미 연결됨")
            QMessageBox.information(self, "Info", f"Board {port} is already connected.")
            return
        
        baud = self.ui.BaudrateComboBox.currentText()
        servo_id = self.ui.ServoIDLineEdit.text()
        print(f"[디버깅] 포트: {port}, 보드레이트: {baud}, 서보 ID: {servo_id} 연결 시도")

        try:
            serial_obj = serial.Serial(port, baud, timeout=1)
            actuator = Actuator(servo_id=int(servo_id), serial_obj=serial_obj, baudrate=baud, port=port)
            self.actuators.append(actuator)
            self.ui.BoardComboBox.addItem(port)
            self.ui.BoardComboBox.setCurrentIndex(self.ui.BoardComboBox.count() - 1)  # 새 항목 선택
            if actuator not in self.actuator_ui_map:
                self.create_actuator_ui(actuator)
            print(f"[디버깅] 포트 {port} 연결 성공")
            
            # PositionUpdater 쓰레드 초기화 및 시작
            if not self.position_updater:
                print("[디버깅] PositionUpdater 쓰레드 초기화")
                self.position_updater = PositionUpdater(self.actuators)
                self.position_updater.position_updated.connect(self._update_jogloc_label)
                self.position_updater.start()
                print("[디버깅] PositionUpdater 쓰레드 시작")
            
            # 대상 포트를 강제로 설정
            if self.position_updater:
                print(f"[디버깅] PositionUpdater 대상 포트 설정: {port}")
                self.position_updater.set_target_port(port)
            
            # 액추에이터 초기 위치 설정
            print(f"[디버깅] 액추에이터 {actuator.servo_id} 초기 위치 설정: 0")
            actuator.send_command(f"SET_POSITION {actuator.servo_id} 0")
            QMessageBox.information(self, "Alert", f"Connection Successful!\nYou are connected to {port}.")
        except Exception as e:
            print(f"[디버깅] 포트 {port} 연결 실패: {e}")
            QMessageBox.critical(self, "Alert", f"Connection Failed.\nError: {str(e)}")

    def setup_board_disconnect(self):
        """ 보드 연결 해제 """
        print("[디버깅] 보드 연결 해제 시도 중")
        selected = self.ui.BoardComboBox.currentText()
        actuator = next((act for act in self.actuators if act.port == selected), None)
        if actuator:
            print(f"[디버깅] 포트 {selected} 연결 해제 중")
            actuator.serial_obj.close()
            self.actuators.remove(actuator)
            self.ui.BoardComboBox.removeItem(self.ui.BoardComboBox.currentIndex())
            QMessageBox.information(self, "Alert", f"Board {selected} disconnected.")
        else:
            print("[디버깅] 연결 해제 대상 액추에이터 없음")

    def on_board_selected(self):
        """ BoardComboBox에서 선택된 보드 변경 시 처리 """
        selected_port = self.ui.BoardComboBox.currentText()
        print(f"[디버깅] 선택된 보드 변경: {selected_port}")
        if not selected_port:  # 선택된 보드가 없을 경우
            self.ui.JoglocLabel.setText("board is not connected")
            if self.position_updater:
                print("[디버깅] PositionUpdater 대상 포트 해제")
                self.position_updater.set_target_port(None)
        else:
            if self.position_updater:
                print(f"[디버깅] PositionUpdater 대상 포트 설정: {selected_port}")
                self.position_updater.set_target_port(selected_port)

    def _update_jogloc_label(self, position):
        """ JoglocLabel에 현재 위치 표시 """
        print(f"[디버깅] JoglocLabel 업데이트: {position}")
        if position is not None:
            # 1자리 단위로 내림 처리
            rounded_position = position // 10 * 10
            print(f"[디버깅] 내림 처리된 위치: {rounded_position}")
            self.ui.JoglocLabel.setText(f"{rounded_position}")
        else:
            self.ui.JoglocLabel.setText("board is not connected")

            
    def on_tab_changed(self, index):
        """탭 변경 시 호출"""
        current_tab_name = self.ui.TabWidget.tabText(index)
        print(f"[디버깅] 탭 변경: {current_tab_name} ({index})")

        if current_tab_name == "Setup":
            # Setup 탭일 때 위치 측정 쓰레드 동작
            if self.position_updater:
                print("[디버깅] 위치 측정 쓰레드 재시작")
                self.position_updater.start()
        else:
            # 다른 탭일 때 위치 측정 쓰레드 중지
            if self.position_updater and self.position_updater.isRunning():
                print("[디버깅] 위치 측정 쓰레드 중지")
                self.position_updater.stop()

                             
    def actuator_home(self):
        """ 액추에이터를 원점으로 이동 """
        print("[디버깅] 액추에이터 원점 이동 시도")
        selected_port = self.ui.BoardComboBox.currentText()
        actuator = next((act for act in self.actuators if act.port == selected_port), None)
        if actuator:
            print(f"[디버깅] 포트 {selected_port}의 액추에이터 원점 이동 명령 전송")
            actuator.send_command(f"SET_POSITION {actuator.servo_id} 0")
            # self._update_jogloc_label()
            # QMessageBox.information(self, "Alert", f"Actuator {actuator.servo_id} moved to home position.")

    def _get_position(self, actuator):
        """ 지정된 액추에이터의 현재 위치 가져오기 """
        if actuator and actuator.serial_obj and actuator.serial_obj.is_open:
            command = f"GET_POSITION {actuator.servo_id}"
            location = actuator.send_command(command, expect_response=True)
            if location:
                try:
                    return int(location)
                except ValueError:
                    print(f"[디버깅] 위치 값을 정수로 변환 실패: {location}")
                    return None
        print("[디버깅] 액추에이터가 열려 있지 않음 또는 잘못된 액추에이터")
        return None

    
    def actuator_fwd(self):
        """ 액추에이터 위치 증가 """
        print("[디버깅] 액추에이터 위치 증가 시도")
        selected_port = self.ui.BoardComboBox.currentText()
        actuator = next((act for act in self.actuators if act.port == selected_port), None)
        if actuator:
            current_position = self._get_position(actuator)
            if current_position is not None:
                temp = int(current_position) + 300 # 설정값 100 (추후 수정가능하게 변경)
                new_position = temp if temp <= 4090 else 4090  
                print(f"[디버깅] 포트 {selected_port}의 액추에이터 위치 증가. 새 위치: {new_position}")
                actuator.send_command(f"SET_POSITION {actuator.servo_id} {new_position}")
            # self._update_jogloc_label()
            # QMessageBox.information(self, "Alert", f"Actuator {actuator.servo_id} moved forward.")
        else:
            print("[디버깅] 선택된 액추에이터 없음")
            

    def actuator_bwd(self):
        """ 액추에이터 위치 감소 """
        print("[디버깅] 액추에이터 위치 감소 시도")
        selected_port = self.ui.BoardComboBox.currentText()
        actuator = next((act for act in self.actuators if act.port == selected_port), None)
        if actuator:
            current_position = self._get_position(actuator)
            if current_position is not None:
                temp = int(current_position) - 300
                new_position = temp if temp >= 1 else 0             
                print(f"[디버깅] 포트 {selected_port}의 액추에이터 위치 감소. 새 위치: {new_position}")
                actuator.send_command(f"SET_POSITION {actuator.servo_id} {new_position}")
            # self._update_jogloc_label()
            # QMessageBox.information(self, "Alert", f"Actuator {actuator.servo_id} moved backward.")
        else:
            print("[디버깅] 선택된 액추에이터 없음")
    

    def save_setup(self):
        """설정 저장"""
        print("[디버깅] 설정 저장 시도")
        try:
            self.position1 = int(self.ui.Pos1LineEdit.text())
            self.position2 = int(self.ui.Pos2LineEdit.text())
            self.push_counts = int(self.ui.PushCountLineEdit.text())
            print(f"[디버깅] 설정 저장 완료: 포지션1={self.position1}, 포지션2={self.position2}, 왕복 횟수={self.push_counts}")
            QMessageBox.information(self, "Alert", "Settings have been saved.")
        except ValueError:
            print("[디버깅] 설정 저장 실패: 입력값이 잘못되었습니다.")
            QMessageBox.critical(self, "Alert", "Invalid settings.")

    def reset_setup(self):
        """ 전체 설정 초기화 """
        print("[디버깅] 설정 초기화 시도")
        self.position1, self.position2, self.test_counts, self.push_counts, self.complete_counts = 0, 0, 0, 0, 0
        self.ui.Pos1LineEdit.clear()
        self.ui.Pos2LineEdit.clear()
        self.ui.PushCountLineEdit.clear()
        print("[디버깅] 설정 초기화 완료")
        QMessageBox.warning(self, "Alert", "All settings have been reset.")
    
    def create_actuator_ui(self, actuator):
        """ 액추에이터별 UI 생성 """
        main_layout = self.ui.MainLayout  # UI 파일의 MainLayout
        layout = QVBoxLayout()

        # Complete Count Label
        complete_count_label = QLabel("Complete Count: 0")
        layout.addWidget(complete_count_label)

        # Start Button
        start_btn = QPushButton("Start Test")
        layout.addWidget(start_btn)
        start_btn.clicked.connect(lambda: self.test_start(actuator, complete_count_label))

        # Reset Button
        reset_btn = QPushButton("Reset Count")
        layout.addWidget(reset_btn)
        reset_btn.clicked.connect(lambda: self.reset_count(actuator, complete_count_label))

        # Add layout to main UI
        main_layout.addLayout(layout)

        # Store UI components in a dictionary
        self.actuator_ui_map[actuator] = {
            "complete_count_label": complete_count_label,
            "start_btn": start_btn,
            "reset_btn": reset_btn,
        }

    
    def test_start(self, actuator, label):
        """테스트 시작"""
        print(f"[디버깅] 테스트 시작: {actuator.port}")
        if actuator in self.workers and self.workers[actuator].isRunning():
            QMessageBox.warning(self, "Alert", "Test is already running for this actuator.")
            return

        worker = TestWorker(actuator, self.position1, self.position2, self.push_counts)
        self.workers[actuator] = worker

        worker.test_complete.connect(lambda: self.update_count(actuator, label))
        worker.finished.connect(lambda: self.cleanup_worker(actuator))
        worker.start()

    def update_count(self, actuator, label):
        """ 완료 횟수 증가 및 UI 업데이트 """
        actuator.complete_count += 1
        label.setText(f"Complete Count: {actuator.complete_count}")
        print(f"[디버깅] {actuator.port} 완료 횟수: {actuator.complete_count}")

    def reset_count(self, actuator, label):
        """ 완료 횟수 초기화 """
        actuator.complete_count = 0
        label.setText("Complete Count: 0")
        print(f"[디버깅] {actuator.port} 완료 횟수 초기화")
        

    def cleanup_worker(self, actuator):
        """ 작업자 정리 """
        if actuator in self.workers:
            print(f"[디버깅] {actuator.port} 작업자 정리")
            self.workers[actuator].quit()
            self.workers[actuator].wait()
            del self.workers[actuator]
    
    def closeEvent(self, event):
        """ 창 닫기 시 쓰레드 정리 """
        for worker in self.workers.values():
            worker.quit()
            worker.wait()
        event.accept()
        

    def close_window(self):
        """프로그램 종료"""
        self.close()
        sys.exit(app.exec())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # apply_stylesheet(app, theme='themes/dark_teal.xml')
    window = ActuatorControlApp()
    sys.exit(app.exec_())
