"""
抖店首页数据采集
"""

from contextlib import suppress
from time import sleep

from BrowserAutomationLauncher import Browser, DataPacketProcessor
from DrissionPage._pages.mix_tab import MixTab
from DrissionPage.errors import ContextLostError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed


class Urls:
    home = 'https://fxg.jinritemai.com/ffa/mshop/homepage/index'


class DataPacketUrls:
    shop_list = 'https://fxg.jinritemai.com/ecomauth/loginv1/get_login_subject'
    """获取当前账号可以切换的店铺列表"""
    submit_fe_barrier = 'https://fxg.jinritemai.com/report/submit_fe_barrier'
    """前端埋点"""


class Home:
    def __init__(self, browser: Browser):
        self._browser = browser

    def _get_home_page(self):
        """
        获取首页页面

        Returns:
            元组 (页面对象, 是否新打开的页面)
        """

        is_new_page = False

        try:
            page = self._browser.chromium.get_tab(url=Urls.home)
            page.set.activate()
        except Exception:
            page = self._browser.chromium.new_tab(url=Urls.home)
            is_new_page = True

        return page, is_new_page

    def get__shop_name(self, page: MixTab = None, close_page=True):
        """
        获取店铺名称

        Args:
            page: 页面对象
            close_page: 自动打开的页面是否需要自动关闭
        """

        _page, is_new_page = (
            (page, False) if isinstance(page, MixTab) else self._get_home_page()
        )

        user_info = None
        for _ in range(10):
            with suppress(ContextLostError):
                user_info: dict = _page.run_js('return window.__INITIAL_USER_INFO__')
                break
            sleep(0.5)

        if not user_info:
            raise RuntimeError('未找到 __INITIAL_USER_INFO__ 信息')

        if 'data' not in user_info:
            raise RuntimeError('__INITIAL_USER_INFO__ 未找到 data 字段')
        data: dict = user_info.get('data')

        shop_name = data.get('shop_name')

        if is_new_page and close_page is True:
            _page.close()

        return shop_name

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_fixed(3),
        reraise=True,
    )
    def switch_shop_byname(self, shop_name: str):
        """
        切换店铺

        Returns:
            是否切换成功
        """

        page, is_new_page = self._get_home_page()
        if not is_new_page:
            page.refresh()

        curr_shop_name = self.get__shop_name(page=page, close_page=False)

        if shop_name == curr_shop_name:
            return True

        shop_name_ele = page.ele('c:div.headerShopName', timeout=15)
        if not shop_name_ele:
            raise RuntimeError('未找到店铺名称元素')

        shop_name_ele.hover()

        switch_btn = page.ele('切换组织/店铺', timeout=5)
        if not switch_btn:
            raise RuntimeError('未找到切换组织/店铺按钮')

        page.listen.start(
            targets=DataPacketUrls.shop_list, method='GET', res_type='XHR'
        )
        switch_btn.click()
        shop_list_datapacket = page.listen.wait(timeout=15)
        if not shop_list_datapacket:
            raise TimeoutError('获取店铺列表数据包超时')

        shop_list_data = DataPacketProcessor(shop_list_datapacket).filter(
            [('data.login_subject_list', 'shop_list')]
        )
        if not shop_list_data['shop_list']:
            raise RuntimeError('当前账号的可切换店铺列表为空')

        target_shop = next(
            (item['account_name'] for item in shop_list_data['shop_list']), None
        )
        if not target_shop:
            raise RuntimeError(f'未找到目标店铺 [{shop_name}], 无法切换')

        target_shop_btn = page.ele(shop_name, timeout=3)
        if not target_shop_btn:
            raise RuntimeError(f'未找到目标店铺 [{shop_name}] 的切换按钮, 无法切换')

        page.listen.start(
            targets=DataPacketUrls.submit_fe_barrier, method='POST', res_type='Fetch'
        )
        target_shop_btn.click(by_js=True)
        barrier_datapacket = page.listen.wait(timeout=15)
        if (
            barrier_datapacket
            and 'toast_message' in barrier_datapacket.request.postData
        ):
            if barrier_datapacket.request.postData['toast_message'] == '登录成功':
                return True
        else:
            for _ in range(20):
                with suppress(Exception):
                    if self.get__shop_name(page=page, close_page=False) == shop_name:
                        return True

        return False
