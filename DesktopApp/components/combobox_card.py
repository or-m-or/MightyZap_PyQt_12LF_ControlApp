from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import SettingCard, ComboBox, PrimaryPushButton
from serial.tools import list_ports
import logging

_logger = logging.getLogger(__name__)


class CustomComboBoxCard(SettingCard):
    """ 커스터마이징된 콤보박스 카드: 콤보박스 가로 길이 조정 가능, 콤보박스에 아이템 업데이트 가능 """
    valueChanged = pyqtSignal(str)  # 값 변경 시그널 정의

    def __init__(self, title, content, items=None, configItem=None, icon=None, parent=None, combobox_width=300):
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
        """
        super().__init__(icon=icon, title=title, content=content, parent=parent)

        self.configItem = configItem  # 설정 객체 저장
        self.comboBox = ComboBox(self)
        self.comboBox.setPlaceholderText("Select a Device")  # 초기 Placeholder 설정
        self.comboBox.addItems(items or [])               # 초기 아이템 추가
        self.comboBox.setFixedSize(combobox_width, 30)               # 콤보박스 크기 설정
        self.comboBox.setCurrentIndex(-1)                 # 초기 선택 없음

        # 설정 객체와 초기 값 동기화
        if self.configItem:
            self.comboBox.setCurrentText(self.configItem.value)  # 설정 값으로 초기화
            self.configItem.valueChanged.connect(self.onConfigItemChanged)

        # 콤보박스 값 변경 시 valueChanged 시그널 발생
        self.comboBox.currentTextChanged.connect(self.onComboBoxChanged)

        # 레이아웃 구성 (텍스트와 콤보박스 분리)
        self._initLayout()

    def _initLayout(self):
        """카드 레이아웃 초기화"""
        cardLayout = self.layout()
        cardLayout.setContentsMargins(16, 8, 16, 8)  # 왼쪽/ 상단/ 오른족/ 하단 여백
        cardLayout.setSpacing(1)  # 위젯 간 간격 아이콘과 제목-내용 사이 간격 조정
        cardLayout.addStretch(5)  # 제목, 내용 이후 공간 확장

        cardLayout.addWidget(self.comboBox)

    def setOptions(self, items):
        """옵션 리스트를 업데이트"""
        self.comboBox.clear()   # 기존 옵션 제거
        self.comboBox.addItems(items)  # 새 옵션 추가
        self.comboBox.setCurrentIndex(0)  # 초기 선택 값 지정

    def addOption(self, item):
        """새 옵션 추가"""
        if item not in [self.comboBox.itemText(i) for i in range(self.comboBox.count())]:
            self.comboBox.addItem(item)

    def removeOption(self, item):
        """옵션 제거"""
        index = self.comboBox.findText(item)
        if index != -1:
            self.comboBox.removeItem(index)

    def currentValue(self):
        """현재 선택된 값을 반환"""
        return self.comboBox.currentText()

    def onComboBoxChanged(self, value):
        """콤보박스 값 변경 시 호출"""
        if self.configItem:
            self.configItem.value = value  # 설정 객체와 값 동기화
        self.valueChanged.emit(value)

    def onConfigItemChanged(self, value):
        """설정 객체 값 변경 시 호출"""
        self.comboBox.setCurrentText(value)
