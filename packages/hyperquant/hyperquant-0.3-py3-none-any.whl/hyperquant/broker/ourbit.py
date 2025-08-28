from typing import Literal, Optional
import pybotters
from .models.ourbit import OurbitSwapDataStore


class OurbitSwap:

    def __init__(self, client: pybotters.Client):
        """
        ✅ 完成:
            下单, 撤单, 查询资金, 查询持有订单, 查询历史订单

        """
        self.client = client
        self.store = OurbitSwapDataStore()
        self.api_url = "https://futures.ourbit.com"
        self.ws_url = "wss://futures.ourbit.com/edge"

    async def __aenter__(self) -> "OurbitSwap":
        client = self.client
        await self.store.initialize(
            client.get(f"{self.api_url}/api/v1/contract/detailV2?client=web")
        )
        return self

    async def update(
        self, update_type: Literal["position", "orders", "balance", "ticker", "all"] = "all"
    ):
        """由于交易所很多不支持ws推送，这里使用Rest"""
        all_urls = [
            f"{self.api_url}/api/v1/private/position/open_positions",
            f"{self.api_url}/api/v1/private/order/list/open_orders?page_size=200",
            f"{self.api_url}/api/v1/private/account/assets",
            f"{self.api_url}/api/v1/contract/ticker",
        ]

        url_map = {
            "position": [all_urls[0]],
            "orders": [all_urls[1]],
            "balance": [all_urls[2]],
            "ticker": [all_urls[3]],
            "all": all_urls,
        }

        try:
            urls = url_map[update_type]
        except KeyError:
            raise ValueError(f"update_type err: {update_type}")

        # 直接传协程进去，initialize 会自己 await
        await self.store.initialize(*(self.client.get(url) for url in urls))

    async def sub_tickers(self):
        self.client.ws_connect(
            self.ws_url,
            send_json={
                "method": "sub.tickers",
                "param": {
                    "timezone": "UTC+8"
                }
            },
            hdlr_json=self.store.onmessage
        )

    async def sub_order_book(self, symbols: str | list[str]):
        if isinstance(symbols, str):
            symbols = [symbols]

        send_jsons = []
        # send_json={"method":"sub.depth.step","param":{"symbol":"BTC_USDT","step":"0.1"}},

        for symbol in symbols:
            step = self.store.detail.find({"symbol": symbol})[0].get("tick_size")
            
            send_jsons.append({
                "method": "sub.depth.step",
                "param": {
                    "symbol": symbol,
                    "step": str(step)
                }
            })

        await self.client.ws_connect(
            self.ws_url,
            send_json=send_jsons,
            hdlr_json=self.store.onmessage
        )

    def ret_content(self, res: pybotters.FetchResult):
        match res.data:
            case {"success": True}:
                return res.data["data"]
            case _:
                raise Exception(f"Failed api {res.response.url}: {res.data}")
            

    async def place_order(
        self,
        symbol: str,
        side: Literal["buy", "sell", "close"],
        size: float = None,
        price: float = None,
        order_type: Literal["market", "limit_GTC", "limit_IOC"] = "market",
        usdt_amount: Optional[float] = None,
        leverage: Optional[int] = 20,
        position_id: Optional[int] = None,
    ):
        """size为合约张数"""
        if (size is None) == (usdt_amount is None):
            raise ValueError("params err")

        max_lev = self.store.detail.find({"symbol": symbol})[0].get("max_lev")
        
        if usdt_amount is not None:
            cs = self.store.detail.find({"symbol": symbol})[0].get("contract_sz")
            size = max(int(usdt_amount / cs / price), 1)
            

        leverage = max(max_lev, leverage)

        data = {
            "symbol": symbol,
            "side": 1 if side == "buy" else 3,
            "openType": 1,
            "type": "5",
            "vol": size,
            "leverage": leverage,
            "marketCeiling": False,
            "priceProtect": "0",
        }

        if order_type == "limit_IOC":
            data["type"] = 3
            data["price"] = str(price)
        if order_type == "limit_GTC":
            data["type"] = "1"
            data["price"] = str(price)

        if side == "close":
            data["side"] = 4
            if position_id is None:
                raise ValueError("position_id is required for closing position")
            data["positionId"] = position_id

        res =  await self.client.fetch(
            "POST", f"{self.api_url}/api/v1/private/order/create", data=data
        )
        return self.ret_content(res)

    async def cancel_orders(self, order_ids: list[str]):
        res = await self.client.fetch(
            "POST",
            f"{self.api_url}/api/v1/private/order/cancel",
            data=order_ids,
        )
        return self.ret_content(res)

    async def query_orders(
        self,
        symbol: str,
        states: list[Literal["filled", "canceled"]],  # filled:已成交, canceled:已撤销
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page_size: int = 200,
        page_num: int = 1,
    ):
        """查询历史订单

        Args:
            symbol: 交易对
            states: 订单状态列表 ["filled":已成交, "canceled":已撤销]
            start_time: 开始时间戳(毫秒), 可选
            end_time: 结束时间戳(毫秒), 可选
            page_size: 每页数量, 默认200
            page_num: 页码, 默认1
        """
        state_map = {"filled": 3, "canceled": 4}

        params = {
            "symbol": symbol,
            "states": ",".join(str(state_map[state]) for state in states),
            "page_size": page_size,
            "page_num": page_num,
            "category": 1,
        }

        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        res = await self.client.fetch(
            "GET",
            f"{self.api_url}/api/v1/private/order/list/history_orders",
            params=params,
        )

        return self.ret_content(res)

    async def query_order(self, order_id: str):
        """查询单个订单的详细信息

        Args:
            order_id: 订单ID

        Returns:
            ..code:python

            订单详情数据，例如:
            [
                    {
                        "id": "38600506",          # 成交ID
                        "symbol": "SOL_USDT",      # 交易对
                        "side": 4,                 # 方向(1:买入, 3:卖出, 4:平仓)
                        "vol": 1,                  # 成交数量
                        "price": 204.11,          # 成交价格
                        "fee": 0.00081644,        # 手续费
                        "feeCurrency": "USDT",    # 手续费币种
                        "profit": -0.0034,        # 盈亏
                        "category": 1,            # 品类
                        "orderId": "219079365441409152",  # 订单ID
                        "timestamp": 1756270991000,       # 时间戳
                        "positionMode": 1,        # 持仓模式
                        "voucher": false,         # 是否使用代金券
                        "taker": true            # 是否是taker
                    }
            ]
        """
        res = await self.client.fetch(
            "GET",
            f"{self.api_url}/api/v1/private/order/deal_details/{order_id}",
        )

        return self.ret_content(res)
