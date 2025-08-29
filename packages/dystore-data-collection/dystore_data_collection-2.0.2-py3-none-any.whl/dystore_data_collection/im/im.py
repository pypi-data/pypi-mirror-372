"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-02-08
Author: Martian Bugs
Description: 飞鸽客服系统数据采集
"""

from BrowserAutomationLauncher import Browser

from .data import Data


class Im:
    def __init__(self, browser: Browser):
        self._browser = browser

        self._data = None

    @property
    def data(self):
        """客服数据采集"""

        if self._data is None:
            self._data = Data(self._browser)

        return self._data
