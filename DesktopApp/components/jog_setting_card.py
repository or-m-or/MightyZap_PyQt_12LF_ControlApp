from PyQt5.QtCore import pyqtSignal, Qt, QRect
from PyQt5.QtGui import QPainter, QFont, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QPushButton, QLineEdit, QSpinBox
from qfluentwidgets import (
    ExpandGroupSettingCard, 
    FluentIcon as FIF, 
    BodyLabel, 
    PrimaryPushButton,
    Slider,
    TitleLabel,
    StrongBodyLabel, 
    LineEdit,
    SpinBox,
    Flyout,
    InfoBarIcon,
    qconfig,
)
from PyQt5.QtWidgets import QSlider, QStyleOptionSlider

    

class JogSettingCard(ExpandGroupSettingCard):
    """ 조그 및 테스트 설정 카드 """
    positionChanged = pyqtSignal(int)  # 슬라이더 값 변경 시
    homeRequested = pyqtSignal()      # 홈 버튼 클릭 시
    testCountUpdated = pyqtSignal(int)  # 테스트 횟수 변경 시
    position1Updated = pyqtSignal(int)  # 포지션1 값 변경 시
    position2Updated = pyqtSignal(int)  # 포지션2 값 변경 시

    def __init__(self, config, parent=None):
        super().__init__(
            FIF.SETTING,  # 아이콘
            "Jog Setting",  # 제목
            "Configure jog and test settings for the actuator",  # 설명
            parent,
        )
        self.config = config
        self.rangeValue = 0 # 범위 값을 JogSettingCard 내부에서 관리 (초기값: 0)
        
        # 조그 이동 슬라이더
        self.slider = Slider(Qt.Horizontal, self)
        self.slider.setRange(0, 4095)
        self.slider.setValue(self.rangeValue)
        self.slider.setFixedWidth(300)
        self.sliderValueLabel = StrongBodyLabel(str(self.rangeValue), self) # 초기값
        self.sliderValueLabel.setAlignment(Qt.AlignCenter)  # 텍스트 중앙 정렬
        self.sliderValueLabel.setFixedWidth(60)  # 라벨 크기 설정
        self.sliderGroup = self._initSliderGroup("Actuator Location (BWD~FWD)", self.slider, self.sliderValueLabel)

        # SpinBox + 홈 버튼
        self.sliderSpinBox = SpinBox(self)
        self.sliderSpinBox.setRange(0, 4095)
        self.sliderSpinBox.setValue(self.rangeValue) # 초기값
        self.sliderSpinBox.setFixedWidth(200)
        self.homeButton = PrimaryPushButton("Home", self)
        self.homeButton.setFixedSize(100, 30)
        self.homeButtonGroup = self._initHomeButtonGroup("Move Actuator Details (BWD~FWD)", self.sliderSpinBox, self.homeButton)
        
        
        # 포지션1 입력
        self.position1Input = LineEdit(self)
        self.position1Input.setPlaceholderText("Position 1 (0~4095)")
        self.position1Input.setFixedWidth(200)
        self.position1Input.setText(str(self.config.position1.value))
        self.position1Group = self._initSingleWidgetGroup("Position 1", self.position1Input)

        # 포지션2 입력
        self.position2Input = LineEdit(self)
        self.position2Input.setPlaceholderText("Position 2 (0~4095)")
        self.position2Input.setFixedWidth(200)
        self.position2Input.setText(str(self.config.position2.value))
        self.position2Group = self._initSingleWidgetGroup("Position 2", self.position2Input)

        # 테스트 횟수 입력
        self.testCountSpinBox = SpinBox(self)
        self.testCountSpinBox.setRange(0, 2140000000)
        self.testCountSpinBox.setValue(self.config.push_counts.value)
        self.testCountSpinBox.setFixedWidth(200)
        self.testCountGroup = self._initSingleWidgetGroup("Test Counts", self.testCountSpinBox)

        # 그룹 추가
        self.addGroupWidget(self.sliderGroup)
        self.addGroupWidget(self.homeButtonGroup)
        self.addGroupWidget(self.position1Group)
        self.addGroupWidget(self.position2Group)
        self.addGroupWidget(self.testCountGroup)

        # ConfigItem 연결
        # config.rangeValue.valueChanged.connect(self.slider.setValue)
        config.push_counts.valueChanged.connect(self.testCountSpinBox.setValue)

        self.config = config

        # 시그널 연결
        self.slider.valueChanged.connect(self._onPositionChanged)
        self.sliderSpinBox.valueChanged.connect(self._onSpinBoxValueChanged)
        self.homeButton.clicked.connect(self._onHomeRequested)
        self.position1Input.textChanged.connect(self._onPosition1Updated)
        self.position2Input.textChanged.connect(self._onPosition2Updated)
        self.testCountSpinBox.valueChanged.connect(self._onTestCountUpdated)

    def _initSliderGroup(self, label_text, slider, value_label):
        """ 슬라이더와 값 라벨이 포함된 그룹 위젯 생성 """
        group = QWidget()
        layout = QHBoxLayout(group)
        layout.setContentsMargins(48, 12, 48, 12)
        label = StrongBodyLabel(label_text, group)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(value_label)  # 값 표시 라벨 추가
        layout.addWidget(slider)      # 슬라이더 추가
        return group
    
    def _initHomeButtonGroup(self, label_text, spinbox, home_button):
        """ SpinBox와 홈 버튼이 포함된 그룹 위젯 생성 """
        group = QWidget()
        layout = QHBoxLayout(group)
        layout.setContentsMargins(48, 12, 48, 12)
        label = StrongBodyLabel(label_text, group)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(spinbox)     # SpinBox 추가
        layout.addWidget(home_button) # 홈 버튼 추가
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

    def _onPositionChanged(self, value):
        """ 슬라이더 값 변경 시 호출 """
        self.rangeValue = value  # 범위 값을 업데이트
        self.sliderValueLabel.setText(str(value)) # 라벨에 슬라이더 값 업데이트
        self.sliderSpinBox.setValue(value)         # SpinBox 값 동기화
        self.positionChanged.emit(value)

    def _onSpinBoxValueChanged(self, value):
        """ SpinBox 값 변경 시 호출 """
        self.rangeValue = value
        self.slider.setValue(value)  # 슬라이더 값 동기화
        
    def _onHomeRequested(self):
        """ 홈 버튼 클릭 시 호출 """
        self.homeRequested.emit()

    def _onPosition1Updated(self, text):
        """ 포지션1 값 변경 시 호출 """
        if not text.strip():
            return  # 공백 무시
        if not text.isdigit():
            # 숫자가 아닌 입력을 제거하고 알림 표시
            corrected_text = ''.join(filter(str.isdigit, text))
            self.position1Input.setText(corrected_text)  # 잘못된 입력 수정
            self._showInvalidInputFlyout(self.position1Input, "Only numeric values are allowed.")
            return

        try:
            value = int(text)
            if 0 <= value <= 4095:
                qconfig.set(self.config.position1, value)  # 값 반영
                qconfig.save()  # 설정 저장
                self.position1Updated.emit(value)
            else:
                self._showInvalidInputFlyout(self.position1Input, "Position 1 must be between 0 and 4095.")
        except ValueError:
            self._showInvalidInputFlyout(self.position1Input, "Position 1 must be a valid number.")


    def _onPosition2Updated(self, text):
        """ 포지션2 값 변경 시 호출 """
        if not text.strip():
            return  # 공백 무시
        if not text.isdigit():
            # 숫자가 아닌 입력을 제거하고 알림 표시
            corrected_text = ''.join(filter(str.isdigit, text))
            self.position2Input.setText(corrected_text)  # 잘못된 입력 수정
            self._showInvalidInputFlyout(self.position2Input, "Only numeric values are allowed.")
            return

        try:
            value = int(text)
            if 0 <= value <= 4095:
                qconfig.set(self.config.position2, value)  # 값 반영
                qconfig.save()  # 설정 저장
                self.position2Updated.emit(value)
            else:
                self._showInvalidInputFlyout(self.position2Input, "Position 2 must be between 0 and 4095.")
        except ValueError:
            self._showInvalidInputFlyout(self.position2Input, "Position 2 must be a valid number.")

    def _onTestCountUpdated(self, value):
        """ 테스트 횟수 변경 시 호출 """
        if not isinstance(value, int) or value < 0:
            self._showInvalidInputFlyout(self.testCountSpinBox, "Test count must be a non-negative integer.")
            return

        qconfig.set(self.config.push_counts, value)  # 값 반영
        qconfig.save()  # 설정 저장
        self.testCountUpdated.emit(value)

    def _showInvalidInputFlyout(self, widget, message):
        """ 유효하지 않은 입력값에 대해 Flyout 표시 """
        Flyout.create(
            icon=InfoBarIcon.WARNING,
            title="Invalid Input",
            content=message,
            target=widget, # 잘못된 입력이 발생한 필드에 Flyout 표시
            parent=self,
            isClosable=True
        )