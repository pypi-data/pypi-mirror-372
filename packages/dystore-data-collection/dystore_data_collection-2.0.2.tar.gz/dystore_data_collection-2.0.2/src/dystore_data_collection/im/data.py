"""
客服数据采集
"""

from BrowserAutomationLauncher import Browser
from BrowserAutomationLauncher._utils.tools import DateTimeTools, WebTools


class Urls:
    history_data = (
        'https://im.jinritemai.com/pc_seller_v2/main/data/customerService/historyData'
    )


class DataPacketUrls:
    history_data__detail = (
        'pigeon.jinritemai.com/backstage/get_historical_staff_statistics_v2'
    )


class ApiUrls:
    history_data__detail__download = (
        'https://pigeon.jinritemai.com/backstage/exportHistoricalStaffStatistics'
    )


class Data:
    def __init__(self, browser: Browser):
        self._browser = browser
        self._timeout = 15

    def download__history_data__detail(
        self,
        begin_date: str,
        end_date: str,
        save_path: str,
        save_name: str,
        timeout: float = None,
        download_timeout: float = None,
        open_page=False,
    ):
        """
        下载客服历史数据详情

        Args:
            download_timeout: 下载超时时间, 默认 120 秒
            open_page: 是否打开页面, 如果为 False 则使用当前激活的页面
        Returns:
            下载的文件路径
        """

        _timeout = timeout if isinstance(timeout, (int, float)) else self._timeout
        _download_timeout = (
            download_timeout if isinstance(download_timeout, (int, float)) else 120
        )

        page = (
            self._browser.chromium.new_tab()
            if open_page is True
            else self._browser.chromium.latest_tab
        )
        if open_page is True:
            page.listen.start(
                targets=DataPacketUrls.history_data__detail,
                method='GET',
                res_type='XHR',
            )
            page.get(Urls.history_data)
            if not page.listen.wait(timeout=_timeout):
                raise TimeoutError('首次进入页面获取数据超时, 可能页面访问失败')

        if not page.ele('t:button@@text()=导出报表', timeout=3):
            raise RuntimeError('未找到 [导出报表] 按钮')

        page.change_mode('s', go=False)

        begin_date_timestamp = end_date_timestamp = None
        if begin_date == end_date:
            begin_date_timestamp = end_date_timestamp = (
                DateTimeTools.datetime_to_timestamp(f'{begin_date} 00:00:00')
            )
        else:
            begin_date_timestamp = DateTimeTools.datetime_to_timestamp(
                f'{begin_date} 00:00:00'
            )
            end_date_timestamp = DateTimeTools.datetime_to_timestamp(
                f'{end_date} 23:59:59'
            )

        query_data = {
            'endTime': end_date_timestamp,
            'groupId': -1,
            'queryStaffName': '',
            'sortTag': 0,
            'sortType': 0,
            'startTime': begin_date_timestamp,
        }

        status, file_path = page.download(
            file_url=WebTools.url_append_params(
                ApiUrls.history_data__detail__download, query_data
            ),
            save_path=save_path,
            rename=save_name,
            file_exists='overwrite',
            show_msg=False,
            timeout=_download_timeout,
        )

        if open_page is True:
            page.close()

        if status != 'success':
            raise RuntimeError('报表下载失败')

        return file_path
