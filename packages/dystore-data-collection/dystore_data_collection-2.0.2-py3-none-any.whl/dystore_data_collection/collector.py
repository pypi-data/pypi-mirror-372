"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-02-08
Author: Martian Bugs
Description: 数据采集器
"""

from BrowserAutomationLauncher import BrowserInitOptions, Launcher

from .compass.compass import Compass
from .home.home import Home
from .im.im import Im


class Collector:
    """采集器. 使用之前请先调用 `connect_browser` 方法连接浏览器."""

    def __init__(self):
        self._launcher = Launcher()

        self._im = None
        self._home = None
        self._compass = None

    def connect_browser(self, port: int):
        """
        连接浏览器

        Args:
            port: 浏览器调试端口号
        """

        options = BrowserInitOptions()
        options.set_basic_options(port=port)

        self.browser = self._launcher.init_browser(options)

    @property
    def home(self):
        """首页"""

        if self._home is None:
            self._home = Home(self.browser)

        return self._home

    @property
    def im(self):
        """飞鸽客服系统"""

        if self._im is None:
            self._im = Im(self.browser)

        return self._im

    @property
    def compass(self):
        """电商罗盘"""

        if self._compass is None:
            self._compass = Compass(self.browser)

        return self._compass
