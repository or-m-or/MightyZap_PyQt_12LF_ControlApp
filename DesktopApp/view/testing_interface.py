import resource_rc
from qfluentwidgets import (
    ScrollArea,
    SingleDirectionScrollArea,
    SettingCardGroup,
    PrimaryPushSettingCard,
    ComboBoxSettingCard,
    PushButton,
    InfoBar,
)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from common.config import cfg
from common.style_sheet import StyleSheet
from qfluentwidgets import GroupHeaderCardWidget, PrimaryPushButton, PushButton

class TestInterface(ScrollArea):
    """테스트 인터페이스 클래스"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # 메인 위젯과 레이아웃
        self.scrollWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.scrollWidget)
        self.mainLayout.setContentsMargins(20, 10, 20, 10)  # 상하 간격 줄임
        self.mainLayout.setSpacing(15)  # 그룹 간 간격 축소

        # 상단 포트 선택 영역
        self.portSelectionWidget = QWidget(self.scrollWidget)
        self.portSelectionLayout = QVBoxLayout(self.portSelectionWidget)
        self.portSelectionLayout.setContentsMargins(0, 0, 0, 0)
        self.portSelectionLayout.setSpacing(10)

        # "Test" 라벨
        self.testLabel = QLabel(self.tr("Testing"))
        self.testLabel.setObjectName("testLabel")
        self.testLabel.setFixedHeight(50)
        self.portSelectionLayout.addWidget(self.testLabel)

        # [포트 선택 그룹]
        self.PortSelectionGroup = SettingCardGroup(self.tr("Device Selection"), self.portSelectionWidget)
        self.portComboBox = ComboBoxSettingCard(
            configItem=cfg.port,
            icon=FIF.CONNECT,
            title=self.tr("Choose a device"),
            content=self.tr("From the list of connected devices, select the device you want to test."),
            texts=cfg.port.options,  # 예제 값. 동적 업데이트 가능
            parent=self.PortSelectionGroup,
        )
        self.addTestButton = PrimaryPushSettingCard(
            text=self.tr("Add Test"),
            icon=FIF.ADD,
            title=self.tr("Add Test"),
            content=self.tr("Click to add a new test template."),
            parent=self.PortSelectionGroup,
        )
        self.addTestButton.clicked.connect(self.addTestTemplate)
        self.PortSelectionGroup.addSettingCard(self.portComboBox)
        self.PortSelectionGroup.addSettingCard(self.addTestButton)
        self.portSelectionLayout.addWidget(self.PortSelectionGroup)

        # 템플릿 그룹 (SettingCardGroup 추가)
        self.TemplateGroup = SettingCardGroup(self.tr("Testing"), self.scrollWidget)
        # 그룹 내 여백 조정
        self.TemplateGroup.layout().setContentsMargins(10, 5, 10, 5)  # 상하 간격 줄임
        self.TemplateGroup.layout().setSpacing(10)

        self.templateScrollArea = SingleDirectionScrollArea(orient=Qt.Vertical)
        self.templateScrollWidget = QWidget()
        self.templateLayout = QVBoxLayout(self.templateScrollWidget)
        self.templateLayout.setContentsMargins(0, 0, 0, 0)
        self.templateLayout.setSpacing(10)
        self.templateLayout.setAlignment(Qt.AlignTop)  # 위쪽 정렬
        self.templateScrollArea.setWidget(self.templateScrollWidget)
        self.templateScrollArea.setWidgetResizable(True)
        self.templateScrollArea.setFixedHeight(500)  # 템플릿 스크롤 영역 높이 증가

        # 템플릿 그룹에 스크롤 영역 추가
        self.TemplateGroup.layout().addWidget(self.templateScrollArea)

        # 메인 레이아웃에 추가
        self.mainLayout.addWidget(self.portSelectionWidget)
        self.mainLayout.addWidget(self.TemplateGroup)
        self.setLayout(self.mainLayout)

        self.__initWidget()
        self.apply_styles()

    def __initWidget(self):
        """테스트 인터페이스 전체 위젯 초기화"""
        # self.testLabel.move(36, 30)
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("testInterface")
        

    def apply_styles(self):
        """QSS 스타일 적용"""
        self.scrollWidget.setObjectName("scrollWidget")
        self.setObjectName("testInterface")
        self.templateScrollWidget.setObjectName("templateLayout")
        StyleSheet.TESTING_INTERFACE.apply(self)


    def addTestTemplate(self):
        """테스트 템플릿 동적 추가 (세로 길이 및 레이아웃 수정)"""
        # 테스트 카드
        testCard = QWidget(self.templateScrollWidget)
        testCard.setObjectName("TestCard")
        testCard.setFixedHeight(200)  # 세로 길이 증가

        # 테스트 카드 레이아웃
        cardLayout = QVBoxLayout(testCard)
        cardLayout.setContentsMargins(16, 16, 16, 16)  # 카드 내부 여백
        cardLayout.setSpacing(12)

        # 테스트 카운트 라벨
        testCountLabel = QLabel("0", testCard)
        testCountLabel.setAlignment(Qt.AlignCenter)
        testCountLabel.setObjectName("testCardLabel")  # 스타일링에 사용할 이름 설정
        cardLayout.addWidget(testCountLabel)

        # 버튼 레이아웃
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(10)
        buttonLayout.setContentsMargins(0, 0, 0, 0)

        # 버튼 생성
        startButton = PrimaryPushButton(self.tr("Start"), testCard)
        startButton.setObjectName("testCardStartButton")  # QSS 스타일링 이름

        ResetButton = PushButton(self.tr("Reset"), testCard)
        ResetButton.setObjectName("testCardStopButton")
        
        deleteButton = PushButton(self.tr("Delete"), testCard)
        deleteButton.setObjectName("testCardDeleteButton")

        # 버튼 크기 고정
        startButton.setFixedHeight(36)
        ResetButton.setFixedHeight(36)
        deleteButton.setFixedHeight(36)

        # 버튼을 버튼 레이아웃에 추가
        buttonLayout.addWidget(startButton)
        buttonLayout.addWidget(ResetButton)
        buttonLayout.addWidget(deleteButton)

        # 버튼 레이아웃을 카드 레이아웃에 추가
        cardLayout.addLayout(buttonLayout)

        # 버튼 동작 설정
        startButton.clicked.connect(lambda: self.onTestStart(testCountLabel))
        ResetButton.clicked.connect(lambda: self.onTestStop(testCountLabel))
        deleteButton.clicked.connect(lambda: self.deleteTestTemplate(testCard))

        # 템플릿 레이아웃에 카드 추가
        self.templateLayout.addWidget(testCard)

        # 스크롤 영역 및 위치 업데이트
        self.templateScrollWidget.adjustSize()
        self.templateScrollArea.verticalScrollBar().setValue(
            self.templateScrollArea.verticalScrollBar().maximum()
        )


    def deleteTestTemplate(self, testCard: QWidget):
        """테스트 템플릿 삭제"""
        testCard.setParent(None)
        self.templateScrollWidget.adjustSize()
        InfoBar.info(
            self.tr("Test template deleted"),
            self.tr("The selected test template has been removed."),
            parent=self,
        )

    def onTestStart(self, label: QLabel):
        """테스트 시작"""
        label.setText("Running...")
        InfoBar.success(
            self.tr("Test started"),
            self.tr("Test is now running."),
            parent=self,
        )

    def onTestStop(self, label: QLabel):
        """테스트 정지"""
        label.setText("Stopped")
        InfoBar.info(
            self.tr("Test stopped"),
            self.tr("Test has been stopped."),
            parent=self,
        )
