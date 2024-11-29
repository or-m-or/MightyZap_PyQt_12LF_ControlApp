"""
[ PyQt5기반 메인 데스크톱 애플리케이션 ]
"""
import sys
import re
import serial
from serial.tools import list_ports
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QMessageBox, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from actuator import Actuator
# from position import PositionUpdater
from worker import TestWorker
from config import DEFAULT_VALUES, setup_logger
import sys
import os


_logger = setup_logger(name="MainApp", level='INFO')

def resource_path(relative_path):
    """ PyInstaller의 임시 경로에서 리소스를 로드 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 실행 파일 경로
        return os.path.join(sys._MEIPASS, relative_path)
    # 개발 환경 실행 시
    return os.path.join(os.path.abspath("."), relative_path)

ui_path = resource_path("app.ui")

class ActuatorControlApp(QDialog):
    def __init__(self):
        super().__init__()
#        self.ui = uic.loadUi("app.ui")
        self.ui = uic.loadUi(ui_path)
        self.setWindowTitle("Actuator Controller") 
        self.default_servo_id = 0      # 서보 ID 기본지정 값 (사용자 입력 받으려면 ServoID 컴포넌트 관련 주석 해제할 것)
        self.actuators = []        # 액추에이터 리스트
        self.actuator_ui_map = {}  # 액추에이터-UI 매핑
        self.workers = {}          # 액추에이터 작업자
        self.position1 = 0         # 포지션 1
        self.position2 = 0         # 포지션 2
        self.push_counts = 5       # 왕복 횟수
        self._initialize_ui()      # UI 피처 초기화
        self.test_counts = {}
        self.timer = QTimer(self)  # 시리얼 데이터 모니터링 타이머
        self.timer.setInterval(300) # 0.3초마다
        self.timer.timeout.connect(self.monitor_serial_data)
        # self.timer.start(300)
        self.last_slider_position = None # 슬라이더 마지막 위치?
        self.slider_timer = QTimer(self)
        self.slider_timer.setInterval(50)  # 슬라이더 업데이트 간격 (50ms)
        self.slider_timer.timeout.connect(self.update_position_from_slider)
        self.is_slider_moving = False  # 슬라이더가 움직이고 있는지 상태 플래그
        self.step_size = 300
        _logger.info("ActuatorControlApp 프로그램 시작")
        self.ui.show()        

    def _initialize_ui(self):
        """ UI 요소 초기화 및 이벤트 연결 """
        # 보드 설정
        self.ui.PortComboBox.addItem("")
        self.ui.BaudrateComboBox.addItems(["9600", "19200", "57600", "115200"])
        # self.ui.ServoIDLineEdit.setPlaceholderText("0") # Servo ID 입력 박스
        self.ui.SearchPushBtn.clicked.connect(self.display_serial_ports)
        self.ui.ConnectPushBtn.clicked.connect(self.setup_board_connect)
        self.ui.DisconnectPushBtn.clicked.connect(self.setup_board_disconnect)
        # JOG 설정
        self.ui.HomePushBtn.clicked.connect(self.actuator_home)
        # self.ui.FwdPushBtn.clicked.connect(self.actuator_fwd)
        # self.ui.BwdPushBtn.clicked.connect(self.actuator_bwd)
        self.ui.JoglocLabel.setText("board is not connected")
        self.ui.BoardComboBox.currentIndexChanged.connect(self.on_board_selected)
        # self.ui.StepSpinBox.setRange(0, 4095)  
        # self.ui.StepSpinBox.setValue(300)  # 기본값 300
        # self.ui.StepSpinBox.valueChanged.connect(self.update_step_size)
        self.ui.PositionSlider.setRange(0, 4095)  # 액추에이터 위치 범위
        self.ui.PositionSlider.valueChanged.connect(self.slider_position_changed)
        # self.ui.PositionSlider.sliderReleased.connect(self.update_position_from_slider)
        # 기타 서보 설정
        # self.ui.SpeedLimitLineEdit.setPlaceholderText(str(DEFAULT_VALUES["speed_limit"]))
        # self.ui.SpeedTempLineEdit.setPlaceholderText(str(DEFAULT_VALUES["speed"]))
        # self.ui.CurrentLimitLineEdit.setPlaceholderText(str(DEFAULT_VALUES["current_limit"]))
        # self.ui.CurrentTempLineEdit.setPlaceholderText(str(DEFAULT_VALUES["current"]))
        # self.ui.ShortLimitLineEdit.setPlaceholderText(str(DEFAULT_VALUES["short_limit"]))
        # self.ui.LongLimitLineEdit.setPlaceholderText(str(DEFAULT_VALUES["long_limit"]))
        # self.ui.AccLineEdit.setPlaceholderText(str(DEFAULT_VALUES["accel"]))
        # self.ui.DecLineEdit.setPlaceholderText(str(DEFAULT_VALUES["decel"]))
        
        # 기타 서보 설정 저장/초기화
        self.ui.ActuatorSaveBtn.clicked.connect(self.save_all_settings)
        self.ui.ActuatorResetBtn.clicked.connect(self.reset_to_defaults)
        # 테스트 설정
        self.ui.SetupSavePushBtn.clicked.connect(self.save_setup)
        self.ui.SetupResetPushBtn.clicked.connect(self.reset_setup)
        self.ui.SetupExitPushBtn.clicked.connect(self.close_window)
        

    def create_actuator_ui(self, actuator):
        """ 액추에이터별 UI 생성 """
        # Main Layout 설정
        main_layout = self.ui.MainLayout  # UI 파일의 MainLayout
        layout = QVBoxLayout()

        # "Complete Count" 제목 라벨
        title_label = QLabel("Complete Count")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))  # 폰트 크기와 스타일 조정
        layout.addWidget(title_label)

        # 실제 숫자만 표시하는 라벨
        complete_count_label = QLabel("0")
        complete_count_label.setFont(QFont("Arial", 40, QFont.Bold))  # 강조된 큰 폰트
        complete_count_label.setStyleSheet("color: black; border: none;")  # 색상만 설정, 테두리 제거
        complete_count_label.setAlignment(Qt.AlignCenter)  # 가운데 정렬
        layout.addWidget(complete_count_label)

        # 버튼들 (Start, Reset)
        button_layout = QVBoxLayout()  # 버튼들을 세로로 배치
        start_btn = QPushButton("Start")
        reset_btn = QPushButton("Reset")
        button_layout.addWidget(start_btn)
        button_layout.addWidget(reset_btn)

        # Start 버튼 동작
        start_btn.clicked.connect(lambda: self.test_start(actuator, complete_count_label))

        # Reset 버튼 동작
        reset_btn.clicked.connect(lambda: self.reset_count(actuator, complete_count_label))

        # 버튼 레이아웃 추가
        layout.addLayout(button_layout)

        # 최종 레이아웃을 메인 레이아웃에 추가
        main_layout.addLayout(layout)

        # UI 매핑 정보 저장
        self.actuator_ui_map[actuator] = {
            "title_label": title_label,
            "complete_count_label": complete_count_label,
            "start_btn": start_btn,
            "reset_btn": reset_btn,
        }


    
    
    def display_serial_ports(self):
        """ 연결된 직렬 포트 탐색 """
        self.ui.PortComboBox.clear()
        self.ui.PortComboBox.addItem("")
        ports = list_ports.comports()                                      # 연결된 모든 포트와 상세 정보 가져오기
        valid_ports = []                                                   # 유효한 포트 저장
        for port in ports:
            _logger.info(f"발견된 포트: {port.device}, {port.description}")
            self.ui.PortComboBox.addItem(f"{port.description}")            # 콤보박스에 포트 설명 추가 예) "USB-SERIAL CH340 (COM3)"
            valid_ports.append(port.device)                                # 포트 이름 리스트에 추가 예) "COM3"
        return valid_ports

    def setup_board_connect(self):
        """ 보드 연결 """
        selected = self.ui.PortComboBox.currentText()
        match = re.search(r'\((.*?)\)', selected)
        
        if not match:
            _logger.warning("Port가 선택되지 않았음")
            QMessageBox.warning(self, "Alert", "The port is not selected.")
            return
        port = match.group(1) # 예) "COM3"

        if any(act.port == port for act in self.actuators):
            _logger.warning(f"이미 연결된 포트를 선택함 : {port}")
            QMessageBox.information(self, "Info", f"Board {port} is already connected.")
            return
        
        baud = self.ui.BaudrateComboBox.currentText()
        # servo_id = self.ui.ServoIDLineEdit.text()
        try:
            serial_obj = serial.Serial(port, baud, timeout=0.2)
            actuator = Actuator(servo_id=self.default_servo_id, serial_obj=serial_obj, baudrate=baud, port=port)
            self.actuators.append(actuator)
            self.ui.BoardComboBox.addItem(port)
            self.ui.BoardComboBox.setCurrentIndex(self.ui.BoardComboBox.count() - 1)  # 새 항목 선택
            if actuator not in self.actuator_ui_map:
                self.create_actuator_ui(actuator)
                
            _logger.info(f"보드 연결 성공 => 포트: {port}, 보드레이트: {baud}")
            actuator.send_command(f"SET_POSITION {actuator.servo_id} 0", expect_response=False) # 액추에이터 초기 위치 설정
            
            self.update_ui_with_actuator_settings() # 기타 서보 반영구 설정 값 가져와서 세팅
            self.timer.start()  # 타이머 시작
            QMessageBox.information(self, "Alert", f"Connection Successful!\nYou are connected to {port}.")
            self.setWindowTitle(f"Actuator Control Application - {port}")
        except Exception as e:
            _logger.error(f"포트 {port} 연결 실패: {e}")
            QMessageBox.critical(self, "Alert", f"Connection Failed.\nError: {str(e)}")

    def setup_board_disconnect(self):
        """ 보드 연결 해제 """
        selected = self.ui.BoardComboBox.currentText()
        actuator = next((act for act in self.actuators if act.port == selected), None)
        if actuator:
            actuator.serial_obj.close()
            self.actuators.remove(actuator)
            self.ui.BoardComboBox.removeItem(self.ui.BoardComboBox.currentIndex())
            
            # 연결 해제된 보드와 관련된 PositionUpdater 쓰레드 중지
            # if hasattr(self, "position_updater") and self.position_updater.target_port == selected:
            #     self.stop_position_updater()
            #     _logger.info(f"{selected}: 관련 PositionUpdater 쓰레드 정지 완료")
            
            # 타이머 정지
            if not self.actuators:  # 연결된 보드가 없을 경우만 멈춤
                self.timer.stop()
                
            QMessageBox.information(self, "Alert", f"Board {selected} disconnected.")
            _logger.info(f"포트 {selected} 연결 해제 완료")
        else:
            _logger.error("연결 해제할 보드(포트)가 없음")

    def on_board_selected(self):
        """ BoardComboBox에서 선택된 보드 변경 시 처리 """
        selected_port = self.ui.BoardComboBox.currentText()
        _logger.info(f"선택된 보드 변경: {selected_port}")
        
        # 선택된 보드가 없을 경우
        if not selected_port:  
            self.ui.JoglocLabel.setText("board is not connected")
    
    def _update_jogloc_label(self, position):
        """ JoglocLabel에 현재 위치 표시 """
        self.ui.JoglocLabel.setText(f"{position // 10 * 10}" if position is not None else "board is not connected")

    def _get_position(self, actuator):
        """ 지정된 액추에이터의 현재 위치 가져오기 """
        if actuator and actuator.serial_obj and actuator.serial_obj.is_open:
            command = f"GET_POSITION {actuator.servo_id}"
            location = actuator.send_command(command, expect_response=True)
            if location:
                try:
                    return int(location)
                except ValueError:
                    _logger.error(f"위치 값을 정수로 변환 실패: {location}")
                    return None
        _logger.error("보드-시리얼이 연결되어 있지 않음(혹은 전압이 부족함)")
        return None
                     
    def actuator_home(self):
        """ 액추에이터 원점 이동 """
        selected_port = self.ui.BoardComboBox.currentText()
        actuator = self._get_actuator_by_port(selected_port)
        if actuator:
            actuator.send_command(f"SET_POSITION {actuator.servo_id} 0", expect_response=False)
            # self.start_position_updater(selected_port)
            updated_position = self._get_position(actuator)  # 위치 업데이트
            self._update_jogloc_label(updated_position)      # Label에 업데이트
        else:
            _logger.error("선택된 포트(보드)가 없음")
    
    # def actuator_fwd(self):
    #     """액추에이터 위치 증가"""
    #     selected_port = self.ui.BoardComboBox.currentText()
    #     actuator = self._get_actuator_by_port(selected_port)
    #     if actuator:
    #         current_position = self._get_position(actuator)
    #         if current_position is not None:
    #             new_position = min(current_position + self.step_size, DEFAULT_VALUES["long_limit"])
    #             actuator.send_command(f"SET_POSITION {actuator.servo_id} {new_position}", expect_response=False)
    #             self.start_position_updater(selected_port)
    #             # updated_position = self._get_position(actuator)  # 위치 업데이트
    #             # self._update_jogloc_label(updated_position)  # Label에 업데이트
    #     else:
    #         _logger.error("선택된 액추에이터 없음")

    # def actuator_bwd(self):
    #     """액추에이터 위치 감소"""
    #     selected_port = self.ui.BoardComboBox.currentText()
    #     actuator = self._get_actuator_by_port(selected_port)
    #     if actuator:
    #         current_position = self._get_position(actuator)
    #         if current_position is not None:
    #             new_position = max(current_position - self.step_size, DEFAULT_VALUES["short_limit"])
    #             actuator.send_command(f"SET_POSITION {actuator.servo_id} {new_position}", expect_response=False)
    #             self.start_position_updater(selected_port)
    #             # updated_position = self._get_position(actuator)  # 위치 업데이트
    #             # self._update_jogloc_label(updated_position)      # Label에 업데이트
    #     else:
    #         _logger.error("[디버깅] 선택된 액추에이터 없음")    
    
    # def start_position_updater(self, port):
    #     """위치 업데이트 쓰레드 시작"""
    #     if not hasattr(self, "position_updater"):
    #         self.position_updater = PositionUpdater(self.actuators)
    #         self.position_updater.position_updated.connect(self._update_jogloc_label)

    #     self.position_updater.set_target_port(port)
    #     if not self.position_updater.isRunning():
    #         self.position_updater.start()
    #         _logger.info("PositionUpdater 쓰레드 시작")

    # def stop_position_updater(self):
    #     """위치 업데이트 쓰레드 정지"""
    #     if hasattr(self, "position_updater") and self.position_updater.isRunning():
    #         self.position_updater.stop()
    #         _logger.info("PositionUpdater 쓰레드 정지")
           
    # def update_step_size(self):
    #     """스텝 크기를 업데이트"""
    #     self.step_size = self.ui.StepSpinBox.value()
    #     _logger.info(f"스텝 크기 변경: {self.step_size}")


    def slider_position_changed(self, value):
        """슬라이더 값 변경 이벤트"""
        selected_port = self.ui.BoardComboBox.currentText()
        actuator = self._get_actuator_by_port(selected_port)
        if actuator:
            self.last_slider_position = value
            self.is_slider_moving = True
            self._update_jogloc_label(value)  # UI 업데이트
            if not self.slider_timer.isActive():
                self.slider_timer.start()  # 슬라이더 타이머 시작

    def update_position_from_slider(self):
        """슬라이더 값에 따라 액추에이터 위치 설정"""
        selected_port = self.ui.BoardComboBox.currentText()
        actuator = self._get_actuator_by_port(selected_port)
        if actuator and self.last_slider_position is not None:
            actuator.send_command(
                f"SET_POSITION {actuator.servo_id} {self.last_slider_position}",
                expect_response=False
            )
            _logger.info(f"슬라이더 동작으로 액추에이터 위치 설정: {self.last_slider_position}")
        self.is_slider_moving = False
        self.slider_timer.stop()  # 타이머 정지


    def save_setup(self):
        """설정 저장"""
        try:
            self.position1 = int(self.ui.Pos1LineEdit.text())
            self.position2 = int(self.ui.Pos2LineEdit.text())
            self.push_counts = int(self.ui.PushCountLineEdit.text())
            _logger.info(f"입력된 설정값 저장 완료: 포지션1={self.position1}, 포지션2={self.position2}, 왕복 횟수={self.push_counts}")
            QMessageBox.information(self, "Alert", "Settings have been saved.")
            self.actuator_home()
        except ValueError:
            _logger.error("입력된 설정값 저장 실패: 입력값이 잘못되었습니다.")
            QMessageBox.critical(self, "Alert", "Invalid settings.")

    def reset_setup(self):
        """ 전체 설정 초기화 """
        self.position1, self.position2, self.test_counts, self.push_counts, self.complete_counts = 0, 0, 0, 0, 0
        self.ui.Pos1LineEdit.clear()
        self.ui.Pos2LineEdit.clear()
        self.ui.PushCountLineEdit.clear()
        _logger.info("설정 초기화 완료")
        QMessageBox.warning(self, "Alert", "All settings have been reset.")
    
    def fetch_actuator_settings(self, actuator):
        """ GET_INFO 명령으로 액추에이터 설정값 가져오기 """
        settings = {}
        if actuator and actuator.serial_obj and actuator.serial_obj.is_open:
            try:
                # GET_INFO 명령어 전송
                actuator.serial_obj.write(f"GET_INFO {actuator.servo_id}\n".encode())
                line = actuator.serial_obj.readline().decode().strip()  # 한 줄 데이터 수신
                _logger.debug(f"Received GET_INFO data: {line}")

                # 콤마(,)로 구분된 데이터 파싱
                entries = line.split(',')
                for entry in entries:
                    key_value = entry.split(' ')
                    if len(key_value) == 2:  # "키 값" 형태
                        key, value = key_value
                        settings[key] = value
            except Exception as e:
                _logger.error(f"Error fetching actuator settings: {e}")
        return settings
    
    def update_ui_with_actuator_settings(self):
        """ GET_INFO로 가져온 반영구 저장 값을 UI에 업데이트 """
        selected_port = self.ui.BoardComboBox.currentText()
        actuator = next((act for act in self.actuators if act.port == selected_port), None)

        if actuator:
            settings = self.fetch_actuator_settings(actuator)
            if settings:  # 가져온 설정값이 있을 경우에만 업데이트
                self.ui.SpeedLimitLineEdit.setText(settings.get("SPL", ""))
                self.ui.CurrentLimitLineEdit.setText(settings.get("CRL", ""))
                self.ui.ShortLimitLineEdit.setText(settings.get("SSL", ""))
                self.ui.LongLimitLineEdit.setText(settings.get("LSL", ""))
                self.ui.AccLineEdit.setText(settings.get("ACC", ""))
                self.ui.DecLineEdit.setText(settings.get("DEC", ""))
            else:
                _logger.warning(f"Unable to fetch settings for port: {selected_port}")
        else:
            QMessageBox.warning(self, "Warning", "No actuator selected.")

    
    def monitor_serial_data(self):
        """아두이노에서 오는 시리얼 데이터 처리"""
        for actuator in self.actuators:
            serial_obj = actuator.serial_obj
            if serial_obj and serial_obj.is_open and serial_obj.in_waiting > 0:
                try:
                    command = serial_obj.readline().strip().decode()
                    _logger.debug(f"[monitor_serial_data] ({actuator.port}) 수신 명령: {command}")
                    if command == "TEST":
                        label = self.actuator_ui_map.get(actuator, {}).get("complete_count_label")
                        if label:
                            self.test_start(actuator, label)
                        else:
                            _logger.error(f"{actuator.port}: UI 매핑된 label이 없습니다.")
                    else:
                        _logger.warning(f"{actuator.port}: 알 수 없는 명령어 -> {command}")
                except UnicodeDecodeError:
                    _logger.error(f"{actuator.port}: 수신 데이터 디코딩 실패")

    
    def test_start(self, actuator, label):
        """테스트 시작"""
        _logger.info(f"테스트 시작: {actuator.port}")
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
        # 작업이 취소된 상태라면 완료 횟수 업데이트 생략
        if actuator not in self.workers:
            _logger.info(f"{actuator.port} 작업 취소됨, 완료 횟수 업데이트 생략")
            return
        
        actuator.complete_count += 1
        label.setText(f"{actuator.complete_count}")
        _logger.info(f"{actuator.port} 완료 횟수: {actuator.complete_count}")

    def reset_count(self, actuator, label):
        """ 완료 횟수 초기화 """
        actuator.complete_count = 0
        label.setText("0")
        _logger.info(f"{actuator.port} 완료 횟수 초기화")
        
        # 현재 워커가 실행 중이라면 취소
        if actuator in self.workers:
            self.workers[actuator].cancel()  # 작업 취소
            self.workers[actuator].wait()   # 워커 종료 대기
            del self.workers[actuator]      # 워커 제거
        
        # 액추에이터를 원점으로 이동
        try:
            actuator.send_command(f"SET_POSITION {actuator.servo_id} 0", expect_response=False)  # 원점으로 이동
            _logger.info(f"{actuator.port} 원점 이동 완료")
        except Exception as e:
            _logger.error(f"{actuator.port} 원점 이동 실패: {e}")
        
    def cleanup_worker(self, actuator):
        """ 작업자 정리 """
        if actuator in self.workers:
            _logger.info(f"{actuator.port} 작업자 정리")
            self.workers[actuator].quit()
            self.workers[actuator].wait()
            del self.workers[actuator]
        
    def _get_actuator_by_port(self, port):
        """현재 선택된 포트에 해당하는 액추에이터 반환"""
        return next((act for act in self.actuators if act.port == port), None)
        
    def save_all_settings(self):
        """ 저장된 설정을 액추에이터에 반영 """
        selected_port = self.ui.BoardComboBox.currentText()
        actuator = next((act for act in self.actuators if act.port == selected_port), None)

        if actuator:
            try:
                actuator.send_command(f"SET_SPEEDLIMIT {actuator.servo_id} {self.ui.SpeedLimitLineEdit.text()}")
                actuator.send_command(f"SET_CURRENTLIMIT {actuator.servo_id} {self.ui.CurrentLimitLineEdit.text()}")
                actuator.send_command(f"SET_SHORTLIMIT {actuator.servo_id} {self.ui.ShortLimitLineEdit.text()}")
                actuator.send_command(f"SET_LONGLIMIT {actuator.servo_id} {self.ui.LongLimitLineEdit.text()}")
                actuator.send_command(f"SET_ACCEL {actuator.servo_id} {self.ui.AccLineEdit.text()}")
                actuator.send_command(f"SET_DECEL {actuator.servo_id} {self.ui.DecLineEdit.text()}")
                QMessageBox.information(self, "Info", "Settings saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No actuator selected.")

    def reset_to_defaults(self):
        """기본값으로 초기화"""
        selected_port = self.ui.BoardComboBox.currentText()
        actuator = next((act for act in self.actuators if act.port == selected_port), None)
        if not actuator:
            QMessageBox.warning(self, "Alert", "No actuator selected or connected.")
            return
        try:
            # DEFAULT_VALUES 사용하여 LineEdit 초기화
            self.ui.SpeedLimitLineEdit.setText(str(DEFAULT_VALUES["speed_limit"]))
            self.ui.SpeedTempLineEdit.setText(str(DEFAULT_VALUES["speed"]))
            self.ui.CurrentLimitLineEdit.setText(str(DEFAULT_VALUES["current_limit"]))
            self.ui.CurrentTempLineEdit.setText(str(DEFAULT_VALUES["current"]))
            self.ui.ShortLimitLineEdit.setText(str(DEFAULT_VALUES["short_limit"]))
            self.ui.LongLimitLineEdit.setText(str(DEFAULT_VALUES["long_limit"]))
            self.ui.AccLineEdit.setText(str(DEFAULT_VALUES["accel"]))
            self.ui.DecLineEdit.setText(str(DEFAULT_VALUES["decel"]))
            
            # DEFAULT_VALUES 사용하여 초기화
            actuator.send_command(f"SET_SPEEDLIMIT {actuator.servo_id} {DEFAULT_VALUES['speed_limit']}")
            actuator.send_command(f"SET_SPEED {actuator.servo_id} {DEFAULT_VALUES['speed']}")
            actuator.send_command(f"SET_CURRENTLIMIT {actuator.servo_id} {DEFAULT_VALUES['current_limit']}")
            actuator.send_command(f"SET_CURRENT {actuator.servo_id} {DEFAULT_VALUES['current']}")
            actuator.send_command(f"SET_SHORTLIMIT {actuator.servo_id} {DEFAULT_VALUES['short_limit']}")
            actuator.send_command(f"SET_LONGLIMIT {actuator.servo_id} {DEFAULT_VALUES['long_limit']}")
            actuator.send_command(f"SET_ACCEL {actuator.servo_id} {DEFAULT_VALUES['accel']}")
            actuator.send_command(f"SET_DECEL {actuator.servo_id} {DEFAULT_VALUES['decel']}")
            
            QMessageBox.information(self, "Info", "All settings have been reset to defaults!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset settings: {e}")
            
    def closeEvent(self, event):
        """ 창 닫기 시 쓰레드 정리 """
        # self.stop_position_updater()
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
