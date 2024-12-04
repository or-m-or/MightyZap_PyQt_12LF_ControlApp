from PyQt5.QtCore import pyqtSignal
# from PyQt5.QtWidgets import QSpinBox
from qfluentwidgets import SettingCard, SpinBox
from core.config import qconfig, setup_logger

_logger = setup_logger(name="MainApp", level='INFO')


class CustomSpinBoxCard(SettingCard):
    """ 사용자 정의 SpinBox 카드 """
    valueChanged = pyqtSignal(int)  # 값 변경 시그널

    def __init__(self, title, content, minimum=0, maximum=100, default=0, icon=None, parent=None, width=200, configItem=None):
        """
        Parameters
        ----------
        title : str
            카드 제목
        content : str
            카드 내용
        minimum : int
            SpinBox의 최소값
        maximum : int
            SpinBox의 최대값
        default : int
            SpinBox의 초기값
        icon : FluentIcon
            카드 아이콘
        parent : QWidget
            부모 위젯
        width : int
            SpinBox의 가로 길이
        configItem : ConfigItem
            설정 값을 저장하는 ConfigItem 객체
        """
        super().__init__(icon=icon, title=title, content=content, parent=parent)

        self.configItem = configItem
        self.spinBox = SpinBox(self)
        self.spinBox.setRange(minimum, maximum)
        self.spinBox.setValue(default if not configItem else configItem.value)
        self.spinBox.setFixedSize(width, 30)
        self.spinBox.setAccelerated(True)
        self.spinBox.valueChanged.connect(self._onValueChanged)  # 값 변경 시그널 연결

        self._initLayout()

    def _initLayout(self):
        """카드 레이아웃 초기화"""
        cardLayout = self.layout()
        cardLayout.setContentsMargins(16, 8, 16, 8)
        cardLayout.setSpacing(1)
        cardLayout.addStretch(5)  # 왼쪽 여백
        cardLayout.addWidget(self.spinBox)

    def setValue(self, value):
        """SpinBox 값 설정"""
        self.spinBox.setValue(value)
        if self.configItem:
            qconfig.set(self.configItem, value)  # 즉시 config.json에 반영

    def value(self):
        """SpinBox 값 반환"""
        return self.spinBox.value()

    def _onValueChanged(self, value):
        """SpinBox 값 변경 시 호출"""
        self.valueChanged.emit(value)
        if self.configItem:
            qconfig.set(self.configItem, value)  # 즉시 config.json에 반영
            _logger.info(f"ConfigItem updated: {self.configItem.key} = {value}")
