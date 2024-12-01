import resource_rc
import sys
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import (
    NavigationItemPosition, 
    MessageBox, 
    FluentWindow, 
    NavigationAvatarWidget, 
    SubtitleLabel, 
    setFont, 
    InfoBadge, 
    InfoBadgePosition, 
    FluentBackgroundTheme,
    SplashScreen,
    SystemThemeListener
)
from qfluentwidgets import FluentIcon as FIF
from view.settings_interface import SettingInterface
from view.testing_interface import TestInterface
from common.signal_bus import signalBus
from common.translator import Translator
from common.config import cfg


class Widget(QFrame):
    """ 서브 인터페이스를 표현하는 위젯 클래스 """

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)  # 텍스트 라벨 생성
        self.hBoxLayout = QHBoxLayout(self)  # 수평 레이아웃 생성

        setFont(self.label, 24)  # 라벨의 폰트 크기를 24로 설정
        self.label.setAlignment(Qt.AlignCenter)  # 라벨 텍스트를 가운데 정렬
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)  # 라벨을 레이아웃에 추가
        self.setObjectName(text.replace(' ', '-'))  # 객체 이름 설정 (공백을 '-'로 대체)


class MainWindow(FluentWindow):
    """ 메인 애플리케이션 윈도우 클래스 """

    def __init__(self):
        super().__init__()
        self.initWindow()  # 윈도우 초기화
        self.setWindowTitle("Actuator Controller")
        
        # 시스템 테마 리스너
        self.themeListener = SystemThemeListener(self)
        
        # 서브 인터페이스 생성
        self.homeInterface = Widget('Home', self)
        self.TestInterface = TestInterface(self) # Widget('Folder Interface', self)
        self.settingInterface = SettingInterface(self) # Widget('Setting Interface', self)
        
        # UI에서 샘플 카드 화면전환/ 사용자 상호작용
        self.connectSignalToSlot()

        self.initNavigation()  # 네비게이션 초기화
        self.splashScreen.finish()
        
        # start theme listener
        self.themeListener.start()
        
        
    def connectSignalToSlot(self):
        # signalBus.switchToSampleCard.connect(self.switchToSample)
        ...
        
    def initNavigation(self):
        """ 네비게이션 인터페이스 초기화 및 항목 추가 """
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))  # 홈 인터페이스                
        self.addSubInterface(self.TestInterface, FIF.PLAY, self.tr('Testing'))        
        self.navigationInterface.addSeparator()  # 구분선 추가
        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('Setup')) # 설정 인터페이스

        # NOTE: 아크릴 효과를 활성화하려면 주석 해제
        self.navigationInterface.setAcrylicEnabled(True)
        self.navigationInterface.setExpandWidth(180) # 확장 너비 : 180px
        

    def initWindow(self):
        """ 메인 윈도우 초기화 """
        self.resize(900, 700)  # 윈도우 크기 설정
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))  # 윈도우 아이콘 설정
        self.setWindowTitle('PyQt-Fluent-Widgets')  # 윈도우 제목 설정

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()
        
        # 창을 화면 중앙으로 이동
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        """ 윈도우 크기 변경되 ㄹ때마다 스플래시 화면 맞춤 """
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())
    
    def closeEvent(self, e):
        """ 윈도우 닫힐 때 호출, 리소스 삭제 """
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()
        

    # def switchToSample(self, routeKey, index):
    #     """ switch to sample """
    #     interfaces = self.findChildren(GalleryInterface)
    #     for w in interfaces:
    #         if w.objectName() == routeKey:
    #             self.stackedWidget.setCurrentWidget(w, False)
    #             w.scrollToCard(index)

