"""
카운팅 초기화 해야함.
이거 카운팅 박스랑 기기 매칭 잘되었는지 코드 검토 필요 

박스 2개 위로 좀 더 올려야함

상태 변경시 알림 방식 변경 필요 
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
        self.setObjectName("TestInterface")
        self.workers = {}  # 실행 중인 워커를 관리하는 딕셔너리
        self.assigned_actuators = [None, None]  # 고정된 두 테스트 화면에 할당된 액추에이터
        self.timer = QTimer(self)  # 시리얼 데이터 모니터링 타이머
        self.timer.setInterval(300)  # 300ms 주기로 실행
        self.timer.timeout.connect(self.monitor_serial_data)
        # self.__initui()
        self.__initWidget()
        
        # Signal 연결
        signalBus.devicesUpdated.connect(self.updateDeviceList)  # SettingInterface의 업데이트 신호 연결
        self.timer.start()  # 타이머 시작
        
    def __initWidget(self):
        """테스트 인터페이스 전체 위젯 초기화"""
        self.settingLabel = QLabel(self.tr("Teasting"), self)
        self.resize(1000, 800)  # 초기 창 크기 설정
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)  # 뷰포트 여백 설정
        self.setObjectName("TestingInterface")

        self.scrollWidget = QWidget()
        self.scrollWidget.setMinimumHeight(600)  # 최소 높이 설정
        self.scrollWidget.setMinimumWidth(800)  # 최소 너비 설정

        # 스타일시트 적용
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('testingLabel')
        StyleSheet.TESTING_INTERFACE.apply(self)

        # 레이아웃 초기화
        self.__initLayout()

        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
    def __initLayout(self):
        """ 레이아웃 초기화 """
        self.settingLabel.move(36, 30)
        
        # 메인 레이아웃 설정
        self.mainLayout = QVBoxLayout(self.scrollWidget)  # 세로로 배치
        self.mainLayout.setSpacing(20)  # 카드 간 간격
        self.mainLayout.setContentsMargins(20, 1, 20, 20)  # 전체 여백 설정

        # self.settingLabel = QLabel(self.tr("Teasting"), self) # "테스팅" 라벨

        # # 상단 제목 추가
        # self.titleLabel = QLabel("Testing", self.scrollWidget)
        # self.titleLabel.setAlignment(Qt.AlignCenter)
        # font = QFont()
        # font.setPointSize(24)  # 제목 폰트 크기
        # font.setBold(True)
        # self.titleLabel.setFont(font)
        # self.mainLayout.addWidget(self.titleLabel, alignment=Qt.AlignTop)

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
        font.setPointSize(50)  # 숫자를 크게 표시
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
            "startButton": startButton,
            "resetButton": resetButton,
        }

    # def __initLayout(self):
    #     """ 레이아웃 초기화 """
    #     self.mainLayout = QHBoxLayout(self.scrollWidget)  # 좌우 배치 레이아웃
    #     self.mainLayout.setSpacing(28)  # 카드 간 간격
    #     self.mainLayout.setContentsMargins(20, 20, 20, 20)  # 전체 여백 설정

    #     # 테스트 카드 1 (왼쪽)
    #     self.testCard1 = self.__createTestCard("Test 1")
    #     self.mainLayout.addWidget(self.testCard1["widget"])

    #     # 테스트 카드 2 (오른쪽)
    #     self.testCard2 = self.__createTestCard("Test 2")
    #     self.mainLayout.addWidget(self.testCard2["widget"])
        

    # def __createTestCard(self, title):
    #     """고정된 테스트 카드 생성"""
    #     testCardWidget = QWidget(self.scrollWidget)
    #     testCardWidget.setObjectName(f"{title.replace(' ', '_')}Card")
    #     testCardWidget.setFixedSize(300, 200)  # 가로 300, 세로 200 크기 설정

    #     cardLayout = QVBoxLayout(testCardWidget)  # 세로로 구성
    #     cardLayout.setContentsMargins(16, 8, 16, 8)
    #     cardLayout.setSpacing(15)

    #     # 카운팅 숫자 (맨 위)
    #     countLabel = QLabel("0", testCardWidget)
    #     countLabel.setAlignment(Qt.AlignCenter)
    #     font = QFont()
    #     font.setPointSize(50)  # 숫자를 크게 표시
    #     font.setBold(True)
    #     countLabel.setFont(font)
    #     cardLayout.addWidget(countLabel, alignment=Qt.AlignTop)

    #     # 테스트 상태 라벨
    #     templateLabel = QLabel(f"{title}: No Device Connected", testCardWidget)
    #     templateLabel.setAlignment(Qt.AlignCenter)
    #     font = QFont()
    #     font.setPointSize(12)
    #     font.setBold(True)
    #     templateLabel.setFont(font)
    #     cardLayout.addWidget(templateLabel)

    #     # 버튼 레이아웃
    #     buttonLayout = QHBoxLayout()
    #     buttonLayout.setSpacing(10)

    #     # 버튼 생성
    #     startButton = PrimaryPushButton(self.tr("Start"), testCardWidget)
    #     resetButton = PushButton(self.tr("Reset"), testCardWidget)  # Reset 버튼
    #     startButton.setFixedSize(120, 30)
    #     resetButton.setFixedSize(120, 30)

    #     buttonLayout.addWidget(startButton)
    #     buttonLayout.addWidget(resetButton)

    #     cardLayout.addLayout(buttonLayout)

    #     return {
    #         "widget": testCardWidget,
    #         "countLabel": countLabel,
    #         "templateLabel": templateLabel,
    #         "startButton": startButton,
    #         "resetButton": resetButton,
    #     }

    def updateDeviceList(self):
        """설정 페이지에서 연결된 장치 리스트를 업데이트하고 고정된 테스트 화면과 매칭"""
        devices = self.setting_interface.getConnectedDevices()

        # 매칭된 기기가 없으면 초기화
        self.assigned_actuators = [None, None]

        if len(devices) > 0:
            self.__assignDeviceToTestCard(devices[0], self.testCard1)
        if len(devices) > 1:
            self.__assignDeviceToTestCard(devices[1], self.testCard2)

    def __assignDeviceToTestCard(self, actuator, testCard):
        """기기를 특정 테스트 카드에 매칭"""
        self.assigned_actuators[self.mainLayout.indexOf(testCard["widget"])] = actuator
        testCard["templateLabel"].setText(f"Device: {actuator.port} ({actuator.baudrate})")
        testCard["countLabel"].setText("0")

        # 버튼 동작 설정
        testCard["startButton"].clicked.connect(lambda: self.__onTestStart(actuator, testCard["countLabel"]))
        testCard["resetButton"].clicked.connect(lambda: self.__onReset(testCard["countLabel"]))

    def __onTestStart(self, actuator: Actuator, countLabel: QLabel):
        """테스트 시작"""
        if actuator in self.workers and self.workers[actuator].isRunning():
            return

        position1 = cfg.position1.value
        position2 = cfg.position2.value
        push_counts = cfg.push_counts.value

        worker = TestWorker(actuator, position1, position2, push_counts)
        self.workers[actuator] = worker

        # 테스트 완료 시 테스트 횟수 업데이트
        worker.test_complete.connect(lambda: self.__updateCount(actuator, countLabel))
        worker.finished.connect(lambda: self.__cleanup_worker(actuator))
        worker.start()

        self.__showFlyout(f"Test started for {actuator.port}.")

    def __onReset(self, countLabel: QLabel):
        """카운팅 숫자를 0으로 초기화"""
        countLabel.setText("0")
        self.__showFlyout("Count reset to 0.")

    #################################################################

    #################################################################
    def __updateCount(self, actuator: Actuator, countLabel: QLabel):
        """테스트 완료 횟수 업데이트"""
        actuator.complete_count = getattr(actuator, 'complete_count', 0) + 1
        countLabel.setText(str(actuator.complete_count))  # 라벨에 테스트 횟수 업데이트

        self.__showFlyout(
            f"Test completed for {actuator.port} ({actuator.baudrate}). "
            f"Total completions: {actuator.complete_count}."
        )

    def monitor_serial_data(self):
        """시리얼 데이터를 주기적으로 확인하여 명령을 처리"""
        for actuator in self.setting_interface.getConnectedDevices():
            serial_obj = actuator.serial_obj
            if serial_obj and serial_obj.is_open and serial_obj.in_waiting > 0:
                try:
                    command = serial_obj.readline().strip().decode()
                    _logger.debug(f"[monitor_serial_data] ({actuator.port}) 수신 명령: {command}")
                    if command == "TEST":
                        self.__startTestByActuator(actuator)
                    else:
                        _logger.warning(f"Unknown command received: {command}")
                except Exception as e:
                    _logger.error(f"Error reading serial data: {e}")

    def __startTestByActuator(self, actuator):
        """특정 액추에이터에 대한 테스트 시작"""
        if actuator == self.assigned_actuators[0]:
            self.__onTestStart(actuator, self.testCard1["countLabel"])
        elif actuator == self.assigned_actuators[1]:
            self.__onTestStart(actuator, self.testCard2["countLabel"])

    def __cleanup_worker(self, actuator: Actuator):
        """워커 정리"""
        if actuator in self.workers:
            self.workers[actuator].quit()
            self.workers[actuator].wait()
            del self.workers[actuator]
            _logger.info(f"Worker cleaned up for {actuator.port}")

    def __showFlyout(self, message):
        """Flyout 알림 표시"""
        Flyout.create(
            icon=FluentIcon.INFO,
            title="Notification",
            content=message,
            target=self.scrollWidget,
            parent=self,
            isClosable=True,
        )
