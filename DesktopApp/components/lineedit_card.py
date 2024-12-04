from PyQt5.QtCore import pyqtSignal
from qfluentwidgets import LineEdit, SettingCard, RangeConfigItem, OptionsConfigItem
from core.config import setup_logger, qconfig

_logger = setup_logger(name="MainApp", level='INFO')


class CustomLineEditCard(SettingCard):
    """ 사용자 정의 LineEdit 카드 """
    textChanged = pyqtSignal(str)  # 텍스트 변경 시그널
    invalidInput = pyqtSignal(str)  # 유효하지 않은 입력값 시그널

    def __init__(self, title, content, placeholder="", icon=None, parent=None, width=200, configItem=None):
        """
        Parameters
        ----------
        title : str
            카드 제목
        content : str
            카드 내용
        placeholder : str
            LineEdit의 Placeholder 텍스트
        icon : FluentIcon
            카드 아이콘
        parent : QWidget
            부모 위젯
        width : int
            LineEdit의 가로 길이
        configItem : ConfigItem
            설정 값을 저장하는 ConfigItem 객체
        """
        super().__init__(icon=icon, title=title, content=content, parent=parent)

        self.configItem = configItem
        self.lineEdit = LineEdit(self)
        self.lineEdit.setPlaceholderText(placeholder)
        self.lineEdit.setFixedSize(width, 30)
        self.lineEdit.setClearButtonEnabled(True)  # Clear 버튼 활성화
        self.lineEdit.textChanged.connect(self._onTextChanged)  # 텍스트 변경 시그널 연결

        if self.configItem:
            # ConfigItem 값으로 초기화
            self.setValue(self.configItem.value)

        self._initLayout()

    def _initLayout(self):
        """카드 레이아웃 초기화"""
        cardLayout = self.layout()
        cardLayout.setContentsMargins(16, 8, 16, 8)
        cardLayout.setSpacing(1)
        cardLayout.addStretch(5)  # 왼쪽 여백
        cardLayout.addWidget(self.lineEdit)  # LineEdit 추가

    def setText(self, text):
        """LineEdit 텍스트 설정"""
        self.lineEdit.setText(text)
        if self.configItem:
            try:
                # ConfigItem 값 업데이트
                value = int(text) if text.isdigit() else 0
                qconfig.set(self.configItem, value)  # 즉시 config.json에 반영
            except ValueError:
                _logger.warning(f"Invalid text for ConfigItem: {text}, defaulting to 0")
                qconfig.set(self.configItem, 0)

    def text(self):
        """LineEdit 텍스트 반환"""
        return self.lineEdit.text()

    def setValue(self, value):
        """ConfigItem 값으로 LineEdit 초기화"""
        self.lineEdit.setText(str(value))
        if self.configItem:
            qconfig.set(self.configItem, value)  # 즉시 config.json에 반영

    def _onTextChanged(self, text):
        """텍스트 변경 시 호출"""
        self.textChanged.emit(text)  # 텍스트 변경 시그널 발행
        if not text.strip():  # 입력값이 공백이면 무시
            return
        if not text.isdigit():  # 숫자가 아닌 경우 invalidInput 시그널 발행
            self.invalidInput.emit(text)
            # 잘못된 입력 제거
            corrected_text = ''.join(filter(str.isdigit, text))  # 숫자만 남김
            self.lineEdit.setText(corrected_text)
        elif self.configItem:
            # ConfigItem 값 동기화 및 저장
            value = int(text)
            qconfig.set(self.configItem, value)  # 즉시 config.json에 반영
