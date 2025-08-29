"""
电商罗盘
"""

from BrowserAutomationLauncher import Browser

from .goods import Goods


class Compass:
    def __init__(self, browser: Browser):
        self._browser = browser

        self._goods = None

    @property
    def goods(self):
        """商品数据"""

        if not self._goods:
            self._goods = Goods(self._browser)

        return self._goods
