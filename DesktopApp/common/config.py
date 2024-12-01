import sys
from enum import Enum
from PyQt5.QtCore import QLocale
from qfluentwidgets import (
    qconfig, 
    QConfig,
    ConfigItem, 
    OptionsConfigItem, 
    BoolValidator,
    OptionsValidator, 
    RangeConfigItem, 
    RangeValidator,
    FolderListValidator, 
    Theme,
    FolderValidator, 
    ConfigSerializer, 
    __version__
)


class Language(Enum):
    """ 언어 선택을 위한 열거형 클래스 """
    ENGLISH = QLocale(QLocale.English)  # 영어
    AUTO = QLocale()                    # 시스템 기본 언어 (자동)


class LanguageSerializer(ConfigSerializer):
    """ 언어를 직렬화/역직렬화하는 클래스 """

    def serialize(self, language):
        """ 언어 데이터를 직렬화 (저장 가능한 문자열로 변환) """
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        """ 저장된 문자열 값을 언어 데이터로 변환 """
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ 
    애플리케이션 설정을 관리하는 클래스 (저장할 값)
    restart=False -> 재시작 없이 즉시 반영 
    """
    
    # Port 설정 (ConfigItem으로 설정, 동적 값 지원)
    port = OptionsConfigItem(
        "BoardSetting",  # 설정 그룹 이름
        "Port",  # 설정 키 이름
        "None",  # 기본값: 빈 문자열
        OptionsValidator(["None"]),  # 초기 옵션 리스트는 빈 리스트
        restart=False
    )

    # Baudrate 설정 (OptionsConfigItem으로 고정 옵션 제공)
    baudrate = OptionsConfigItem(
        "BoardSetting",  # 설정 그룹 이름
        "Baudrate",  # 설정 키 이름
        "9600",  # 기본값: 9600
        OptionsValidator(["9600", "19200", "38400", "57600", "115200"]),  # 허용 값
        restart=False
    )
    
    # 조그 
    rangeValue = RangeConfigItem("Jog", "RangeValue", 0, RangeValidator(0, 4095))

    # 메인 윈도우 설정
    dpiScale = OptionsConfigItem(
        "MainWindow",
        "DpiScale",
        "Auto",  # 기본값: 자동 DPI 스케일
        OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]),  # 선택 가능 값
        restart=True  # 변경 시 애플리케이션 재시작 필요
    )
    
    # 언어
    language = OptionsConfigItem(
        "MainWindow",
        "Language",
        Language.AUTO,  # 기본값: 시스템 기본 언어
        OptionsValidator(Language),  # 언어 값 검증
        LanguageSerializer(),  # 언어 직렬화 클래스 사용
        restart=True  # 변경 시 애플리케이션 재시작 필요
    )

    # 머티리얼 관련 설정
    blurRadius = RangeConfigItem(
        "Material",  # 설정 그룹
        "AcrylicBlurRadius",  # 키 이름
        15,  # 기본값: 블러 반경
        RangeValidator(0, 40)  # 허용 범위: 0~40
    )


# 메타데이터 (앱 정보)
YEAR = 2023
AUTHOR = "zhiyiYo"
VERSION = __version__
HELP_URL = "https://qfluentwidgets.com"
REPO_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"
EXAMPLE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/master/examples"
FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"
ZH_SUPPORT_URL = "https://qfluentwidgets.com/zh/price/"  # 중국어 지원 URL
EN_SUPPORT_URL = "https://qfluentwidgets.com/price/"    # 영어 지원 URL


# 설정 객체 생성
cfg = Config()
cfg.themeMode.value = Theme.AUTO  # 테마 모드를 자동으로 설정
qconfig.load('common/config.json', cfg)  # 설정 파일에서 설정 로드
