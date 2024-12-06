from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox
from qfluentwidgets import (
    ExpandGroupSettingCard,
    FluentIcon as FIF,
    StrongBodyLabel,
    SpinBox,
    Flyout,
    InfoBarIcon,
    qconfig,
)


class ActuatorSettingCard(ExpandGroupSettingCard):
    """ 액추에이터 설정 카드 """
    globalSpeedUpdated = pyqtSignal(int)  # 글로벌 속도 값 변경 시
    backwardLimitUpdated = pyqtSignal(int)  # 후진 제한 값 변경 시
    forwardLimitUpdated = pyqtSignal(int)  # 전진 제한 값 변경 시

    def __init__(self, config, parent=None):
        super().__init__(
            FIF.SETTING,  # 아이콘
            "Actuator Setting",  # 제목
            "Configure actuator settings such as speed and limits.",  # 설명
            parent,
        )
        self.config = config

        # 글로벌 속도 설정
        self.globalSpeedSpinBox = SpinBox(self)
        self.globalSpeedSpinBox.setRange(0, 1023)
        self.globalSpeedSpinBox.setValue(config.global_speed.value)
        self.globalSpeedSpinBox.setFixedWidth(200)
        self.globalSpeedGroup = self._initSingleWidgetGroup("Speed (0~1023)", self.globalSpeedSpinBox)

        # 후진 제한값 설정
        self.backwardLimitSpinBox = SpinBox(self)
        self.backwardLimitSpinBox.setRange(0, 4095)
        self.backwardLimitSpinBox.setValue(config.bwd_limit.value)
        self.backwardLimitSpinBox.setFixedWidth(200)
        self.backwardLimitGroup = self._initSingleWidgetGroup("Backward Limit (0~4095)", self.backwardLimitSpinBox)

        # 전진 제한값 설정
        self.forwardLimitSpinBox = SpinBox(self)
        self.forwardLimitSpinBox.setRange(0, 4095)
        self.forwardLimitSpinBox.setValue(config.fwd_limit.value)
        self.forwardLimitSpinBox.setFixedWidth(200)
        self.forwardLimitGroup = self._initSingleWidgetGroup("Forward Limit (0~4095)", self.forwardLimitSpinBox)

        # 그룹 추가
        self.addGroupWidget(self.globalSpeedGroup)
        self.addGroupWidget(self.backwardLimitGroup)
        self.addGroupWidget(self.forwardLimitGroup)

        # 시그널 연결
        self.globalSpeedSpinBox.valueChanged.connect(self._onGlobalSpeedChanged)
        self.backwardLimitSpinBox.valueChanged.connect(self._onBackwardLimitChanged)
        self.forwardLimitSpinBox.valueChanged.connect(self._onForwardLimitChanged)

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

    def _onGlobalSpeedChanged(self, value):
        """ 글로벌 속도 값 변경 시 호출 """
        if not isinstance(value, int) or not (0 <= value <= 1023):
            self._showInvalidInputFlyout(self.globalSpeedSpinBox, "Global speed must be between 0 and 1023.")
            return

        qconfig.set(self.config.global_speed, value)  # 값 반영
        qconfig.save()  # 설정 저장
        self.globalSpeedUpdated.emit(value)

    def _onBackwardLimitChanged(self, value):
        """ 후진 제한 값 변경 시 호출 """
        if not isinstance(value, int) or not (0 <= value <= 4095):
            self._showInvalidInputFlyout(self.backwardLimitSpinBox, "Backward limit must be between 0 and 4095.")
            return

        qconfig.set(self.config.bwd_limit, value)  # 값 반영
        qconfig.save()  # 설정 저장
        self.backwardLimitUpdated.emit(value)

    def _onForwardLimitChanged(self, value):
        """ 전진 제한 값 변경 시 호출 """
        if not isinstance(value, int) or not (0 <= value <= 4095):
            self._showInvalidInputFlyout(self.forwardLimitSpinBox, "Forward limit must be between 0 and 4095.")
            return

        qconfig.set(self.config.fwd_limit, value)  # 값 반영
        qconfig.save()  # 설정 저장
        self.forwardLimitUpdated.emit(value)

    def _showInvalidInputFlyout(self, widget, message):
        """ 유효하지 않은 입력값에 대해 Flyout 표시 """
        Flyout.create(
            icon=InfoBarIcon.WARNING,
            title="Invalid Input",
            content=message,
            target=widget,
            parent=self,
            isClosable=True
        )
