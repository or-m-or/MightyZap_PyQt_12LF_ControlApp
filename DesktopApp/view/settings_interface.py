import resource_rc
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
    isDarkTheme
)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar, SpinBox
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog

from common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from common.signal_bus import signalBus
from common.style_sheet import StyleSheet

from qfluentwidgets import ExpandGroupSettingCard, PrimaryPushButton, PushButton, ComboBoxSettingCard, SettingCard
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QComboBox
from qfluentwidgets import LineEdit, PrimaryPushSettingCard, SettingCardGroup, BodyLabel
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class SettingInterface(ScrollArea):
    """ 설정 인터페이스 클래스 """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()                          # 스크롤 가능한 메인 위젯 생성
        self.expandLayout = ExpandLayout(self.scrollWidget)    # 확장 가능한 레이아웃 생성
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(20, 40, 20, 20)   # 전체 여백 설정
        
         # "설정" 라벨
        self.settingLabel = QLabel(self.tr("Setup"), self.scrollWidget) 
        self.settingLabel.setObjectName('settingLabel')  # QSS 적용을 위해 ObjectName 설정
        self.settingLabel.setFixedHeight(50)                                # 높이 지정으로 글자 잘림 방지
        self.expandLayout.addWidget(self.settingLabel)   # 라벨을 스크롤 레이아웃에 추가
        
        # [ 보드 설정 그룹 ] 초기화
        self.BoardSettingGroup = SettingCardGroup( self.tr("Board Setting"), self.scrollWidget )
        # Search 버튼
        self.searchBtnCard = PrimaryPushSettingCard(
            text=self.tr("Search"),
            icon=FIF.SEARCH,
            title=self.tr("Search for Ports"),
            content=self.tr("Click the Search button to search for devices connected to the serial port."),
            parent=self.BoardSettingGroup
        )
        # Port
        self.portCard = OptionsSettingCard(
            configItem=cfg.port,
            icon=FIF.CONNECT,
            title=self.tr("Select a Port"),
            content=self.tr("Choose a serial port to connect to."),
            texts=cfg.port.options,  # 초기 옵션을 텍스트로 표시
            parent=self.BoardSettingGroup
        )
        # Baudrate
        self.baudrateCard = ComboBoxSettingCard(
            configItem=cfg.baudrate,
            icon=FIF.SPEED_HIGH,
            title=self.tr("Baudrate"),
            content=self.tr("Select the serial communication speed between your device and PC."),
            texts=["9600", "19200", "57600", "115200"],
            parent=self.BoardSettingGroup
        )
        # Connect 버튼
        self.connectBtnCard = PrimaryPushSettingCard(
            text=self.tr("Connect"),
            icon=FIF.CHEVRON_DOWN_MED,
            title=self.tr("Connect to Board"),
            content=self.tr("Attempts to connect with the selected device."),
            parent=self.BoardSettingGroup
        )

        # [ 조그 설정 그룹 ]
        self.JogSettingGroup = SettingCardGroup(self.tr("Jog Setting"), self.scrollWidget)
        # 조그 이동 슬라이더
        self.rangeSettingCard = RangeSettingCard(
            configItem=cfg.rangeValue,  # Config에서 정의된 값 사용
            icon=FIF.CARE_RIGHT_SOLID,
            title=self.tr("Acuator Location"),
            content=self.tr("You can move the slider to move the actuator."),
            parent=self.JogSettingGroup
        )
        # Home 버튼
        self.homeButtonCard = PushSettingCard(
            text=self.tr("Home"),
            icon=FIF.HOME,
            title=self.tr("Return Home"),
            content=self.tr("Reset the location to the home point."),
            parent=self.JogSettingGroup
        )
        # Position 1 입력 필드
        self.position1Card = SettingCard(
            icon=FIF.LEFT_ARROW,
            title=self.tr("Pos 1"),
            content=self.tr("Enter the starting point for the Actuator behavior."),
            parent=self.JogSettingGroup
        )
        self.__addCustomLineEditCard(self.position1Card, "Position 1")
        # Position 2 입력 필드
        self.position2Card = SettingCard(
            icon=FIF.RIGHT_ARROW,
            title=self.tr("Pos 2"),
            content=self.tr("Enter the arrival point for the Actuator behavior."),
            parent=self.JogSettingGroup
        )
        self.__addCustomLineEditCard(self.position2Card, "Position 2")
        
        # [ 테스트 설정 그룹 ]
        self.TestSettingGroup = SettingCardGroup(self.tr("Test Setting"), self.scrollWidget)        
        # 테스트 횟수
        test_count_title = "Test Counts"
        self.testCountCard = SettingCard(
            icon=FIF.ROTATE,
            title=self.tr(test_count_title),
            content=self.tr("Fill in the number of times you want to go back and forth between Location1 and Location2 in one test."),
            parent=self.TestSettingGroup
        )  
        self.__addCustomLineEditCard(self.testCountCard, test_count_title)
        
        
        # [ 액추에이터 설정 그룹 ]
        self.ActuatorSettingGroup = SettingCardGroup(self.tr("Actuator Setting"), self.scrollWidget)
        # 반영구 속도 설정
        self.globalSpeedSettingCard = SettingCard(
            icon=FIF.SETTING,
            title=self.tr("General Speed Limit"),
            content=self.tr("Set the speed of the actuator (0-1023) (this setting is semi-permanently stored in the actuator)."),
            parent=self.ActuatorSettingGroup
        )
        self.__addCustomSpinBoxCard(card=self.globalSpeedSettingCard, limit=1023)
        # 임시 속도 설정
        self.tempSpeedSettingCard = SettingCard(
            icon=FIF.SETTING,
            title=self.tr("Temp Speed Limit"),
            content=self.tr("Set the speed of the actuator (0-1023) (this setting is reset on device restart)"),
            parent=self.ActuatorSettingGroup
        )
        self.__addCustomSpinBoxCard(card=self.tempSpeedSettingCard, limit=1023)
        # 전진 제한값 설정
        self.bwdLimitSettingCard = SettingCard(
            icon=FIF.SETTING,
            title=self.tr("BWD Limit"),
            content=self.tr("Sets the maximum travel limit for the actuator in the reverse direction."),
            parent=self.ActuatorSettingGroup
        )
        self.__addCustomSpinBoxCard(card=self.bwdLimitSettingCard, limit=4095)
        # 후진 제한값 설정
        self.fwdLimitSettingCard = SettingCard(
            icon=FIF.SETTING,
            title=self.tr("FWD Limit"),
            content=self.tr("Sets the maximum travel limit for the actuator in the forward direction."),
            parent=self.ActuatorSettingGroup
        )
        self.__addCustomSpinBoxCard(card=self.fwdLimitSettingCard, limit=4095)
        
        
        # [ 개인 설정 ]
        self.personalGroup = SettingCardGroup( self.tr('Personalization'), self.scrollWidget )
        # 테마 선택
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,  # 현재 테마
            FIF.BRUSH, 
            self.tr('Theme'),  
            self.tr("Change the color of an application"), 
            texts=[
                self.tr('Light'), self.tr('Dark'), self.tr('Use system setting')
            ],
            parent=self.personalGroup
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
        self.languageCard = ComboBoxSettingCard(
            cfg.language,  # 현재 언어 설정
            FIF.LANGUAGE,  
            self.tr('Language'),  
            self.tr('Set your preferred language'),  
            texts=['Korean', 'English', self.tr('Use system setting')],  
            parent=self.personalGroup
        )

        # [ 앱 정보 ]
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)  # "정보" 그룹
        # 도움말 하이퍼링크
        self.helpCard = HyperlinkCard(
            HELP_URL,                   # 도움말 URL
            self.tr('Open help page'),  
            FIF.HELP,                   
            self.tr('Help'),            
            self.tr('Check out 0000 how-to guide'),  # 설명
            self.aboutGroup
        )

        self.__initWidget()  # 위젯 초기화

    def __addCustomLineEditCard(self, card, title):
        """ 커스텀 카드 1: LineEdit """
        cardLayout = card.layout()
        cardLayout.setContentsMargins(16, 8, 16, 8)
        cardLayout.setSpacing(12)
        inputField = LineEdit(card)
        inputField.setFixedSize(200, 30)
        inputField.setClearButtonEnabled(True)
        inputField.setPlaceholderText(self.tr(f"Enter {title.lower()}"))
        # 텍스트 박스를 약간 오른쪽으로 이동
        cardLayout.addStretch(1)
        cardLayout.addWidget(inputField)
        cardLayout.addStretch(3)
        # 오른쪽 정렬을 위해 Stretch 추가
        cardLayout.addStretch()
        cardLayout.addWidget(inputField)
    
    def __addCustomSpinBoxCard(self, card, limit):
        """ 커스텀 카드 2: SpinBox """
        cardLayout = card.layout()
        cardLayout.setContentsMargins(16, 8, 16, 8)
        cardLayout.setSpacing(12)
        spinBox = SpinBox(card)
        spinBox.setFixedSize(200, 30)
        spinBox.setRange(0, limit)  # 범위 설정
        spinBox.setAccelerated(True)  # 빠른 입력 활성화
        cardLayout.addWidget(spinBox)
        self.ActuatorSettingGroup.addSettingCard(card)
        
    def __initWidget(self):
        """ 설정 인터페이스 전체 위젯 초기화 """
        self.resize(1000, 800)  # 창 크기
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 가로 스크롤 비활성화
        # self.setViewportMargins(0, 80, 0, 20)   # 뷰포트 여백
        self.setViewportMargins(0, 0, 0, 0)   # 뷰포트 여백
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
        self.BoardSettingGroup.addSettingCard(self.searchBtnCard)  # [Board] 포트 검색 버튼
        self.BoardSettingGroup.addSettingCard(self.portCard)       # [Board] 포트 목록 컴보박스
        self.BoardSettingGroup.addSettingCard(self.baudrateCard)   # [Board] 연결속도 선택 박스
        self.BoardSettingGroup.addSettingCard(self.connectBtnCard) # [Board] 연결 버튼
        self.JogSettingGroup.addSettingCard(self.rangeSettingCard) # [JOG] 조그 이동 슬라이더
        self.JogSettingGroup.addSettingCard(self.homeButtonCard)   # [JOG] 조그 원점 이동
        self.JogSettingGroup.addSettingCard(self.position1Card)    # [JOG] 포지션1위치 지정
        self.JogSettingGroup.addSettingCard(self.position2Card)    # [JOG] 포지션2위치 지정
        self.TestSettingGroup.addSettingCard(self.testCountCard)   # [Test] 테스트 횟수
        self.ActuatorSettingGroup.addSettingCard(self.globalSpeedSettingCard) # [Actu] 액추에이터 반영구 속도
        self.ActuatorSettingGroup.addSettingCard(self.tempSpeedSettingCard)   # [Actu] 액추에이터 임시 속도
        self.ActuatorSettingGroup.addSettingCard(self.bwdLimitSettingCard)    # [Actu] 액추에이터 후진 제한 위치
        self.ActuatorSettingGroup.addSettingCard(self.fwdLimitSettingCard)    # [Actu] 액추에이터 전진 제한 위치
        self.personalGroup.addSettingCard(self.themeCard)          # [Personal] "테마" 선택
        # self.personalGroup.addSettingCard(self.zoomCard)           # [Personal] "확대/축소" 선택
        self.personalGroup.addSettingCard(self.languageCard)       # [Personal] "언어" 선택
        self.aboutGroup.addSettingCard(self.helpCard)              # [About] "도움말" 카드

        # 그룹 -> 레이아웃
        self.expandLayout.setSpacing(28)  # 그룹 간 간격
        self.expandLayout.setContentsMargins(36, 10, 36, 0)  # 여백
        self.expandLayout.addWidget(self.BoardSettingGroup)  # [Board]
        self.expandLayout.addWidget(self.JogSettingGroup)    # [JOG]
        self.expandLayout.addWidget(self.TestSettingGroup)   # [Test]
        self.expandLayout.addWidget(self.ActuatorSettingGroup) # [Actu]
        self.expandLayout.addWidget(self.personalGroup)      # [Personal]
        self.expandLayout.addWidget(self.aboutGroup)         # [About]

        
        

    # [ 로직 ]
    #################################################################################################
        
    def __showRestartTooltip(self):
        """ 재시작 알림 표시 """
        InfoBar.success(
            self.tr('Updated successfully'),  # "성공적으로 업데이트됨"
            self.tr('Configuration takes effect after restart'),  # "설정은 재시작 후 적용됨"
            duration=1500,  # 표시 시간 (1.5초)
            parent=self
        )


    def __connectSignalToSlot(self):
        """ 시그널과 슬롯 연결 """
        cfg.appRestartSig.connect(self.__showRestartTooltip)  # 설정 업데이트 후 재시작 알림 표시

        # Search 버튼 이벤트 연결
        self.searchBtnCard.clicked.connect(self.__searchPorts)
        self.connectBtnCard.clicked.connect(self.__onConnectClicked)
        
        # "개인 설정" 관련
        cfg.themeChanged.connect(setTheme)  # 테마 변경 시 테마 적용,

    
    #################################################################################################

    def __searchPorts(self):
        """ 사용 가능한 포트를 검색하고 ComboBox 업데이트 """
        # 여기서 실제 사용 가능한 포트를 검색하는 로직 추가
        availablePorts = ["COM1", "COM2", "COM3"]  # 예제 값

        # OptionsConfigItem의 options 업데이트
        cfg.port.options = availablePorts + availablePorts

        # ComboBoxSettingCard에 새 옵션 반영
        self.portCard.setOptions(cfg.port.options)  # UI에 옵션 업데이트
        print(f"Available ports updated: {availablePorts}")
        
        
    def __onConnectClicked(self):
        """ Connect 버튼 클릭 시 호출 """
        selectedPort = cfg.port.value  # 선택된 포트 가져오기

        if selectedPort == "None":
            print("No port selected!")
            return

        print(f"Connecting to {selectedPort}...")

    
    def __onTestCountChanged(self, text):
        """ 테스트 횟수 입력 변경 이벤트 """
        print(f"Test count changed: {text}")

    def __onRunTestClicked(self):
        """ 테스트 실행 버튼 클릭 이벤트 """
        testCount = self.testCountInput.text()
        print(f"Running test with count: {testCount}")