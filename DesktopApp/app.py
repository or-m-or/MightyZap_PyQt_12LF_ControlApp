import os
import sys
from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator
from common.config import cfg
from view.main_window import MainWindow


# DPI 스케일링 설정 활성화
if cfg.get(cfg.dpiScale) == "Auto":                             # DPI 스케일링을 자동으로 설정한 경우
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)        # DPI 스케일 값을 그대로 사용
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)       # 고해상도 DPI 스케일링 활성화
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"               # DPI 스케일링 비활성화
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))  # 설정값에 따른 스케일 강제 적용

QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps) # 고해상도 픽스맵 사용 설정 (아이콘, 이미지 품질 개선)

# 애플리케이션 생성
app = QApplication(sys.argv)                           
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)  # 네이티브 위젯 중복 생성을 방지

# 다국어 지원
locale = cfg.get(cfg.language).value
translator = FluentTranslator(locale)
galleryTranslator = QTranslator()
# galleryTranslator.load(locale, "gallery", ".", ":/gallery/i18n")

app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# 메인 윈도우 생성 및 실행
w = MainWindow()
w.show()
app.exec_() # 애플리케이션 이벤트 루프 실행
