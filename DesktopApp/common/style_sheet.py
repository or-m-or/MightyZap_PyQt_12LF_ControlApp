# coding: utf-8
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    HOME_INTERFACE = "home_interface"
    SETTING_INTERFACE = "setting_interface"
    NAVIGATION_VIEW_INTERFACE = "navigation_view_interface"
    TESTING_INTERFACE = "testing_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f":/resource/qss/{theme.value.lower()}/{self.value}.qss"
