"""API client for Eastmoney trading operations."""

from typing import Any

import httpx
from loguru import logger

from emta.models.trading import OrderType

from ..models.exceptions import TradingError

# Base headers for API requests
BASE_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36",
    "Origin": "https://jywg.18.cn",
    "Host": "jywg.18.cn",
}


class APIClient:
    """Handles API requests to Eastmoney trading services"""

    def __init__(self, session: httpx.Client):
        """Initialize the API client.

        Args:
            session: HTTP client session
        """
        self.session = session
        self.logger = logger

    def _check_response(self, resp: httpx.Response) -> None:
        """Check if response is successful.

        Args:
            resp: HTTP response to check

        Raises:
            TradingError: If response status is not 200
        """
        if resp.status_code != 200:
            self.logger.error(
                f"Request {resp.url} failed, code={resp.status_code}, response={resp.text}"
            )
            raise TradingError(f"API request failed with status {resp.status_code}")

    def query_something(
        self, url: str, validate_key: str, req_data: dict[str, Any] | None = None
    ) -> httpx.Response:
        """通用查询函数

        :param url: 请求url
        :param validate_key: 验证key
        :param req_data: 请求提交数据,可选
        :return: HTTP响应
        """
        full_url = f"{url}{validate_key}"
        if req_data is None:
            req_data = {
                "qqhs": 100,
                "dwc": "",
            }
        headers = BASE_HEADERS.copy()
        headers["X-Requested-With"] = "XMLHttpRequest"
        self.logger.debug(f"(url={full_url}), (data={req_data})")
        resp = self.session.post(full_url, headers=headers, data=req_data)
        self._check_response(resp)
        return resp

    def get_asset_and_position(self, validate_key: str) -> dict[str, Any]:
        """Get asset and position information.

        Args:
            validate_key: Validation key for the session

        Returns:
            Dictionary containing asset and position data
        """
        url = "https://jywg.18.cn/Com/queryAssetAndPositionV1?validatekey="
        resp = self.query_something(url, validate_key)
        return resp.json()  # type: ignore[no-any-return]

    def create_order(
        self,
        validate_key: str,
        stock_code: str,
        trade_type: OrderType,
        market: str,
        price: float,
        amount: int,
    ) -> dict[str, Any]:
        """交易接口, 买入或卖出.

        :param str stock_code: 股票代码
        :param str trade_type: 交易方向,B for buy, S for sell
        :param str market: 股票市场,HA 上海, SA
        :param float price: 股票价格
        :param int amount: 买入/卖出数量
        """
        req_data = {
            "stockCode": stock_code,
            "tradeType": trade_type,
            "zqmc": "",
            "market": market,
            "price": price,
            "amount": amount,
        }
        url = "https://jywg.18.cn/Trade/SubmitTradeV2?validatekey="
        resp = self.query_something(url, validate_key, req_data=req_data)
        if resp:
            self.logger.info(resp.json())
        return resp.json()  # type: ignore[no-any-return]
