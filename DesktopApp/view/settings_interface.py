"""
설정 박스 그룹 박스로 일괄 변경 필요
"""
import resource_rc
import serial, re
from serial.tools import list_ports
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, QComboBox
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
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(20, 40, 20, 20)   # 전체 여백 설정

        self.settingLabel = QLabel(self.tr("Setup"), self) # "설정" 라벨
        
        # [ 보드 설정 그룹 ] 초기화
        self.BoardSettingGroup = SettingCardGroup(self.tr("Board Setting"), self.scrollWidget)        
        
        # Device 검색 버튼 + 선택 콤보박스
        self.searchDeviceCard = CustomComboBoxButtonCard(
            icon=FIF.CONNECT,
            title=self.tr("Select a Device"),
            content=self.tr("Search and select a serial device to connect"),
            items=["No devices detected."],
            combobox_width=300,
            button_width=80,
            button_text="Search",
            # configItem=cfg.port,
            parent=self.BoardSettingGroup,
        )        
        # Device Baudrate 선택 콤보박스
        self.baudrateCard = ComboBoxSettingCard(
            icon=FIF.SPEED_HIGH,
            title=self.tr("Baudrate"),
            content=self.tr("Select the serial communication speed between your device and PC."),
            texts=["9600", "19200", "57600", "115200"],
            configItem=cfg.baudrate,
            parent=self.BoardSettingGroup
        )
        # Connect 버튼 + 콤보박스
        self.connectDeviceCard = CustomComboBoxTwoButtonCard(
            icon=FIF.CHEVRON_DOWN_MED,
            title=self.tr("Connect to Device"),
            content=self.tr("Attempts to connect with the selected device."),
            items=["No devices are connected."],
            combobox_width=180,
            button_width=100,
            button1_text="Connect",
            button2_text="Disconnect",
            parent=self.BoardSettingGroup,
        )         
        

        # [ 조그 설정 그룹 ]
        self.JogSettingGroup = SettingCardGroup(self.tr("Jog Setting"), self.scrollWidget)
        # 조그 이동 슬라이더
        self.rangeSettingCard = RangeSettingCard(
            icon=FIF.CARE_RIGHT_SOLID,            
            title=self.tr("Acuator Location (0~4095)"),
            content=self.tr("You can move the slider to move the actuator."),
            configItem=cfg.rangeValue,  # Config에서 정의된 값 사용
            parent=self.JogSettingGroup,
        )
        # Home 버튼
        self.homeButtonCard = PushSettingCard(
            icon=FIF.HOME,
            title=self.tr("Return Home"),
            content=self.tr("Reset the location to the home point."),
            text=self.tr("Home"),
            parent=self.JogSettingGroup
        )
        # position 1 라인박스
        self.position1Card = CustomLineEditCard(
            icon=FIF.LEFT_ARROW,
            title="Pos 1 (0~4095)",
            content="Enter the starting point for the Actuator behavior.",
            placeholder="Position 1",
            configItem=cfg.position1,
            parent=self.JogSettingGroup
        )
        # position 2 라인박스
        self.position2Card = CustomLineEditCard(
            icon=FIF.RIGHT_ARROW,
            title="Pos 2 (0~4095)",
            content="Enter the arrival point for the Actuator behavior.",
            placeholder="Position 2",
            configItem=cfg.position2,
            parent=self.JogSettingGroup
        )
        
        
        # [ 테스트 설정 그룹 ]
        self.TestSettingGroup = SettingCardGroup(self.tr("Test Setting"), self.scrollWidget)        
        # 테스트 횟수
        self.testCountCard = CustomSpinBoxCard(
            icon=FIF.ROTATE,
            title="Test Counts",
            content="Enter the number of repetitions for the test.",
            minimum=0,
            maximum=100000,
            default=0,
            configItem=cfg.push_counts,
            parent=self.JogSettingGroup
        )
        
        
        # [ 액추에이터 설정 그룹 ]
        self.ActuatorSettingGroup = SettingCardGroup(self.tr("Actuator Setting"), self.scrollWidget)
        # 반영구 속도 설정
        self.globalSpeedSettingCard = CustomSpinBoxCard(
            icon=FIF.SETTING,
            title=self.tr("General Speed Limit (0~1023)"),
            content=self.tr("Set the speed of the actuator (0-1023) (this setting is semi-permanently stored in the actuator)."),
            minimum=0,
            maximum=1023,
            default=cfg.global_speed.value,
            configItem=cfg.global_speed,
            parent=self.ActuatorSettingGroup
        )

        # # 임시 속도 설정
        # self.tempSpeedSettingCard = CustomSpinBoxCard(
        #     icon=FIF.SETTING,
        #     title=self.tr("Temp Speed Limit"),
        #     content=self.tr("Set the speed of the actuator (0-1023) (this setting is reset on device restart)."),
        #     minimum=0,
        #     maximum=1023,
        #     default=cfg.temp_speed.value,
        #     configItem=cfg.temp_speed,
        #     parent=self.ActuatorSettingGroup
        # )

        # 후진 제한값 설정
        self.bwdLimitSettingCard = CustomSpinBoxCard(
            icon=FIF.SETTING,
            title=self.tr("BWD Limit"),
            content=self.tr("Sets the maximum travel limit for the actuator in the reverse direction."),
            minimum=0,
            maximum=4095,
            default=cfg.bwd_limit.value,
            configItem=cfg.bwd_limit,
            parent=self.ActuatorSettingGroup
        )

        # 전진 제한값 설정
        self.fwdLimitSettingCard = CustomSpinBoxCard(
            icon=FIF.SETTING,
            title=self.tr("FWD Limit"),
            content=self.tr("Sets the maximum travel limit for the actuator in the forward direction."),
            minimum=0,
            maximum=4095,
            default=cfg.fwd_limit.value,
            configItem=cfg.fwd_limit,
            parent=self.ActuatorSettingGroup
        )

        
        # [ 저장 및 초기화 ]
        self.SaveResetGroup = SettingCardGroup(self.tr('Danger'), self.scrollWidget)
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
        self.PersonalGroup = SettingCardGroup( self.tr('Personalization'), self.scrollWidget )
        # 테마 선택
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,  # 현재 테마
            FIF.BRUSH, 
            self.tr('Theme'),  
            self.tr("Change the color of an application"), 
            texts=[
                self.tr('Light'), self.tr('Dark'), self.tr('Use system setting')
            ],
            parent=self.PersonalGroup
        )
        # # 인터페이스 확대/축소
        # self.zoomCard = OptionsSettingCard(
        #     cfg.dpiScale,  # DPI 설정
        #     FIF.ZOOM,  
        #     self.tr("Interface zoom"),  
        #     self.tr("Change the size of widgets and fonts"), 
        #     texts=[
        #         "100%", "125%", "150%", "175%", "200%",  
        #         self.tr("Use system setting")            
        #     ],
        #     parent=self.personalGroup
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

        # # [ 앱 정보 ]
        # self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)  # "정보" 그룹
        # # 도움말 하이퍼링크
        # self.helpCard = HyperlinkCard(
        #     HELP_URL,                   # 도움말 URL
        #     self.tr('Open help page'),  
        #     FIF.HELP,                   
        #     self.tr('Help'),            
        #     self.tr('Check out 0000 how-to guide'),  # 설명
        #     self.aboutGroup
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

        # 카드 -> 그룹
        self.BoardSettingGroup.addSettingCard(self.searchDeviceCard) # [Board]-[Port 콤보박스 + Search 버튼]
        self.BoardSettingGroup.addSettingCard(self.baudrateCard)           # [Board]-[Baudrate 콤보박스]
        self.BoardSettingGroup.addSettingCard(self.connectDeviceCard)         # [Board]-[Connect 버튼]  
        self.JogSettingGroup.addSettingCard(self.rangeSettingCard) # [JOG] 조그 이동 슬라이더
        self.JogSettingGroup.addSettingCard(self.homeButtonCard)   # [JOG] 조그 원점 이동
        self.JogSettingGroup.addSettingCard(self.position1Card)    # [JOG] 포지션1위치 지정
        self.JogSettingGroup.addSettingCard(self.position2Card)    # [JOG] 포지션2위치 지정      
        self.TestSettingGroup.addSettingCard(self.testCountCard)   # [Test] 테스트 횟수
        self.ActuatorSettingGroup.addSettingCard(self.globalSpeedSettingCard) # [Actu] 액추에이터 반영구 속도
        # self.ActuatorSettingGroup.addSettingCard(self.tempSpeedSettingCard)   # [Actu] 액추에이터 임시 속도
        self.ActuatorSettingGroup.addSettingCard(self.bwdLimitSettingCard)    # [Actu] 액추에이터 후진 제한 위치
        self.ActuatorSettingGroup.addSettingCard(self.fwdLimitSettingCard)    # [Actu] 액추에이터 전진 제한 위치
        self.SaveResetGroup.addSettingCard(self.applyButtonCard)      # [SR] Save
        self.SaveResetGroup.addSettingCard(self.resetButtonCard)      # [SR] Reset
        self.PersonalGroup.addSettingCard(self.themeCard)          # [Personal] "테마" 선택
        # self.personalGroup.addSettingCard(self.zoomCard)           # [Personal] "확대/축소" 선택
        # self.PersonalGroup.addSettingCard(self.languageCard)       # [Personal] "언어" 선택
        # self.aboutGroup.addSettingCard(self.helpCard)              # [About] "도움말" 카드

        # 그룹 -> 레이아웃
        self.expandLayout.setSpacing(28)  # 그룹 간 간격
        self.expandLayout.setContentsMargins(36, 10, 36, 0)  # 여백
        self.expandLayout.addWidget(self.BoardSettingGroup)  # [Board]
        # self.expandLayout.addWidget(self.connectedBoards)    # [Board]-[연결된 기기(보드) 리스트]
        self.expandLayout.addWidget(self.JogSettingGroup)    # [JOG]
        self.expandLayout.addWidget(self.TestSettingGroup)   # [Test]
        self.expandLayout.addWidget(self.ActuatorSettingGroup) # [Actu]
        self.expandLayout.addWidget(self.SaveResetGroup)        # [Danger]
        self.expandLayout.addWidget(self.PersonalGroup)      # [Personal]
        # self.expandLayout.addWidget(self.aboutGroup)         # [About]
    
    def __connectSignalToSlot(self):
        """ 시그널과 슬롯 연결 """
        cfg.appRestartSig.connect(self.__showRestartTooltip)  # 설정 변경 시, 재 시작 알림 표시        
        # 포트 및 장치 연결 관련
        self.searchDeviceCard.setButtonAction(self.__searchPorts)             # [Search 버튼]-클릭 시, 연결된 포트 검색 후 콤보박스에 추가
        self.searchDeviceCard.valueChanged.connect(self.__onPortValueChanged) # [Port 콤보박스]-콤보박스 목록 변동 발생 시, 알림 발생
        self.connectDeviceCard.setButton1Action(self.__onConnectClicked)      # [Connect 버튼]-선택된 보드 연결
        self.connectDeviceCard.setButton2Action(self.__onDisConnectClicked)   # [Disconnect 버튼]-선택된 보드 연결해제

        # 슬라이더 및 위치 관련
        self.rangeSettingCard.valueChanged.connect(self.__actuator_position_changed) # [슬라이더 값 변경]
        self.homeButtonCard.clicked.connect(self.__actuator_position_home) # [Home 버튼 클릭]
        self.position1Card.invalidInput.connect(self.__onInvalidInput)
        self.position2Card.invalidInput.connect(self.__onInvalidInput)
        
        # Reset 및 Apply 버튼
        self.applyButtonCard.clicked.connect(self.__onApplyClicked)  # [Apply 버튼]
        self.resetButtonCard.clicked.connect(self.__onResetClicked) # [Reset 버튼]
        cfg.themeChanged.connect(setTheme)  # [Personal] 테마 변경 시 즉시 적용
    
    def __showRestartTooltip(self):
        """ 설정 변경 직후 , 재시작 알림 표시 """
        InfoBar.success(
            self.tr('Updated successfully'),  
            self.tr('Configuration takes effect after restart'),  # "설정은 재시작 후 적용됨"
            duration=1500,  # 표시 시간 (1.5초)
            parent=self
        )
           
    # [ Board ] ####################################################################################
    def __searchPorts(self):
        """ [Search 버튼] 사용 가능한 포트 검색 및 콤보박스 업데이트 """
        ports = list_ports.comports()                     # 연결된 모든 포트와 상세 정보 가져오기
        port_lists = [port.description for port in ports] # 포트 이름 리스트 생성
        
        if not port_lists:
            port_lists = ["No ports found"]
        
        # UI 콤보박스에 새 옵션 업데이트
        self.searchDeviceCard.setOptions(port_lists)
        _logger.info(f"[Setting] 발견된 포트 목록: {port_lists}")


    def __onPortValueChanged(self, port):
        """ [Port 콤보박스] 포트 값 변경 시 알림 창 생성 """
        _logger.info(f"Selected port: {port}")

        # Flyout 생성
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,  
            title='Alert',  
            content=f"device has changed!",  
            target=self.searchDeviceCard.comboBox, # portcard 위젯 위에 생성
            parent=self,    # 부모 위젯 설정
            isClosable=True # 닫기 버튼 활성화
        )
        
    def __onConnectClicked(self):
        """ [Connect 버튼] PC-보드 연결 """
        selected = self.searchDeviceCard.currentValue()
        match = re.search(r'\((.*?)\)', selected)        
        baud = self.baudrateCard.configItem.value

        # 선택된 보드 X 경우 예외처리
        if not match:
            MessageBox('Error', "No devices are selected. Tap the Search button and select the device you want to connect to first.", self).exec()  # MessageBox 표시
            return
        port = match.group(1)
        
        # 모든 기기가 이미 연결된 경우 알림 표시
        if len(self.actuators) >= 2:
            MessageBox('Notice', "All devices are already connected.", self).exec()
            return
        
        try:
            serial_obj = serial.Serial(port, baud, timeout=0.2)
            actuator = Actuator(
                servo_id=self.default_servo_id,
                serial_obj=serial_obj,
                baudrate=baud,
                port=port
            )
            self.actuators.append(actuator)
            self.connectDeviceCard.setOptions([f'{port} ({baud})']) # 연결된 보드 UI 추가
            
            # 슬라이더 및 실제 액추에이터 0 위치로 초기화
            actuator.send_command(f"SET_POSITION {actuator.servo_id} 0", expect_response=False)  # 액추에이터 초기 위치 설정
            self.rangeSettingCard.slider.setValue(0)
            self.last_slider_position = 0  # 슬라이더의 내부 상태도 0으로 설정  
            
            signalBus.devicesUpdated.emit()  # TestInterface 업데이트 알림
             
            _logger.info(f"보드 연결 성공 => 포트: {selected}, 보드레이트: {baud}")
            MessageBox("Alert", f"Connection Successful!\nYou are connected to {selected}.", self).exec()
        except PermissionError:
            _logger.warning(f"{selected}가 사용 중이거나, 이미 연결됨 (PermissionError)")
            MessageBox("Error", f"Device {selected} is already used.", self).exec()                
        except Exception as e:
            _logger.error(f"포트 {selected} 연결 실패: {e}")
            MessageBox("Error", f"Connection Failed : {selected}", self).exec()
    
                  
    def __onDisConnectClicked(self):
        """ 보드 연결 해제 """
        selected = self.connectDeviceCard.currentValue()
        actuator = None
        for act in self.actuators:
            temp = f'{act.port} ({act.baudrate})'
            if temp == selected:
                actuator = act    
        
        if actuator:
            actuator.serial_obj.close()
            self.actuators.remove(actuator)
            self.connectDeviceCard.removeOption(selected)
            signalBus.devicesUpdated.emit()  # 장치 상태 업데이트 알림 추가
            MessageBox("Alert", f"Board {selected} is disconnected", self).exec()
        else:
            MessageBox("Alert", f"No device to disconnect", self).exec()
            
            
    # [ JOG ] ####################################################################################
    def __get_actuator_by_port(self, port):
        """ 현재 선택된 포트에 해당하는 액추에이터 반환 """
        return next((act for act in self.actuators if act.port == port), None)

    def __actuator_position_changed(self, value):
        """ 슬라이더 값에 따른 액추에이터 위치 변경 """
        selected = self.connectDeviceCard.currentValue()  # 현재 선택된 보드 가져오기
        selected_port = selected.split(' ')[0]  # 포트 정보만 추출
        actuator = self.__get_actuator_by_port(selected_port)
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
        selected = self.connectDeviceCard.currentValue()
        selected_port = selected.split(' ')[0]
        actuator = self.__get_actuator_by_port(selected_port)
        if actuator:
            actuator.send_command(f"SET_POSITION {actuator.servo_id} 0", expect_response=False)
            self.rangeSettingCard.slider.setValue(0)
            self.last_slider_position = 0
        else:
            _logger.error("선택된 포트(보드)가 없음")
    
    def __onInvalidInput(self, text):
        """ 유효하지 않은 입력값이 감지되었을 때 호출 """
        sender = self.sender()  # 현재 신호를 발생시킨 CustomLineEditCard
        Flyout.create(
            icon=InfoBarIcon.WARNING,
            title="Invalid Input",
            content="Please enter a valid number.",
            target=sender.lineEdit,  # 발생한 LineEdit에 Flyout 표시
            parent=self,
            isClosable=True
        )
        _logger.warning(f"Invalid input detected: {text}")
    
    
    def __onResetClicked(self):
        """ Reset 버튼 클릭 시 호출 """
        _logger.info("Resetting all settings to default values.")

        # 설정 초기화 (기본값으로 설정)
        cfg.rangeValue.value = cfg.rangeValue.defaultValue  # Reset RangeValue
        cfg.position1.value = cfg.position1.defaultValue  # Reset Position1
        cfg.position2.value = cfg.position2.defaultValue  # Reset Position2
        cfg.push_counts.value = cfg.push_counts.defaultValue  # Reset PushCounts
        cfg.global_speed.value = cfg.global_speed.defaultValue  # Reset GlobalSpeed
        cfg.temp_speed.value = cfg.temp_speed.defaultValue  # Reset TempSpeed
        cfg.bwd_limit.value = cfg.bwd_limit.defaultValue  # Reset BackwardLimit
        cfg.fwd_limit.value = cfg.fwd_limit.defaultValue  # Reset ForwardLimit

        # UI 업데이트
        self.rangeSettingCard.setValue(cfg.rangeValue.value)
        self.position1Card.setValue(cfg.position1.value)
        self.position2Card.setValue(cfg.position2.value)
        self.testCountCard.setValue(cfg.push_counts.value)
        self.globalSpeedSettingCard.setValue(cfg.global_speed.value)
        # self.tempSpeedSettingCard.setValue(cfg.temp_speed.value)
        self.bwdLimitSettingCard.setValue(cfg.bwd_limit.value)
        self.fwdLimitSettingCard.setValue(cfg.fwd_limit.value)

        # 즉시 저장
        qconfig.save()
        
        # 초기화 후 저장 동작 수행
        self.__applySettings()
        MessageBox('Warning', "All settings have been reset to default values and applied to the actuator.", self).exec()

    def __onApplyClicked(self):
        """ Apply 버튼 클릭 시 호출 """
        _logger.info("Applying settings to the actuator.")
        self.__applySettings()

    def __applySettings(self):
        """ 저장된 설정을 액추에이터에 반영 """
        selected_port = self.connectDeviceCard.currentValue().split(' ')[0]  # 선택된 포트
        actuator = next((act for act in self.actuators if act.port == selected_port), None)

        if actuator:
            try:
                actuator.send_command(f"SET_SPEEDLIMIT {actuator.servo_id} {cfg.global_speed.value}")
                actuator.send_command(f"SET_SPEED {actuator.servo_id} {cfg.temp_speed.value}")
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

    def getConnectedDevices(self):
        """ 현재 연결된 장치 목록 반환(액추에이터 객체) """
        return [act for act in self.actuators]
    
    def __showFlyout(self, message):
        """Flyout 알림 표시"""
        Flyout.create(
            icon=FluentIcon.INFO,
            title="Alert", # Notification
            content=message,
            target=self.scrollWidget,
            parent=self,
            isClosable=True,
        )