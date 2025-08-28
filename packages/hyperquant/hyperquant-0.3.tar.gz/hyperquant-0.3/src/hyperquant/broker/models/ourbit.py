from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Awaitable

import aiohttp
from pybotters.store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from pybotters.typedefs import Item
    from pybotters.ws import ClientWebSocketResponse


logger = logging.getLogger(__name__)


class Book(DataStore):
    """深度数据存储类，用于处理订单簿深度信息

    Channel: push.depth.step

    用于存储和管理订单簿深度数据，包含买卖盘的价格和数量信息
    Keys: ["symbol", "side", "px"]
    - symbol: 交易对符号
    - side: 买卖方向 (A: ask卖出, B: bid买入)
    - px: 价格


    """

    _KEYS = ["symbol", "side", "px"]

    def _init(self) -> None:
        # super().__init__()
        self._time: int | None = None

    def _on_message(self, msg: dict[str, Any]) -> None:

        symbol = msg.get("symbol")
        data = msg.get("data", {})
        asks = data.get("asks", [])
        bids = data.get("bids", [])
        timestamp = data.get("ct")  # 使用服务器时间

        data_to_insert: list[Item] = []

        # 先删除旧的订单簿数据
        self._find_and_delete({"symbol": symbol})

        # 处理买卖盘数据
        for side_id, levels in (("B", bids), ("A", asks)):
            for level in levels:
                # level格式: [price, size, count]
                if len(level) >= 3:
                    price, size, count = level[0:3]
                    data_to_insert.append(
                        {
                            "symbol": symbol,
                            "side": side_id,
                            "px": str(price),
                            "sz": str(size),
                            "count": count,
                        }
                    )

        # 插入新的订单簿数据
        self._insert(data_to_insert)
        self._time = timestamp

    @property
    def time(self) -> int | None:
        """返回最后更新时间"""
        return self._time

    @property
    def sorted(self) -> dict[str, list[Item]]:
        """获取排序后的订单簿数据

        Returns:
            返回按价格排序的买卖盘数据，卖盘升序，买盘降序

        .. code-block:: python

            {
                "asks": [
                    {"symbol": "BTC_USDT", "side": "A", "px": "110152.5", "sz": "53539", "count": 1},
                    {"symbol": "BTC_USDT", "side": "A", "px": "110152.6", "sz": "95513", "count": 2}
                ],
                "bids": [
                    {"symbol": "BTC_USDT", "side": "B", "px": "110152.4", "sz": "76311", "count": 1},
                    {"symbol": "BTC_USDT", "side": "B", "px": "110152.3", "sz": "104688", "count": 2}
                ]
            }
        """
        return self._sorted(
            item_key="side",
            item_asc_key="A",  # asks 升序
            item_desc_key="B",  # bids 降序
            sort_key="px",
        )


class Ticker(DataStore):
    _KEYS = ["symbol"]

    def _on_message(self, data: dict[str, Any]):
        self._onresponse(data)

    def _onresponse(self, data: dict[str, Any]):
        tickers = data.get("data", [])
        if tickers:
            data_to_insert: list[Item] = []
            for ticker in tickers:
                ticker: dict[str, Any] = ticker
                for ticker in tickers:
                    data_to_insert.append(
                        {
                            "amount24": ticker.get("amount24"),
                            "fair_price": ticker.get("fairPrice"),
                            "high24_price": ticker.get("high24Price"),
                            "index_price": ticker.get("indexPrice"),
                            "last_price": ticker.get("lastPrice"),
                            "lower24_price": ticker.get("lower24Price"),
                            "max_bid_price": ticker.get("maxBidPrice"),
                            "min_ask_price": ticker.get("minAskPrice"),
                            "rise_fall_rate": ticker.get("riseFallRate"),
                            "symbol": ticker.get("symbol"),
                            "timestamp": ticker.get("timestamp"),
                            "volume24": ticker.get("volume24"),
                        }
                    )
            # self._clear()
            self._insert(data_to_insert)


