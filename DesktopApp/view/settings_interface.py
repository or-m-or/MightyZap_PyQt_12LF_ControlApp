import resource_rc
import serial, re
from serial.tools import list_ports
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, QComboBox, QFrame
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy

from qfluentwidgets import (
    SettingCardGroup, 
    SwitchSettingCard, 
    FolderListSettingCard,
    OptionsSettingCard, 
    PushSettingCard,
    HyperlinkCard, 
    PrimaryPushSettingCard, 
    ScrollArea,
    ComboBoxSettingCard, 
    ExpandLayout, 
    Theme,
    CustomColorSettingCard,             
    setTheme, 
    RangeSettingCard, 
    isDarkTheme,
    InfoBar,
    SpinBox,
    Flyout,
    InfoBarIcon,
    ExpandGroupSettingCard, 
    PrimaryPushButton, 
    PushButton, 
    SettingCard,
    OptionsValidator,
    OptionsConfigItem, 
    MessageBox,
    LineEdit, 
    BodyLabel, 
    ListWidget,
    qconfig,
    FluentIcon,
    FluentIcon as FIF
) 
from core.config import cfg, setup_logger, HELP_URL
from core.signal_bus import signalBus
from core.style_sheet import StyleSheet
from core.actuator import Actuator
from components.combobox_card import CustomComboBoxCard
from components.combobox_button_card import CustomComboBoxButtonCard, CustomComboBoxTwoButtonCard
from components.lineedit_card import CustomLineEditCard
from components.spinbox_card import CustomSpinBoxCard
from components.board_setting_card import BoardSettingCard
from components.jog_setting_card import JogSettingCard
from components.actuator_setting_card import ActuatorSettingCard

_logger = setup_logger(name="MainApp", level='INFO')


