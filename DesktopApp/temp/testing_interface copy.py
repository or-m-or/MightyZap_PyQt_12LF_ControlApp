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

_logger = setup_logger(name="MainApp", level='INFO')


class TestInterface(ScrollArea):
    """테스트 인터페이스 클래스"""

    def __init__(self, setting_interface: SettingInterface, parent=None):
        super().__init__(parent=parent)
        self.setting_interface = setting_interface # SettingInterface 인스턴스 참조
        self.workers = {}  # 실행 중인 워커를 관리하는 딕셔너리
        self.__initui()
        
        # Signal 연결
        signalBus.devicesUpdated.connect(self.updateDeviceList)  # SettingInterface의 업데이트 신호 연결
        
    def __initui(self):    
        self.scrollWidget = QWidget()
        self.expandLayout = QVBoxLayout(self.scrollWidget)
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(20, 40, 20, 20)
        
        # 위에서 아래로 쌓이도록 설정
        self.expandLayout.setDirection(QVBoxLayout.TopToBottom)
        
        self.settingLabel = QLabel(self.tr("Teasting"), self) # "테스팅" 라벨
        self.scrollWidget.setLayout(self.expandLayout)
        
        # [기기 선택 그룹]
        self.BoardSelectionGroup = SettingCardGroup(self.tr("Device Selection"), self.scrollWidget)
        self.boardSelectCard = CustomComboBoxButtonCard(
            icon=FIF.ADD,
            title=self.tr("Add Test"),
            content=self.tr(
                "Select the device you want to test from the list of connected devices. \n"
                "Then click the Add Test button to add a new test template."
            ),
            items=[""],
            combobox_width=190,
            button_width=80,
            button_text="Add Test",
            parent=self.BoardSelectionGroup,
        )  
        self.updateDeviceList()
        self.__initWidget()
        
    def updateDeviceList(self):
        """ SettingInterface에서 연결된 장치 리스트를 가져와 콤보박스에 설정 """
        devices = self.setting_interface.getConnectedDevices()
        # devices가 문자열 리스트인지 검사
        if not devices or isinstance(devices[0], str):
            self.boardSelectCard.setOptions(["No devices connected"])
            _logger.info("No devices connected.")
            return
        
        temp = [f"{act.port} ({act.baudrate})" for act in devices]
        self.boardSelectCard.setOptions(temp)
        _logger.info(f"TestInterface 장치 목록 업데이트: {devices}")

    def __initWidget(self):
        """테스트 인터페이스 전체 위젯 초기화"""
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)   # 뷰포트 여백
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("TestingInterface")
        self.scrollWidget.setMinimumHeight(600)  # 최소 높이 설정
        self.scrollWidget.setMinimumWidth(800)  # 최소 너비 설정
        
        # 스타일시트 적용
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('testingLabel')
        StyleSheet.TESTING_INTERFACE.apply(self)
        
        # 레이아웃 초기화
        self.__initLayout()
        self.__connectSignalToSlot()
    
    def __initLayout(self):
        """ 레이아웃 초기화 """
        self.settingLabel.move(36, 30)  # 설정 라벨 위치 설정 (좌측 상단)
        
        # 카드 -> 그룹
        self.BoardSelectionGroup.addSettingCard(self.boardSelectCard)
        
        # 그룹 -> 레이아웃
        self.expandLayout.setSpacing(28)  # 그룹 간 간격
        self.expandLayout.setContentsMargins(36, 10, 36, 0)  # 여백
        self.expandLayout.addWidget(self.BoardSelectionGroup)
    
    def __connectSignalToSlot(self):
        """ 시그널 슬롯 연결 """
        self.boardSelectCard.setButtonAction(self.__onAddTestClicked)
        
    def __onAddTestClicked(self):
        """ Add Test 버튼 클릭 시 실행 """
        selected_device = self.boardSelectCard.currentValue()
        
        _logger.info(f"Add Test button clicked. Selected device: {selected_device}")
        
        if selected_device == "No devices connected":
            InfoBar.warning(
                self.tr("No device selected"),
                self.tr("Please select a connected device before adding a test."),
                parent=self,
            )
            return

        # SettingInterface에서 해당 액추에이터 객체 찾기
        actuator = next(
            (act for act in self.setting_interface.getConnectedDevices() if f"{act.port} ({act.baudrate})" == selected_device),
            None,
        )

        if actuator:
            _logger.info(f"Add Test for actuator: {actuator.port} ({actuator.baudrate})")
            self.__addTestTemplate(actuator)  # 선택된 액추에이터를 기반으로 템플릿 추가
        else:
            InfoBar.error(
                self.tr("Invalid selection"),
                self.tr("Could not find the selected device."),
                parent=self,
            )
            
    def __addTestTemplate(self, actuator: Actuator):
        """테스트 템플릿 동적 추가"""      
        
        # 테스트 카드
        testCard = QWidget(self.scrollWidget)
        testCard.setObjectName("TestCard")
        testCard.setFixedHeight(100)

        # 테스트 카드 레이아웃
        cardLayout = QHBoxLayout(testCard)
        cardLayout.setContentsMargins(16, 8, 16, 8)
        cardLayout.setSpacing(15)

        # 테스트 횟수 라벨
        countLabel = QLabel("0", testCard)
        countLabel.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(40)  # 숫자를 크게 표시
        font.setBold(True)
        countLabel.setFont(font)
        cardLayout.addWidget(countLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # 템플릿 정보와 버튼 그룹
        infoButtonLayout = QVBoxLayout()
        infoButtonLayout.setSpacing(5)

        # 템플릿 정보 레이아웃
        infoLayout = QVBoxLayout()
        infoLayout.setSpacing(5)

        # 장치 정보 라벨
        templateLabel = QLabel(f"Template: {actuator.port} ({actuator.baudrate})", testCard)
        templateLabel.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        templateLabel.setFont(font)
        infoLayout.addWidget(templateLabel)

        # 버튼 레이아웃
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(10)

        # 버튼 생성
        startButton = PrimaryPushButton(self.tr("Start"), testCard)
        stopButton = PushButton(self.tr("Stop"), testCard)
        deleteButton = PushButton(self.tr("Delete"), testCard)

        # 버튼 크기 조정
        startButton.setFixedSize(180, 30)
        stopButton.setFixedSize(180, 30)
        deleteButton.setFixedSize(180, 30)

        # 버튼 동작 설정
        startButton.clicked.connect(lambda: self.__onTestStart(actuator, countLabel))  # countLabel 추가
        stopButton.clicked.connect(lambda: self.__onTestStop(actuator))  # countLabel 불필요
        deleteButton.clicked.connect(lambda: self.__deleteTestTemplate(testCard))

        # 버튼을 버튼 레이아웃에 추가
        buttonLayout.addWidget(startButton)
        buttonLayout.addWidget(stopButton)
        buttonLayout.addWidget(deleteButton)

        # 레이아웃을 카드에 추가
        infoButtonLayout.addLayout(infoLayout)
        infoButtonLayout.addLayout(buttonLayout)

        # 템플릿 카드 레이아웃에 추가
        cardLayout.addLayout(infoButtonLayout)
        self.expandLayout.insertWidget(1, testCard) # 테스트 카드를 레이아웃의 첫 번째 위치에 삽입

        # Flyout 알림 추가
        self.__showFlyout(f"Test template added for {actuator.port} ({actuator.baudrate}).")

        # 강제 갱신
        self.scrollWidget.adjustSize()
        self.scrollWidget.update()
        self.update()
        _logger.info("Test template added and UI updated.")

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

    def __updateCount(self, actuator: Actuator, countLabel: QLabel):
        """테스트 완료 횟수 업데이트"""
        actuator.complete_count = getattr(actuator, 'complete_count', 0) + 1
        countLabel.setText(str(actuator.complete_count))  # 라벨에 테스트 횟수 업데이트

        self.__showFlyout(
            f"Test completed for {actuator.port} ({actuator.baudrate}). "
            f"Total completions: {actuator.complete_count}."
        )

        
    def __onTestStop(self, actuator: Actuator): # label: QLabel  statusBadge
        """테스트 정지"""
        if actuator in self.workers:
            self.workers[actuator].cancel()
            # label.setText("Status: Stopping")
            # InfoBar.info(
            #     self.tr("Test stopping"),
            #     self.tr(f"Stopping test for {actuator.port}."),
            #     parent=self,
            # )
            # spinner.setVisible(False)  # Progress Ring 숨기기
            self.workers[actuator].cancel()
            self.__showFlyout(f"Test stopping for {actuator.port}.")


    def __deleteTestTemplate(self, testCard: QWidget):
        """테스트 템플릿 삭제 및 카운팅 초기화"""
        # 테스트 카드의 부모에서 제거
        testCard.setParent(None)

        # 템플릿에 연결된 Actuator 찾기
        device_label = testCard.findChild(QLabel, None)
        if device_label:
            device_info = device_label.text()
            if device_info.startswith("Template: "):  # 텍스트 형식 확인
                try:
                    device_details = device_info.split(": ")[1]
                    port, baudrate = device_details.split(" (")
                    baudrate = baudrate.strip(")")

                    actuator = next((act for act in self.setting_interface.getConnectedDevices()
                                    if act.port == port and str(act.baudrate) == baudrate), None)
                    if actuator:
                        actuator.complete_count = 0  # 카운팅 초기화
                        _logger.info(f"Reset complete count for actuator: {actuator.port} ({actuator.baudrate})")
                    else:
                        _logger.warning(f"Actuator not found for device: {device_info}")
                except (IndexError, ValueError) as e:
                    _logger.error(f"Error parsing device info '{device_info}': {e}")
            else:
                _logger.error(f"Unexpected device label format: '{device_info}'")
        else:
            _logger.error("Device label not found in the test card")

        # UI 갱신
        self.scrollWidget.adjustSize()
        InfoBar.info(
            self.tr("Test template deleted"),
            self.tr("The selected test template has been removed, and count reset."),
            parent=self,
        )


    def __cleanup_worker(self, actuator: Actuator):
        """워커 정리"""
        if actuator in self.workers:
            self.workers[actuator].quit()
            self.workers[actuator].wait()
            del self.workers[actuator]
            _logger.info(f"Worker cleaned up for {actuator.port}")
            
    # def __updateStatusBadge(self, badge, status):
    #     """상태 Badge 업데이트"""
    #     status_map = {
    #         "ready": (FluentIcon.INFO, "Ready", "blue"),
    #         "running": (FluentIcon.PLAY_SOLID, "Running", "green"),
    #         "stopping": (FluentIcon.PAUSE_BOLD, "Stopping", "orange"),
    #         "complete": (FluentIcon.ACCEPT_MEDIUM, "Complete", "purple"),
    #     }
    #     icon, text, _ = status_map[status]
    #     badge.setIcon(icon)
    #     badge.setText(text)

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