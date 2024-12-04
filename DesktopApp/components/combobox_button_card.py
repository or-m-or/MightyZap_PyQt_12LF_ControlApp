from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout
from qfluentwidgets import PrimaryPushButton
from components.combobox_card import CustomComboBoxCard  # CustomComboBoxCard를 가져옴


class CustomComboBoxButtonCard(CustomComboBoxCard):
    """CustomComboBoxCard 확장: 버튼 추가"""
    
    def __init__(self, title, content, items=None, configItem=None, icon=None, parent=None, combobox_width=300, button_text="Action", button_width=80):
        """
        Parameters
        ----------
        title : str
            카드 제목
        content : str
            카드 내용
        items : list[str]
            콤보박스에 표시할 초기 옵션
        configItem : ConfigItem
            설정 값과 동기화할 설정 객체
        icon : FluentIcon
            카드의 아이콘
        parent : QWidget
            부모 위젯
        width : int
            콤보박스의 가로 길이
        button_text : str
            버튼에 표시할 텍스트
        """
        # 기존 CustomComboBoxCard 초기화
        super().__init__(title, content, items, configItem, icon, parent, combobox_width)

        # 버튼 추가
        self.button = PrimaryPushButton(button_text, self)
        self.button.setFixedSize(button_width, 30)  # 버튼 크기 설정

        # 레이아웃 재구성
        self._initButtonLayout()

    def _initButtonLayout(self):
        """콤보박스와 버튼 레이아웃 초기화"""
        # 기존 콤보박스 레이아웃을 재구성
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 1, 8)  # 여백 설정
        layout.addWidget(self.comboBox)
        layout.addWidget(self.button)
        layout.setSpacing(8)  # 콤보박스와 버튼 간 간격 설정

        # 기존 카드의 레이아웃을 교체
        cardLayout = self.layout()
        cardLayout.addLayout(layout)

    def setButtonAction(self, callback):
        """버튼 클릭 시 호출될 콜백 설정"""
        self.button.clicked.connect(callback)



class CustomComboBoxTwoButtonCard(CustomComboBoxCard):
    """CustomComboBoxCard 확장: 버튼 2개 추가"""
    
    def __init__(
        self, 
        title, 
        content, 
        items=None, 
        configItem=None, 
        icon=None, 
        parent=None, 
        combobox_width=300, 
        button1_text="Button 1", 
        button2_text="Button 2", 
        button_width=80
    ):
        """
        Parameters
        ----------
        title : str
            카드 제목
        content : str
            카드 내용
        items : list[str]
            콤보박스에 표시할 초기 옵션
        configItem : ConfigItem
            설정 값과 동기화할 설정 객체
        icon : FluentIcon
            카드의 아이콘
        parent : QWidget
            부모 위젯
        combobox_width : int
            콤보박스의 가로 길이
        button1_text : str
            첫 번째 버튼에 표시할 텍스트
        button2_text : str
            두 번째 버튼에 표시할 텍스트
        button_width : int
            두 버튼의 가로 길이
        """
        # 기존 CustomComboBoxCard 초기화
        super().__init__(title, content, items, configItem, icon, parent, combobox_width)

        # 첫 번째 버튼 추가
        self.button1 = PrimaryPushButton(button1_text, self)
        self.button1.setFixedSize(button_width, 30)  # 첫 번째 버튼 크기 설정

        # 두 번째 버튼 추가
        self.button2 = PrimaryPushButton(button2_text, self)
        self.button2.setFixedSize(button_width, 30)  # 두 번째 버튼 크기 설정

        # 레이아웃 재구성
        self._initTwoButtonLayout()

    def _initTwoButtonLayout(self):
        """콤보박스와 두 버튼의 레이아웃 초기화"""
        # 기존 콤보박스 레이아웃을 재구성
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 1, 8)  # 여백 설정
        layout.addWidget(self.comboBox)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.setSpacing(8)  # 콤보박스와 버튼 간 간격 설정

        # 기존 카드의 레이아웃을 교체
        cardLayout = self.layout()
        cardLayout.addLayout(layout)

    def setButton1Action(self, callback):
        """첫 번째 버튼 클릭 시 호출될 콜백 설정"""
        self.button1.clicked.connect(callback)

    def setButton2Action(self, callback):
        """두 번째 버튼 클릭 시 호출될 콜백 설정"""
        self.button2.clicked.connect(callback)
