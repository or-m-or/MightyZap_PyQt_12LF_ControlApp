from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton, QSizePolicy
from qfluentwidgets import (
    ExpandGroupSettingCard,
    FluentIcon as FIF
)
from qfluentwidgets import (
    SettingCard, 
    ComboBox, 
    PushButton, 
    BodyLabel, 
    TitleLabel,
    PrimaryPushButton,
    StrongBodyLabel
)

class BoardSettingCard(ExpandGroupSettingCard):
    """ 보드 설정 카드 """
    searchRequested = pyqtSignal()  # 검색 버튼 클릭 시
    deviceSelected = pyqtSignal(str)  # 장치 선택 시
    connectRequested = pyqtSignal(str)  # 연결 버튼 클릭 시
    disconnectRequested = pyqtSignal()  # 연결 해제 버튼 클릭 시
    
    def __init__(self, parent=None):
        super().__init__(
            FIF.CONNECT,  # 아이콘
            "Board Setting",  # 제목
            "Configure board-related settings",  # 설명
            parent,
        )

        # 첫 번째 그룹: 콤보박스와 버튼
        self.deviceComboBox = ComboBox(self)
        self.deviceComboBox.setFixedWidth(180)  # 콤보박스 너비 설정
        self.searchButton = PushButton("Search", self)
        self.searchButton.setFixedSize(80, 30)  # 버튼 크기 설정
        self.connectButton = PrimaryPushButton("Connect", self)
        self.connectButton.setFixedSize(80, 30)
        self.deviceGroup = self._initComboBoxTwoButtonGroup("Search Device", self.deviceComboBox, self.searchButton, self.connectButton)

        # 두 번째 그룹: Baudrate 설정
        self.baudrateComboBox = ComboBox(self)
        self.baudrateComboBox.addItems(["9600", "19200", "57600", "115200"])
        self.baudrateComboBox.setFixedWidth(100)
        self.baudrateGroup = self._initSingleWidgetGroup("Baudrate", self.baudrateComboBox)

        # 세 번째 그룹: Connect와 Disconnect 버튼
        self.connectionComboBox = ComboBox(self)
        self.connectionComboBox.setFixedWidth(250)
        self.disconnectButton = PrimaryPushButton("Disconnect", self)
        self.disconnectButton.setFixedSize(100, 30)
        self.connectionGroup = self._initComboBoxButtonGroup("Connection", self.connectionComboBox, self.disconnectButton)

        # 그룹 추가
        self.addGroupWidget(self.deviceGroup)
        self.addGroupWidget(self.baudrateGroup)
        self.addGroupWidget(self.connectionGroup)
        
        # 시그널 연결
        self.searchButton.clicked.connect(self._onSearchRequested)
        self.deviceComboBox.currentTextChanged.connect(self._onDeviceSelected)
        self.connectButton.clicked.connect(self._onConnectRequested)
        self.disconnectButton.clicked.connect(self._onDisconnectRequested)
        

    def _initComboBoxButtonGroup(self, label_text, comboBox, button):
        """ 콤보박스와 버튼이 포함된 그룹 위젯 생성 """
        group = QWidget()
        layout = QHBoxLayout(group)
        layout.setContentsMargins(48, 12, 48, 12)
        label = StrongBodyLabel(label_text, group)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(comboBox)
        layout.addWidget(button)
        return group

    def _initSingleWidgetGroup(self, label_text, widget):
        """ 단일 위젯이 포함된 그룹 위젯 생성 """
        group = QWidget()
        layout = QHBoxLayout(group)
        layout.setContentsMargins(48, 12, 48, 12)
        label = StrongBodyLabel(label_text, group)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)
        return group

    def _initComboBoxTwoButtonGroup(self, label_text, comboBox, button1, button2):
        """ 콤보박스와 두 개의 버튼이 포함된 그룹 위젯 생성 """
        group = QWidget()
        layout = QHBoxLayout(group)
        layout.setContentsMargins(48, 12, 48, 12)
        label = StrongBodyLabel(label_text, group)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(comboBox)
        layout.addWidget(button1)
        layout.addWidget(button2)
        return group

    def toggleExpansion(self):
        """ 카드 펼치기/접기 상태에 따라 위젯 표시/숨김 """
        super().toggleExpansion()
        expanded = self.isExpanded()
        for widget in [self.deviceGroup, self.baudrateGroup, self.connectionGroup]:
            widget.setVisible(expanded)

    def _onSearchRequested(self):
        """ 검색 버튼 클릭 시 """
        self.searchRequested.emit()

    def _onDeviceSelected(self, device):
        """ 장치 선택 시 """
        self.deviceSelected.emit(device)

    def _onConnectRequested(self):
        """ 연결 버튼 클릭 시 """
        device = self.connectionComboBox.currentText()
        self.connectRequested.emit(device)

    def _onDisconnectRequested(self):
        """ 연결 해제 버튼 클릭 시 """
        self.disconnectRequested.emit()