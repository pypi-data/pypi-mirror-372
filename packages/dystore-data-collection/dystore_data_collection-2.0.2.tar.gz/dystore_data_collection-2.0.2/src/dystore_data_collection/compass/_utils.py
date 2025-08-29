from time import sleep

from DrissionPage._pages.mix_tab import MixTab
from DrissionPage.common import Keys


def pick__daterange(page: MixTab, begin_date: str, end_date: str):
    """选择日期范围"""

    daterange_input = page.ele('c:div.ecom-picker-range', timeout=3)
    if not daterange_input:
        raise RuntimeError('未找到日期范围选择器元素')

    daterange_input.click(by_js=True)

    begin_date_input = page.ele('c:input[placeholder="开始日期"]', timeout=3)
    begin_date_input.input(begin_date.replace('-', '/') + Keys.ENTER, clear=True)
    sleep(0.8)

    end_date_input = page.ele('c:input[placeholder="结束日期"]', timeout=3)
    end_date_input.input(end_date.replace('-', '/') + Keys.ENTER, clear=True)
