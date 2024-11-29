# coding:utf-8
import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel

from qfluentwidgets import (
    NavigationInterface, NavigationItemPosition, MessageBox, isDarkTheme, FluentIcon as FIF
)
from qframelesswindow import FramelessWindow, StandardTitleBar
from setting_interface import SettingInterface


class Widget(QFrame):
    """ 간단한 텍스트 기반 위젯 """
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)  # 텍스트를 가운데 정렬
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))  # 위젯의 이름 설정


class Window(FramelessWindow):
    """ 메인 윈도우 클래스 """

    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))  # 기본 타이틀 바 설정

        # 레이아웃 구성
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)  # 좌측 네비게이션 패널
        self.stackWidget = QStackedWidget(self)  # 페이지 전환을 위한 QStackedWidget

        # 각 페이지(서브 인터페이스) 생성
        # self.settingInterface = Widget('Setting Interface', self)
        self.searchInterface = Widget('Search Interface', self)
        self.settingInterface = SettingInterface(self)  # SettingInterface 추가
        
        

        # 레이아웃 및 네비게이션 초기화
        self.initLayout()
        self.initNavigation()
        self.initWindow()

    def initLayout(self):
        """ 메인 레이아웃 초기화 """
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)  # 타이틀 바 아래로 레이아웃 설정
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)  # 스택 위젯 크기 비율 조정

    def initNavigation(self):
        """ 네비게이션 메뉴 초기화 및 항목 추가 """
        self.addSubInterface(self.searchInterface, FIF.PLAY, 'Run')
        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Setup')
        
        
        # 네비게이션 확장 너비 설정
        self.navigationInterface.setExpandWidth(140)  # 최대 확장 너비 설정 (예: 200px)
        self.navigationInterface.setMinimumExpandWidth(110)  # 최소 확장 너비 설정 (예: 100px)
        
        # 현재 페이지 변경 시 호출
        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)  # 기본 페이지를 첫 번째 페이지로 설정

    def initWindow(self):
        """ 메인 윈도우 초기 설정 """
        self.resize(900, 700)  # 윈도우 크기 설정
        self.setWindowIcon(QIcon('resource/logo.png'))  # 윈도우 아이콘 설정
        self.setWindowTitle('Yong Actuator Controller')  # 윈도우 타이틀 설정
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        # 화면 중앙에 배치
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # 스타일(QSS) 적용
        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, parent=None):
        """ 서브 인터페이스 추가 """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None
        )

    def setQss(self):
        """ 스타일(QSS) 설정 """
        color = 'light'
        with open(f'resource/qss/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        """ 페이지 전환 """
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        """ 현재 페이지가 변경될 때 호출 """
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    # def showMessageBox(self):
    #     """ 메시지 박스 표시 """
    #     w = MessageBox(
    #         '지원 요청 🥰',
    #         '개발을 계속 유지하려면 지원이 필요합니다! 작은 후원이 큰 힘이 됩니다 🚀',
    #         self
    #     )
    #     w.yesButton.setText('지원하기')
    #     w.cancelButton.setText('나중에')

    #     if w.exec():
    #         QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))


if __name__ == '__main__':
    # DPI 설정 및 앱 초기화
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()  # 메인 윈도우 생성
    w.show()
    app.exec_()  # 앱 실행
