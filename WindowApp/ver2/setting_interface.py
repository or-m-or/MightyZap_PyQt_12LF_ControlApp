# coding:utf-8
from config import cfg, DEFAULT_VALUES
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, RangeSettingCard, PushSettingCard,
                            ColorSettingCard, HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme, MessageBox)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog
from serial.tools import list_ports
from actuator import Actuator
import serial
import re



class SettingInterface(ScrollArea):
    """ 설정 화면 인터페이스 클래스 """

    # 시그널 정의
    checkUpdateSig = pyqtSignal()  # 업데이트 확인 시그널
    acrylicEnableChanged = pyqtSignal(bool)  # 아크릴 효과 활성화 여부 변경 시그널
    downloadFolderChanged = pyqtSignal(str)  # 다운로드 폴더 변경 시그널
    minimizeToTrayChanged = pyqtSignal(bool)  # 트레이 최소화 여부 변경 시그널

    def __init__(self, parent=None):
        """ 초기화 """
        super().__init__(parent=parent)
        self.actuators = []
        self.scrollWidget = QWidget()  # 스크롤 가능한 위젯 생성
        self.expandLayout = ExpandLayout(self.scrollWidget)  # 확장 레이아웃 설정
        
        # self.__connectSignalToSlot() # 시그널 연결

        # 설정 화면 제목
        self.settingLabel = QLabel(self.tr("Setup"), self)
        self.BoardGroup = SettingCardGroup(self.tr('Board Setting'), self.scrollWidget) # 보드 설정 그룹
        
        self.PortCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Port'),
            self.tr("Select the port connected to your PC"),
            texts=[],
            parent=self.BoardGroup
        )
        
        self.BaudrateCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Baudrate'),
            self.tr('Select the Baudrate between the board and PC'),
            texts=["115200", "57600", "19200", self.tr("9600")],
            parent=self.BoardGroup
        )
        
        # Scan Ports 버튼 추가
        self.ScanButton = PushSettingCard(
            self.tr('Scan Ports'),
            FIF.SEARCH,
            self.tr('Scan'),
            parent=self.BoardGroup
        )
        self.ScanButton.clicked.connect(self.display_serial_ports)  # 버튼 클릭 시 display_serial_ports 호출

        self._initWidget()

    def _initWidget(self):
        """ 위젯 초기화 """
        self.resize(1000, 800)  # 초기 창 크기
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 수평 스크롤바 비활성화
        self.setViewportMargins(0, 120, 0, 20)  # 여백 설정
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # 스타일 및 레이아웃 초기화
        self._setQss()
        self._initLayout()
        # self.__connectSignalToSlot()

    def _initLayout(self):
        """ 레이아웃 초기화 """
        self.settingLabel.move(60, 63)  # 제목 라벨 위치 설정

        # 설정 그룹에 카드 추가
        self.BoardGroup.addSettingCard(self.PortCard)
        self.BoardGroup.addSettingCard(self.BaudrateCard)
        self.BoardGroup.addSettingCard(self.ScanButton)  # Scan Ports 버튼 추가
        
        # 그룹을 레이아웃에 추가
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.BoardGroup)

    def _setQss(self):
        """ 스타일 시트 설정 """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'light'  # 테마 기본값
        with open(f'resource/qss/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    # def __connectSignalToSlot(self):
        # """ 시그널과 슬롯 연결 """
        # cfg.appRestartSig.connect(self.__showRestartTooltip)
        # cfg.themeChanged.connect(self.__onThemeChanged)

        # 보드 설정
#        self.PortCard.clicked.connect(self.display_serial_ports)
        
        # 개인화 설정
        # self.enableAcrylicCard.checkedChanged.connect(
        #     self.acrylicEnableChanged)
        # self.PortCard.colorChanged.connect(setThemeColor)

        
        # 가사 설정
        # self.deskLyricFontCard.clicked.connect(self.__onDeskLyricFontCardClicked)

        # 메인 패널 설정
        # self.minimizeToTrayCard.checkedChanged.connect(
        #     self.minimizeToTrayChanged)

        # # 어플리케이션 정보
        # self.aboutCard.clicked.connect(self.checkUpdateSig)
        # self.feedbackCard.clicked.connect(
        #     lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
                
                
    def display_serial_ports(self):
        """ 탐색된 직렬 포트를 PortCard에 추가 """
        ports = list_ports.comports()  # 연결된 모든 포트와 상세 정보 가져오기
        port_list = [f"{port.device} ({port.description})" for port in ports]  # 포트와 설명 추가
        if not port_list:
            port_list = [self.tr("No Ports Found")]  # 포트가 없는 경우 기본값

        for port in port_list:
            
            self.PortCard.addWidget(port)

