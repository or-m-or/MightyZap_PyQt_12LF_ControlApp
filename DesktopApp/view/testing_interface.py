"""
테스팅 화면에 기본 설정 기능 추가
"""
import resource_rc
import serial, re
from serial.tools import list_ports
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths, QTimer
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
    SingleDirectionScrollArea,
    FluentIcon,
    InfoBadge,
    IndeterminateProgressRing,
    IndeterminateProgressBar,
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
from view.settings_interface import SettingInterface
from core.worker import TestWorker 

_logger = setup_logger(name="TestInterface", level='INFO')

class TestInterface(ScrollArea):
    """테스트 인터페이스 클래스"""

    def __init__(self, setting_interface: SettingInterface, parent=None):
        super().__init__(parent=parent)
        self.setting_interface = setting_interface  # SettingInterface 인스턴스 참조
        self.workers = {}                           # 실행중인 테스트 워커
        self.assigned_actuators = [None, None]      # 테스트 액추에이터
        self.progressBars = {} 
        self.timer = QTimer(self)                   # 시리얼 데이터 모니터링 타이머
        self.timer.setInterval(300)                 # 300ms 주기로 실행
        self.timer.timeout.connect(self.monitor_serial_data)  
        self.__initui()
        
        # Signal 연결
        signalBus.devicesUpdated.connect(self.updateDeviceList)  # SettingInterface의 업데이트 신호 연결
        self.timer.start()  # 타이머 시작

    def __initui(self):
        """ 테스트 인터페이스 전체 위젯 초기화 """
        self.setObjectName("TestingInterface")
        self.resize(1000, 800)  # 초기 창 크기 설정
        self.setWidgetResizable(True) # 창 크기 변경 허용
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded) # 가로 스크롤바 표시여부(자동, 기본옵션)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)   # 세로 스크롤바
        self.setViewportMargins(0, 80, 0, 20)  # 뷰포트 여백 설정
        
        self.scrollWidget = QWidget()           # 메인 위젯
        self.scrollWidget.setMinimumHeight(600) # 최소 높이 설정
        self.scrollWidget.setMinimumWidth(800)  # 최소 너비 설정
        self.scrollWidget.setObjectName('scrollWidget') # 스타일시트 적용
        self.setWidget(self.scrollWidget)
        
        # 레이아웃 초기화
        self.__initLayout()
        
        # 스타일시트 적용
        StyleSheet.TESTING_INTERFACE.apply(self)
        
        
    def __initLayout(self):
        """ 레이아웃 초기화 """
        self.settingLabel = QLabel(self.tr("Teasting"), self)
        self.settingLabel.move(36, 30)
        self.settingLabel.setObjectName('testingLabel')
        
        # 메인 레이아웃 설정
        self.mainLayout = QVBoxLayout(self.scrollWidget)  # 세로로 배치
        self.mainLayout.setSpacing(20)  # 카드 간 간격
        self.mainLayout.setContentsMargins(20, 1, 20, 20)  # 전체 여백 설정

        # 테스트 카드 레이아웃 (좌우 배치)
        self.cardLayout = QHBoxLayout()  # 카드 배치용 가로 레이아웃
        self.cardLayout.setSpacing(28)  # 카드 간 간격

        # 테스트 카드 1 (왼쪽)
        self.testCard1 = self.__createTestCard("Test 1")
        self.cardLayout.addWidget(self.testCard1["widget"])

        # 테스트 카드 2 (오른쪽)
        self.testCard2 = self.__createTestCard("Test 2")
        self.cardLayout.addWidget(self.testCard2["widget"])

        # 카드 레이아웃을 메인 레이아웃에 추가
        self.mainLayout.addLayout(self.cardLayout)

    def __createTestCard(self, title):
        """고정된 테스트 카드 생성"""
        testCardWidget = QWidget(self.scrollWidget)
        testCardWidget.setObjectName(f"{title.replace(' ', '_')}Card")
        testCardWidget.setFixedSize(350, 300)  # 카드 크기 조정 (넓이 350, 높이 300)

        cardLayout = QVBoxLayout(testCardWidget)  # 세로로 구성
        cardLayout.setContentsMargins(16, 8, 16, 8)
        cardLayout.setSpacing(20)

        # 카운팅 숫자 (맨 위)
        countLabel = QLabel("0", testCardWidget)
        countLabel.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(70)  # 숫자를 크게 표시
        font.setBold(True)
        countLabel.setFont(font)
        cardLayout.addWidget(countLabel, alignment=Qt.AlignTop)
        
        # 테스트 상태 라벨
        templateLabel = QLabel(f"{title}: No Device Connected", testCardWidget)
        templateLabel.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)  # 상태 라벨 크기
        font.setBold(True)
        templateLabel.setFont(font)
        cardLayout.addWidget(templateLabel)
        
        # ProgressBar 추가 (숨김 상태로 초기화)
        progressBar = IndeterminateProgressBar(testCardWidget)
        progressBar.setFixedHeight(4)  # ProgressBar 높이 설정
        progressBar.stop()
        cardLayout.addWidget(progressBar)
                
        # 버튼 레이아웃
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(15)

        # 버튼 생성
        startButton = PrimaryPushButton(self.tr("Start"), testCardWidget)
        resetButton = PushButton(self.tr("Reset"), testCardWidget)  # Reset 버튼
        startButton.setFixedSize(140, 40)  # 버튼 크기
        resetButton.setFixedSize(140, 40)

        buttonLayout.addWidget(startButton)
        buttonLayout.addWidget(resetButton)

        cardLayout.addLayout(buttonLayout)

        return {
            "widget": testCardWidget,
            "countLabel": countLabel,
            "templateLabel": templateLabel,
            "progressBar": progressBar,  # ProgressBar 추가
            "startButton": startButton,
            "resetButton": resetButton,
        }


    def monitor_serial_data(self):
        """ 시리얼 통신 데이터를 주기적으로 확인하여 물리 버튼 눌러지면 -> 티스트 1회 실행 """
        for idx, actuator in enumerate(self.assigned_actuators):
            if actuator and actuator.serial_obj and actuator.serial_obj.is_open and actuator.serial_obj.in_waiting > 0:
                try:
                    command = actuator.serial_obj.readline().strip().decode()
                    _logger.debug(f"[monitor_serial_data] ({actuator.port}) 수신 명령: {command}")
                    if command == "TEST":
                        # 매칭된 카드의 테스트를 시작
                        self.__startTestByActuator(idx)
                    else:
                        _logger.warning(f"Unknown command received: {command}")
                except Exception as e:
                    _logger.error(f"Error reading serial data: {e}")
                    
    def updateDeviceList(self):
        """ 설정 페이지에서 연결된 장치 리스트를 업데이트하고 고정된 테스트 화면과 매칭 """
        devices = self.setting_interface.getConnectedDevices()
        
        # 이미 모든 기기가 연결된 경우 알림 표시
        if len(devices) >= 2 and self.assigned_actuators[0] and self.assigned_actuators[1]:
            self.setting_interface.showFlyout("All devices are already connected.")
            return

        # 현재 매칭된 액추에이터를 유지
        for idx, actuator in enumerate(devices[:2]):  # 최대 2개의 기기만 처리
            if self.assigned_actuators[idx] == actuator:
                continue  # 이미 매칭된 경우 그대로 유지
            self.assigned_actuators[idx] = actuator  # 새로운 기기 매칭
            if idx == 0:
                self.__assignDeviceToTestCard(actuator, self.testCard1)  # 첫 번째 테스트 카드와 매칭
            elif idx == 1:
                self.__assignDeviceToTestCard(actuator, self.testCard2)  # 두 번째 테스트 카드와 매칭

        # 현재 연결이 없는 테스트 카드를 초기화
        for idx in range(len(devices), 2):  # 연결된 기기 개수 이후의 카드 초기화
            self.assigned_actuators[idx] = None
            if idx == 0:
                self.__clearTestCard(self.testCard1)
            elif idx == 1:
                self.__clearTestCard(self.testCard2)        
                
    def __clearTestCard(self, testCard):
        """테스트 카드의 상태를 초기화"""
        testCard["templateLabel"].setText("No Device Connected")
        testCard["countLabel"].setText("0")  # 카운트 초기화


    def __assignDeviceToTestCard(self, actuator, testCard):
        """ 기기를 특정 테스트 카드에 매칭 """
        # 기존 기기와 동일한 기기를 다시 매칭하려는 경우 아무 작업도 하지 않음
        if testCard["templateLabel"].text() == f"Device: {actuator.port} ({actuator.baudrate})":
            return  # 이미 연결된 상태이므로 중복 작업 방지
    
        # 테스트 카드 라벨 업데이트
        testCard["templateLabel"].setText(f"Device: {actuator.port} ({actuator.baudrate})")
        testCard["countLabel"].setText("0")  # 초기화된 카운트 표시

        # 새로운 슬롯 연결
        testCard["startButton"].clicked.connect(lambda: self.__onTestStart(actuator, testCard["countLabel"]))
        testCard["resetButton"].clicked.connect(lambda: self.__onReset(testCard["countLabel"]))

    def __onTestStart(self, actuator: Actuator, countLabel: QLabel):
        """ 테스트 시작 """
        if actuator in self.workers and self.workers[actuator].isRunning():
            return

        # ProgressBar 표시
        testCard = self.testCard1 if countLabel == self.testCard1["countLabel"] else self.testCard2
        progressBar = testCard["progressBar"]
        progressBar.setMaximumHeight(4)
        progressBar.start()
        
        # 워커 생성
        position1 = cfg.position1.value
        position2 = cfg.position2.value
        push_counts = cfg.push_counts.value

        worker = TestWorker(actuator, position1, position2, push_counts)
        self.workers[actuator] = worker

        # 테스트 완료 시 테스트 횟수 업데이트
        worker.test_complete.connect(lambda: self.__updateCount(actuator, countLabel))
        worker.finished.connect(lambda: self.__cleanup_worker(actuator))
        worker.finished.connect(lambda: self.__hideProgressBar(progressBar))

        worker.start()

    def __onReset(self, countLabel: QLabel):
        """카운팅 숫자를 0으로 초기화"""
        # 해당 countLabel에 매칭된 actuator를 찾음
        for actuator in self.assigned_actuators:
            if actuator and countLabel == self.testCard1["countLabel"]:
                actuator.complete_count = 0
                break
            elif actuator and countLabel == self.testCard2["countLabel"]:
                actuator.complete_count = 0
                break

        countLabel.setText("0")

    def __updateCount(self, actuator: Actuator, countLabel: QLabel):
        """테스트 완료 횟수 업데이트"""
        actuator.complete_count = getattr(actuator, 'complete_count', 0) + 1
        countLabel.setText(str(actuator.complete_count))  # 라벨에 테스트 횟수 업데이트

    def __startTestByActuator(self, index):
        """특정 액추에이터에 대한 테스트 시작"""
        if index == 0:
            actuator = self.assigned_actuators[0]
            if actuator:
                self.__onTestStart(actuator, self.testCard1["countLabel"])
        elif index == 1:
            actuator = self.assigned_actuators[1]
            if actuator:
                self.__onTestStart(actuator, self.testCard2["countLabel"])

    def __cleanup_worker(self, actuator: Actuator):
        """워커 정리"""
        if actuator in self.workers:
            self.workers[actuator].quit()
            self.workers[actuator].wait()
            del self.workers[actuator]
            _logger.info(f"Worker cleaned up for {actuator.port}")
    
    def __hideProgressBar(self, progressBar: IndeterminateProgressBar):
        """ProgressBar 숨기기"""
        progressBar.stop()
        
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