class Orders(DataStore):
    _KEYS = ["order_id"]

    # {'success': True, 'code': 0, 'data': [{'orderId': '219108574599630976', 'symbol': 'SOL_USDT', 'positionId': 0, 'price': 190, 'priceStr': '190', 'vol': 1, 'leverage': 20, 'side': 1, 'category': 1, 'orderType': 1, 'dealAvgPrice': 0, 'dealAvgPriceStr': '0', 'dealVol': 0, 'orderMargin': 0.09652, 'takerFee': 0, 'makerFee': 0, 'profit': 0, 'feeCurrency': 'USDT', 'openType': 1, 'state': 2, 'externalOid': '_m_2228b23a75204e1982b301e44d439cbb', 'errorCode': 0, 'usedMargin': 0, 'createTime': 1756277955008, 'updateTime': 1756277955037, 'positionMode': 1, 'version': 1, 'showCancelReason': 0, 'showProfitRateShare': 0, 'voucher': False}]}
    def _onresponse(self, data: dict[str, Any]):
        orders = data.get("data", [])
        if orders:
            data_to_insert: list[Item] = []
            for order in orders:
                order: dict[str, Any] = order

                data_to_insert.append(
                    {
                        "order_id": order.get("orderId"),
                        "symbol": order.get("symbol"),
                        "px": order.get("priceStr"),
                        "vol": order.get("vol"),
                        "lev": order.get("leverage"),
                        "side": "buy" if order.get("side") == 1 else "sell",
                        "deal_vol": order.get("dealVol"),
                        "deal_avg_px": order.get("dealAvgPriceStr"),
                        "create_ts": order.get("createTime"),
                        "update_ts": order.get("updateTime"),
                    }
                )

            self._clear()
            self._update(data_to_insert)


class Detail(DataStore):
    _KEYS = ["symbol"]

    def _on_message(self, data: dict[str, Any]):
        self._onresponse(data)

    def _onresponse(self, data: dict[str, Any]):
        details: dict = data.get("data", {})
        data_to_insert: list[Item] = []
        if details:
            for detail in details:
                data_to_insert.append(
                    {
                        "symbol": detail.get("symbol"),
                        "ft": detail.get("ft"),
                        "max_lev": detail.get("maxL"),
                        "tick_size": detail.get("pu"),
                        "vol_unit": detail.get("vu"),
                        "io": detail.get("io"),
                        "contract_sz": detail.get("cs"),
                        "minv": detail.get("minV"),
                        "maxv": detail.get("maxV")
                    }
                )
        self._update(data_to_insert)

class Position(DataStore):
    _KEYS = ["position_id"]
    # {"success":true,"code":0,"data":[{"positionId":5355366,"symbol":"SOL_USDT","positionType":1,"openType":1,"state":1,"holdVol":1,"frozenVol":0,"closeVol":0,"holdAvgPrice":203.44,"holdAvgPriceFullyScale":"203.44","openAvgPrice":203.44,"openAvgPriceFullyScale":"203.44","closeAvgPrice":0,"liquidatePrice":194.07,"oim":0.10253376,"im":0.10253376,"holdFee":0,"realised":-0.0008,"leverage":20,"marginRatio":0.0998,"createTime":1756275984696,"updateTime":1756275984696,"autoAddIm":false,"version":1,"profitRatio":0,"newOpenAvgPrice":203.44,"newCloseAvgPrice":0,"closeProfitLoss":0,"fee":0.00081376}]}
    def _onresponse(self, data: dict[str, Any]):
        positions = data.get("data", [])
        if positions:
            data_to_insert: list[Item] = []
            for position in positions:
                position: dict[str, Any] = position

                data_to_insert.append(
                    {
                        "position_id": position.get("positionId"),
                        "symbol": position.get("symbol"),
                        "side": "short" if position.get("positionType") == 2 else "long",
                        "open_type": position.get("openType"),
                        "state": position.get("state"),
                        "hold_vol": position.get("holdVol"),
                        "frozen_vol": position.get("frozenVol"),
                        "close_vol": position.get("closeVol"),
                        "hold_avg_price": position.get("holdAvgPriceFullyScale"),
                        "open_avg_price": position.get("openAvgPriceFullyScale"),
                        "close_avg_price": str(position.get("closeAvgPrice")),
                        "liquidate_price": str(position.get("liquidatePrice")),
                        "oim": position.get("oim"),
                        "im": position.get("im"),
                        "hold_fee": position.get("holdFee"),
                        "realised": position.get("realised"),
                        "leverage": position.get("leverage"),
                        "margin_ratio": position.get("marginRatio"),
                        "create_ts": position.get("createTime"),
                        "update_ts": position.get("updateTime"),
                    }
                )

            self._clear()
            self._insert(data_to_insert)

