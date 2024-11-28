import logging
from logging.handlers import RotatingFileHandler


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
[ 설정 기본 값 세팅 ]

Model Number        : 41234
Firmware Version    : 2.10
Present Temperature : 245
Short Stroke Limit  : 0
Long Stroke Limit   : 3686
Speed Limit         : 1023
Current Limit       : 800
Acceleration Ratio  : 20
Deceleration Ratio  : 64
Default values read successfully.
"""
DEFAULT_VALUES = {
    "speed_limit": 1023,   # 반영구 속도 제한값
    "speed": 1023,         # 임시 속도 제한값
    "current_limit": 800,  # 반영구 전류 제한값 (mA)
    "current": 800,        # 임시 전류 제한값
    "short_limit": 0,      # 최소 지점 한계값
    "long_limit": 3686,    # 최대 지점 한계값
    "accel": 20,           # 가속률
    "decel": 64            # 감속률
}