class SettingInterface(ScrollArea):
    """ 설정 인터페이스 클래스 """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.default_servo_id = 0 # 서보 ID 기본지정 값
        self.actuators = [] # 액추에이터 리스트
        self.last_slider_position = None # 슬라이더 마지막 위치
        self.__initui()
 
    def __initui(self):    
        self.scrollWidget = QWidget()                          # 스크롤 가능한 메인 위젯 생성
        self.expandLayout = ExpandLayout(self.scrollWidget)    # 확장 가능한 레이아웃 생성
        self.expandLayout.setSpacing(5)                       # 카드 간 간격
        self.expandLayout.setContentsMargins(20, 40, 20, 20)   # 전체 여백 설정

        self.settingLabel = QLabel(self.tr("Setup"), self) # "설정" 라벨
        
        self.boardSettingCard = BoardSettingCard(self.scrollWidget) # 보드 설정 카드 추가
        self.jogSettingCard = JogSettingCard(cfg, self.scrollWidget) # 조그 및 테스트 설정 카드 추가
        self.actuatorSettingCard = ActuatorSettingCard(cfg, self.scrollWidget) # 액추에이터 설정 카드
        
                
        # # [ 저장 및 초기화 ]
        self.SaveResetGroup = SettingCardGroup(self.tr(''), self.scrollWidget)
        # Apply 버튼
        self.applyButtonCard = PrimaryPushSettingCard(
            icon=FIF.SAVE,
            title=self.tr("Apply Settings"),
            content=self.tr("Apply current settings to the actuator."),
            text=self.tr("Apply"),
            parent=self.SaveResetGroup
        )
        # Reset 버튼
        self.resetButtonCard = PrimaryPushSettingCard(
            icon=FIF.ROTATE,
            title=self.tr("Reset All Settings"),
            content=self.tr("This will reset all settings to their default values."),
            text=self.tr("Reset"),
            parent=self.SaveResetGroup
        )
       
        # [ 개인 설정 ]
        # self.PersonalGroup = SettingCardGroup( self.tr('Personalization'), self.scrollWidget )
        # # 테마 선택 기능 필요 시 주석해제
        # self.themeCard = OptionsSettingCard(
        #     cfg.themeMode,  # 현재 테마
        #     FIF.BRUSH, 
        #     self.tr('Theme'),  
        #     self.tr("Change the color of an application"), 
        #     texts=[
        #         self.tr('Light'), self.tr('Dark'), self.tr('Use system setting')
        #     ],
        #     parent=self.PersonalGroup
        # )
        # 언어 설정
        # self.languageCard = ComboBoxSettingCard(
        #     cfg.language,  # 현재 언어 설정
        #     FIF.LANGUAGE,  
        #     self.tr('Language'),  
        #     self.tr('Set your preferred language'),  
        #     texts=['Korean', 'English', self.tr('Use system setting')],  
        #     parent=self.PersonalGroup
        # )
        self.__initWidget()  # 위젯 초기화
        
    def __initWidget(self):
        """ 설정 인터페이스 전체 위젯 초기화 """
        self.resize(1000, 800)  # 창 크기
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 가로 스크롤 비활성화
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setViewportMargins(0, 80, 0, 20)   # 뷰포트 여백
        self.setWidget(self.scrollWidget)       # 스크롤 위젯
        self.setWidgetResizable(True)           # 창 크기 변경 허용
        self.setObjectName('settingInterface')  # 객체 이름 설정

        # 스타일시트 적용
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # 레이아웃 초기화
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ 레이아웃 초기화 """
        self.settingLabel.move(36, 30)  # 설정 라벨 위치 설정 (좌측 상단)

        # 개별 카드(코드 위치 변경 X)
        self.SaveResetGroup.addSettingCard(self.applyButtonCard)  # Save
        self.SaveResetGroup.addSettingCard(self.resetButtonCard)  # Reset
        # self.PersonalGroup.addSettingCard(self.themeCard)       # 테마 선택 기능 필요 시 주석 해제
        
        # 그룹 카드
        self.expandLayout.addWidget(self.boardSettingCard)    # 기기 설정
        self.expandLayout.addWidget(self.jogSettingCard)      # 조그 및 테스트 설정
        self.expandLayout.addWidget(self.actuatorSettingCard) # 액추에이터 설정
        
        # 여백 추가 (위쪽, 아래쪽)
        self.expandLayout.addWidget(self.SaveResetGroup)      # [Danger]

        # 스크롤 위젯 높이 동기화
        self.scrollWidget.setMinimumHeight(self.expandLayout.sizeHint().height())

        # self.expandLayout.addWidget(self.SaveResetGroup)        # [Danger]
        
        
    def __connectSignalToSlot(self):
        """ 시그널과 슬롯 연결 """
        cfg.appRestartSig.connect(self.__showRestartTooltip)  # 설정 변경 시, 재 시작 알림 표시
        
        # 보드 설정 관련 시그널
        self.boardSettingCard.searchRequested.connect(self.__searchDevices)
        self.boardSettingCard.deviceSelected.connect(self.__onDeviceSelected)
        self.boardSettingCard.connectRequested.connect(self.__onConnectClicked)
        self.boardSettingCard.disconnectRequested.connect(self.__onDisconnectClicked)
        
        # 조그 설정 관련 시그널
        self.jogSettingCard.positionChanged.connect(self.__actuator_position_changed)  # 슬라이더 값 변경
        self.jogSettingCard.homeRequested.connect(self.__actuator_position_home)  # 홈 버튼 클릭
        self.jogSettingCard.position1Updated.connect(self.__onPosition1Updated)  # 포지션1 값 변경
        self.jogSettingCard.position2Updated.connect(self.__onPosition2Updated)  # 포지션2 값 변경
        self.jogSettingCard.testCountUpdated.connect(self.__onTestCountUpdated)  # 테스트 횟수 변경
                    
        # # Reset 및 Apply 버튼
        self.applyButtonCard.clicked.connect(self.__onApplyClicked)  # [Apply 버튼]
        self.resetButtonCard.clicked.connect(self.__onResetClicked) # [Reset 버튼]
        # cfg.themeChanged.connect(setTheme)  # [Personal] 테마 변경 시 즉시 적용
    
    def __showRestartTooltip(self):
        """ 설정 변경 직후 , 재시작 알림 표시 """
        InfoBar.success(
            self.tr('Updated successfully'),  
            self.tr('Configuration takes effect after restart'),  # "설정은 재시작 후 적용됨"
            duration=1500,  # 표시 시간 (1.5초)
            parent=self
        )
           
    # [ Board ] ####################################################################################
    def __searchDevices(self):
        """ [Search 버튼] 사용 가능한 포트 검색 및 콤보박스 업데이트 """
        ports = list_ports.comports()                     # 연결된 모든 포트와 상세 정보 가져오기
        device_lists = [port.description for port in ports] # 포트 이름 리스트 생성
        
        if not device_lists:
            device_lists = ["No ports found"]
        
        # UI 콤보박스에 새 옵션 업데이트
        self.boardSettingCard.deviceComboBox.clear()
        self.boardSettingCard.deviceComboBox.addItems(device_lists)
        # self.searchDeviceCard.setOptions(device_lists)
        _logger.info(f"[Setting] 발견된 포트 목록: {device_lists}")

    def __onDeviceSelected(self, device):
        """ [Port 콤보박스] 포트 값 변경 시 알림 창 생성 """
        _logger.info(f"Selected port: {device}")

        # Flyout 생성
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,  
            title='Alert',  
            content=f"device has changed!",  
            target=self.boardSettingCard.deviceComboBox, # portcard 위젯 위에 생성
            parent=self,    # 부모 위젯 설정
            isClosable=True # 닫기 버튼 활성화
        )
            
    def __onConnectClicked(self, device):
        """ [Connect 버튼] PC-보드 연결 """
        selected = self.boardSettingCard.deviceComboBox.currentText()
        match = re.search(r'\((.*?)\)', selected)        
        if not match:
            MessageBox("Error", "Invalid device format. Unable to connect.", self).exec()
            return
            
        baud = self.boardSettingCard.baudrateComboBox.currentText()
        port = match.group(1)
        
        # 선택된 보드 X 경우 예외처리
        if not selected or selected == "No devices found":
            MessageBox('Error', "No device selected. Please search and select a device.", self).exec()
            return
        
        # 모든 기기가 이미 연결된 경우 알림 표시
        if len(self.actuators) >= 2:
            MessageBox('Notice', "All devices are already connected.", self).exec()
            return
        
        try:
            serial_obj = serial.Serial(port, int(baud), timeout=0.2)
            actuator = Actuator(
                servo_id=self.default_servo_id,
                serial_obj=serial_obj,
                baudrate=baud,
                port=port
            )
            self.actuators.append(actuator) # Actuator 리스트에 추가
            
            # UI 업데이트: 연결된 보드 정보를 ComboBox에 추가
            self.boardSettingCard.connectionComboBox.addItem(f"{selected} ({baud})")
            
            # 슬라이더 및 실제 액추에이터 0 위치로 초기화
            actuator.send_command(f"SET_POSITION {actuator.servo_id} 0", expect_response=False)  # 액추에이터 초기 위치 설정
            self.jogSettingCard.slider.setValue(0) # 슬라이더를 초기 위치(0)로 설정
            self.last_slider_position = 0  # 내부 슬라이더 상태 초기화
            
            # SignalBus로 다른 인터페이스에 업데이트 알림
            signalBus.devicesUpdated.emit()  # TestInterface 업데이트 알림
        
            # 성공 메시지 및 로그
            _logger.info(f"보드 연결 성공 => 포트: {selected}, 보드레이트: {baud}")
            MessageBox("Alert", f"Connection Successful!\nYou are connected to {selected}.", self).exec()
        except PermissionError:
            _logger.warning(f"{selected}가 사용 중이거나, 이미 연결됨 (PermissionError)")
            MessageBox("Error", f"Device {selected} is already used.", self).exec()                
        except Exception as e:
            _logger.error(f"포트 {selected} 연결 실패: {e}")
            MessageBox("Error", f"Connection Failed : {selected}", self).exec()
                   
    def __onDisconnectClicked(self):
        """ 보드 연결 해제 """    
        selected = self.boardSettingCard.connectionComboBox.currentText()  # 선택된 장치 정보 가져오기

        if not selected:
            MessageBox("Alert", "No device selected to disconnect.", self).exec()
            return

        # 포트와 Baudrate를 추출
        match = re.match(r"(.*) \((\d+)\)", selected)
        if not match:
            MessageBox("Error", "Invalid device format. Unable to disconnect.", self).exec()
            return
        
        name_port, baudrate = match.groups()
        port = re.search(r'\((.*?)\)', name_port).group(1)
        
        # Actuator 찾기
        actuator = next((act for act in self.actuators if act.port == port and str(act.baudrate) == baudrate), None)

        if actuator:
            try:
                # Serial 연결 해제
                actuator.serial_obj.close()
                self.actuators.remove(actuator)  # 내부 리스트에서 제거

                # UI 업데이트: 연결된 장치를 ComboBox에서 제거
                self.boardSettingCard.connectionComboBox.removeItem(
                    self.boardSettingCard.connectionComboBox.currentIndex()
                )

                # 슬라이더 및 기타 상태 초기화
                self.jogSettingCard.slider.setValue(0)
                self.last_slider_position = 0

                # SignalBus로 상태 업데이트
                signalBus.devicesUpdated.emit()

                # 성공 메시지 및 로그
                _logger.info(f"Disconnected device: {port} at {baudrate} baud")
                MessageBox("Alert", f"Disconnected from {port}.", self).exec()

            except Exception as e:
                # 연결 해제 실패 시 에러 처리
                _logger.error(f"Error disconnecting device {port}: {e}")
                MessageBox("Error", f"Failed to disconnect {port}.\n{str(e)}", self).exec()

        else:
            # 해당 Actuator를 찾지 못했을 경우
            MessageBox("Alert", f"No connected device found for {selected}.", self).exec()

    def getConnectedDevices(self):
        """현재 연결된 장치 목록 반환"""
        return self.actuators  # self.actuators에 저장된 연결된 액추에이터 리스트를 반환        
            
    # [ JOG ] ####################################################################################
    def __get_actuator_by_port(self, port):
        """ 현재 선택된 포트에 해당하는 액추에이터 반환 """
        return next((act for act in self.actuators if act.port == port), None)

    def __actuator_position_changed(self, value):
        """ 슬라이더 값에 따른 액추에이터 위치 변경 """
        selected = self.boardSettingCard.deviceComboBox.currentText()  # 현재 선택된 보드 가져오기
        match = re.search(r'\((.*?)\)', selected)        
        if not match:
            # 연결된 액추에이터 없으면 무시
            return
        
        port = match.group(1)
        actuator = self.__get_actuator_by_port(port)
        if actuator:
            try:
                # SET_POSITION 명령 전송
                actuator.send_command(f"SET_POSITION {actuator.servo_id} {value}", expect_response=False)
                _logger.info(f"슬라이더 위치로 액추에이터 이동: {value}")
            except Exception as e:
                _logger.error(f"액추에이터 명령 전송 실패: {e}")
        else:
            _logger.warning("슬라이더 값을 전송할 액추에이터가 없습니다.")
    
    def __actuator_position_home(self):
        """  액추에이터 원점 이동 """
        selected = self.boardSettingCard.deviceComboBox.currentText()
        match = re.search(r'\((.*?)\)', selected)        
        if not match:
            MessageBox("Error", "Invalid device format. Unable to connect.", self).exec()
            return
            
        port = match.group(1)
        actuator = self.__get_actuator_by_port(port)
        if actuator:
            actuator.send_command(f"SET_POSITION {actuator.servo_id} 0", expect_response=False)
            self.jogSettingCard.slider.setValue(0)
            self.last_slider_position = 0
        else:
            _logger.error("선택된 포트(보드)가 없음")
    
    def __onPosition1Updated(self, value):
        """ 포지션1 값 변경 시 호출 """
        _logger.info(f"Position 1 updated to: {value}")
        cfg.position1.value = value  # Config에 값 업데이트

    def __onPosition2Updated(self, value):
        """ 포지션2 값 변경 시 호출 """
        _logger.info(f"Position 2 updated to: {value}")
        cfg.position2.value = value  # Config에 값 업데이트

    def __onTestCountUpdated(self, value):
        """ 테스트 횟수 값 변경 시 호출 """
        _logger.info(f"Test Count updated to: {value}")
        cfg.push_counts.value = value  # Config에 값 업데이트
    
    
    def __onResetClicked(self):
        """ Reset 버튼 클릭 시 호출 """
        _logger.info("Resetting all settings to default values.")

        # 설정 초기화 (기본값으로 설정)
        cfg.position1.value = cfg.position1.defaultValue  # Reset Position1
        cfg.position2.value = cfg.position2.defaultValue  # Reset Position2
        cfg.push_counts.value = cfg.push_counts.defaultValue  # Reset PushCounts
        cfg.global_speed.value = cfg.global_speed.defaultValue  # Reset GlobalSpeed
        cfg.bwd_limit.value = cfg.bwd_limit.defaultValue  # Reset BackwardLimit
        cfg.fwd_limit.value = cfg.fwd_limit.defaultValue  # Reset ForwardLimit

        # UI 업데이트
        self.jogSettingCard.position1Input.setText(str(cfg.position1.value))
        self.jogSettingCard.position2Input.setText(str(cfg.position2.value))
        self.jogSettingCard.testCountSpinBox.setValue(cfg.push_counts.value)
        self.actuatorSettingCard.globalSpeedSpinBox.setValue(cfg.global_speed.value)
        self.actuatorSettingCard.backwardLimitSpinBox.setValue(cfg.bwd_limit.value)
        self.actuatorSettingCard.forwardLimitSpinBox.setValue(cfg.fwd_limit.value)

        # 즉시 저장
        qconfig.save()
        
        # 초기화 후 저장 동작 수행
        self.__onApplyClicked()
        MessageBox('Warning', "All settings have been reset to default values and applied to the actuator.", self).exec()

    def __onApplyClicked(self):
        _logger.info("Applying settings to the actuator.")
       
        """ 저장된 설정을 액추에이터에 반영 """
        selected = self.boardSettingCard.deviceComboBox.currentText()
        match = re.search(r'\((.*?)\)', selected)        
        if not match:
            MessageBox("Error", "Invalid device format. Unable to connect.", self).exec()
            return
            
        port = match.group(1)
        actuator = next((act for act in self.actuators if act.port == port), None)

        if actuator:
            try:
                actuator.send_command(f"SET_SPEEDLIMIT {actuator.servo_id} {cfg.global_speed.value}")
                actuator.send_command(f"SET_SHORTLIMIT {actuator.servo_id} {cfg.bwd_limit.value}")
                actuator.send_command(f"SET_LONGLIMIT {actuator.servo_id} {cfg.fwd_limit.value}")
                
                InfoBar.success(
                    self.tr("Applied Successful"),
                    self.tr("Settings saved and applied successfully."),
                    duration=2000,
                    parent=self
                )
            except Exception as e:
                MessageBox("Error", f"Failed to apply settings: {e}", self).exec()
        else:
            MessageBox("Warning", "No actuator selected.", self).exec()
