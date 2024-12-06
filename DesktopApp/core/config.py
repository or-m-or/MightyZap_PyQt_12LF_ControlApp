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
import logging


"""
[ 로깅 설정 ]
"""
def setup_logger(name='AppLogger', level=logging.DEBUG, log_file='app.log'):
    """공용 로거 설정 함수"""
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 포맷 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(console_handler)

    return logger


"""
[ 앱 설정 ]
"""
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
    
    qconfig.load("config.json", cfg) # 설정값 로드
    cfg.theme.value # 테마 값 출력
    cfg.theme.setValue("키") 설정 값 변경
    qconfig.save(cfg) # 저장
    """    
    # Baudrate 설정 (OptionsConfigItem으로 고정 옵션 제공)
    # baudrate = OptionsConfigItem(
    #     "BoardSetting",  # 설정 그룹 이름
    #     "Baudrate",  # 설정 키 이름
    #     "9600",  # 기본값: 9600
    #     OptionsValidator(["9600", "19200", "57600", "115200"]),  # 허용 값
    #     restart=False
    # )
    
     # 조그(액추에이터) 이동 관련
    # rangeValue = RangeConfigItem("Jog", "RangeValue", 0, RangeValidator(0, 4095))
    position1 = RangeConfigItem("Jog", "Position1", 0, RangeValidator(0, 4095))
    position2 = RangeConfigItem("Jog", "Position2", 0, RangeValidator(0, 4095))
    
    # 테스트1회당 왕복 횟수
    push_counts = ConfigItem(
        "Test",              # 설정 그룹 이름
        "PushCounts",        # 설정 키 이름
        5,                   # 기본값
        RangeValidator(0, 100000),  # 허용 범위 (0~100)
        restart=False
    )
    
    # 액추에이터 관련 설정
    global_speed = RangeConfigItem(
        "Actuator", 
        "GlobalSpeed", 
        1023, 
        RangeValidator(0, 1023)  # 범위: 0~1023
    )

    # temp_speed = RangeConfigItem(
    #     "Actuator", 
    #     "TempSpeed", 
    #     1023, 
    #     RangeValidator(0, 1023)  # 범위: 0~1023
    # )

    bwd_limit = RangeConfigItem(
        "Actuator", 
        "BackwardLimit", 
        0, 
        RangeValidator(0, 4095)  # 범위: 0~4095
    )

    fwd_limit = RangeConfigItem(
        "Actuator", 
        "ForwardLimit", 
        3686, 
        RangeValidator(0, 4095)  # 범위: 0~4095
    )
    
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
YEAR = 2024
AUTHOR = ""
VERSION = ""
HELP_URL = ""
REPO_URL = ""
RELEASE_URL = ""
KR_SUPPORT_URL = ""
EN_SUPPORT_URL = "https://qfluentwidgets.com/price/"    # 영어 지원 URL


# 설정 객체 생성
cfg = Config()
# cfg.themeMode.value = Theme.AUTO  # 테마 모드를 자동으로 설정 필요시 주석 해제
cfg.themeMode.value = Theme.LIGHT

qconfig.load('common/config.json', cfg)  # 설정 파일에서 설정 로드