class Balance(DataStore):
    _KEYS = ["currency"]

    def _onresponse(self, data: dict[str, Any]):
        balances = data.get("data", [])
        if balances:
            data_to_insert: list[Item] = []
            for balance in balances:
                balance: dict[str, Any] = balance
                data_to_insert.append({
                    "currency": balance.get("currency"),
                    "position_margin": balance.get("positionMargin"),
                    "available_balance": balance.get("availableBalance"),
                    "cash_balance": balance.get("cashBalance"),
                    "frozen_balance": balance.get("frozenBalance"),
                    "equity": balance.get("equity"),
                    "unrealized": balance.get("unrealized"),
                    "bonus": balance.get("bonus"),
                    "last_bonus": balance.get("lastBonus"),
                    "wallet_balance": balance.get("walletBalance"),
                    "voucher": balance.get("voucher"),
                    "voucher_using": balance.get("voucherUsing"),
                })
            self._clear()
            self._insert(data_to_insert)

class OurbitSwapDataStore(DataStoreCollection):
    """
    Ourbit DataStoreCollection

    REST API:
      - 地址: https://futures.ourbit.com
      - 合约详情
        GET /api/v1/contract/detailV2?client=web
      - ticker
        GET /api/v1/contract/ticker
      - open_orders
        GET /api/v1/private/order/list/open_orders?page_size=200
      - open_positions
        GET /api/v1/private/position/open_positions

    WebSocket API:
      - 地址: wss://futures.ourbit.com/edge or /ws
      - 支持频道:
        * 深度数据（Book）: push.depth.step
        * 行情数据（Ticker）: push.tickers

    示例订阅 JSON:

    .. code:: json

        {
            "method": "sub.depth.step",
            "param": {
                "symbol": "BTC_USDT",
                "step": "0.1"
            }
        }

    .. code:: json

        {
            "method": "sub.tickers",
            "param": {
                "timezone": "UTC+8"
            }
        }

    TODO:
      - 添加 trades、ticker、candle 等其他数据流
    """

    def _init(self) -> None:
        self._create("book", datastore_class=Book)
        self._create("detail", datastore_class=Detail)
        self._create("ticker", datastore_class=Ticker)
        self._create("orders", datastore_class=Orders)
        self._create("position", datastore_class=Position)
        self._create("balance", datastore_class=Balance)
        # TODO: 添加其他数据流，如 trades, ticker, candle 等

    def onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        channel = msg.get("channel")

        if channel == "push.depth.step":
            self.book._on_message(msg)
        if channel == "push.tickers":
            self.ticker._on_message(msg)
        else:
            logger.debug(f"未知的channel: {channel}")

    async def initialize(self, *aws: Awaitable[aiohttp.ClientResponse]) -> None:
        """Initialize DataStore from HTTP response data."""
        for f in asyncio.as_completed(aws):
            res = await f
            data = await res.json()
            if res.url.path == "/api/v1/contract/detailV2":
                self.detail._onresponse(data)
            if res.url.path == "/api/v1/contract/ticker":
                self.ticker._onresponse(data)
            if res.url.path == "/api/v1/private/order/list/open_orders":
                self.orders._onresponse(data)
            if res.url.path == "/api/v1/private/position/open_positions":
                self.position._onresponse(data)
            if res.url.path == "/api/v1/private/account/assets":
                self.balance._onresponse(data)

    @property
    def detail(self) -> Detail:
        """合约详情
        Data structure:
        .. code:: python
        [
            {
                "symbol": "BTC_USDT",   # 交易对
                "ft": 100,            # 合约面值
                "max_lev": 100,       # 最大杠杆
                "tick_size": 0.1,     # 最小变动价位
                "vol_unit": 1,        # 合约单位
                "io": ["binance", "mexc"],  # 交易所列表
                "contract_sz": 1,
                "minv": 1,
                "maxv": 10000

            }
        ]
        """
        return self._get("detail", Detail)

    @property
    def book(self) -> Book:
        """订单簿深度数据流

        Data type: Mutable

        Keys: ("symbol", "side", "px")

        Data structure:

        .. code:: python

            [
                {
                    "symbol": "BTC_USDT",    # 交易对
                    "side": "A",             # 卖出方向
                    "px": "110152.5",        # 价格
                    "sz": "53539",           # 数量
                    "count": 1               # 订单数量
                },
                {
                    "symbol": "BTC_USDT",    # 交易对
                    "side": "B",             # 买入方向
                    "px": "110152.4",        # 价格
                    "sz": "76311",           # 数量
                    "count": 1               # 订单数量
                }
            ]
        """
        return self._get("book", Book)

    @property
    def ticker(self) -> Ticker:
        """市场行情数据流

        Data type: Mutable

        Keys: ("symbol",)

        Data structure:

        .. code:: python

            [
                {
                    "symbol": "BTC_USDT",        # 交易对
                    "last_price": "110152.5",    # 最新价格
                    "index_price": "110000.0",   # 指数价格
                    "fair_price": "110100.0",    # 公允价格
                    "high24_price": "115000.0",  # 24小时最高价
                    "lower24_price": "105000.0", # 24小时最低价
                    "volume24": "1500",          # 24小时交易量
                    "amount24": "165000000",     # 24小时交易额
                    "rise_fall_rate": "0.05",    # 涨跌幅
                    "max_bid_price": "110150.0", # 买一价
                    "min_ask_price": "110155.0", # 卖一价
                    "timestamp": 1625247600000   # 时间戳
                }
            ]
        """
        return self._get("ticker", Ticker)

    @property
    def orders(self) -> Orders:
        """
        订单数据
        Data structure:

        .. code:: json

            [
                {
                    "id": "123456",
                    "symbol": "BTC_USDT",
                    "side": "buy",
                    "price": "110152.5",
                    "size": "0.1",
                    "status": "open",
                    "create_ts": 1625247600000,
                    "update_ts": 1625247600000
                }
            ]
        """
        return self._get("orders", Orders)

    @property
    def position(self) -> Position:
        """
        持仓数据

        Data structure:
        .. code:: python
        [
            {
                "position_id": "123456",
                "symbol": "BTC_USDT",
                "side": "long",
                "open_type": "limit",
                "state": "open",
                "hold_vol": "0.1",
                "frozen_vol": "0.0",
                "close_vol": "0.0",
                "hold_avg_price": "110152.5",
                "open_avg_price": "110152.5",
                "close_avg_price": "0.0",
                "liquidate_price": "100000.0",
                "oim": "0.0",
                "im": "0.0",
                "hold_fee": "0.0",
                "realised": "0.0",
                "leverage": "10",
                "margin_ratio": "0.1",
                "create_ts": 1625247600000,
                "update_ts": 1625247600000
            }
        ]
        """
        return self._get("position", Position)

    @property
    def balance(self) -> Balance:
        """账户余额数据
        
        Data structure:
        .. code:: python
            [
                {
                    "currency": "USDT",            # 币种
                    "position_margin": 0.3052,     # 持仓保证金
                    "available_balance": 19.7284,  # 可用余额
                    "cash_balance": 19.7284,      # 现金余额
                    "frozen_balance": 0,          # 冻结余额
                    "equity": 19.9442,           # 权益
                    "unrealized": -0.0895,       # 未实现盈亏
                    "bonus": 0,                  # 奖励
                    "last_bonus": 0,             # 最后奖励
                    "wallet_balance": 20.0337,   # 钱包余额
                    "voucher": 0,               # 代金券
                    "voucher_using": 0          # 使用中的代金券
                }
            ]
        """
        return self._get("balance", Balance)
