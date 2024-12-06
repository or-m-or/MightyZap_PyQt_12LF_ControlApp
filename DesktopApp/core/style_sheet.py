# coding: utf-8
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    SETTING_INTERFACE = "setting_interface"
    NAVIGATION_VIEW_INTERFACE = "navigation_view_interface"
    TESTING_INTERFACE = "testing_interface"

    def path(self, theme=Theme.AUTO):
        theme = Theme.LIGHT
        # theme = qconfig.theme if theme == Theme.AUTO else theme # 다크모드, 화이트모드 전환 기능 필요 시 주석해제
        return f":/resource/qss/{theme.value.lower()}/{self.value}.qss"
