from .exceptions import BitgetAPIException

class CopyTrading:
    def __init__(self, client):
        self.client = client

    async def add_or_modify_following_configurations(self, traderId, settings, autoCopy=None, mode=None):
        request_path = "/api/v2/copy/spot-follower/settings"
        body = {
            "traderId": traderId,
            "settings": settings
        }
        if autoCopy:
            body["autoCopy"] = autoCopy
        if mode:
            body["mode"] = mode
        return await self.client._send_request("POST", request_path, body=body)

    async def set_mix_copy_trade_settings(self, traderId, settings, autoCopy=None, mode=None):
        request_path = "/api/v2/copy/mix-follower/settings"
        body = {
            "traderId": traderId,
            "settings": settings
        }
        if autoCopy:
            body["autoCopy"] = autoCopy
        if mode:
            body["mode"] = mode
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_follow(self, traderId):
        request_path = "/api/v2/copy/spot-follower/cancel-trader"
        body = {"traderId": traderId}
        return await self.client._send_request("POST", request_path, body=body)

    async def unfollow_mix_trader(self, traderId):
        request_path = "/api/v2/copy/mix-follower/cancel-trader"
        body = {"traderId": traderId}
        return await self.client._send_request("POST", request_path, body=body)

    async def change_copy_trade_symbol_setting(self, settingList):
        request_path = "/api/v2/copy/mix-trader/config-setting-symbols"
        body = {"settingList": settingList}
        return await self.client._send_request("POST", request_path, body=body)

    async def change_global_copy_trade_setting(self, enable=None, showTotalEquity=None, showTpsl=None):
        request_path = "/api/v2/copy/mix-trader/config-settings-base"
        body = {}
        if enable:
            body["enable"] = enable
        if showTotalEquity:
            body["showTotalEquity"] = showTotalEquity
        if showTpsl:
            body["showTpsl"] = showTpsl
        return await self.client._send_request("POST", request_path, body=body)

    async def set_spot_copytrade_symbols(self, symbolList, settingType):
        request_path = "/api/v2/copy/spot-trader/config-setting-symbols"
        body = {"symbolList": symbolList, "settingType": settingType}
        return await self.client._send_request("POST", request_path, body=body)

    async def close_positions(self, productType, trackingNo=None, symbol=None, marginCoin=None, marginMode=None, holdSide=None):
        request_path = "/api/v2/copy/mix-follower/close-positions"
        body = {"productType": productType}
        if trackingNo:
            body["trackingNo"] = trackingNo
        if symbol:
            body["symbol"] = symbol
        if marginCoin:
            body["marginCoin"] = marginCoin
        if marginMode:
            body["marginMode"] = marginMode
        if holdSide:
            body["holdSide"] = holdSide
        return await self.client._send_request("POST", request_path, body=body)

    async def close_tracking_order(self, productType, trackingNo=None, symbol=None):
        request_path = "/api/v2/copy/mix-trader/order-close-positions"
        body = {"productType": productType}
        if trackingNo:
            body["trackingNo"] = trackingNo
        if symbol:
            body["symbol"] = symbol
        return await self.client._send_request("POST", request_path, body=body)

    async def copy_settings(self, traderId, copyAmount, copyAllPostions=None, autoCopy=None, equityGuardian=None, equityGuardianMode=None, equity=None, marginMode=None, leverage=None, multiple=None):
        request_path = "/api/v2/copy/mix-follower/copy-settings"
        body = {
            "traderId": traderId,
            "copyAmount": copyAmount
        }
        if copyAllPostions:
            body["copyAllPostions"] = copyAllPostions
        if autoCopy:
            body["autoCopy"] = autoCopy
        if equityGuardian:
            body["equityGuardian"] = equityGuardian
        if equityGuardianMode:
            body["equityGuardianMode"] = equityGuardianMode
        if equity:
            body["equity"] = equity
        if marginMode:
            body["marginMode"] = marginMode
        if leverage:
            body["leverage"] = leverage
        if multiple:
            body["multiple"] = multiple
        return await self.client._send_request("POST", request_path, body=body)

    async def create_copy_apikey(self, passphrase):
        request_path = "/api/v2/copy/mix-trader/create-copy-api"
        body = {"passphrase": passphrase}
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_tracking_order_tpsl(self, trackingNo, productType, stopSurplusPrice=None, stopLossPrice=None):
        request_path = "/api/v2/copy/mix-trader/order-modify-tpsl"
        body = {
            "trackingNo": trackingNo,
            "productType": productType
        }
        if stopSurplusPrice:
            body["stopSurplusPrice"] = stopSurplusPrice
        if stopLossPrice:
            body["stopLossPrice"] = stopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def get_copy_trade_settings(self, traderId):
        request_path = "/api/v2/copy/mix-follower/query-settings"
        params = {"traderId": traderId}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_trader_current_trading_pair(self, traderId):
        request_path = "/api/v2/copy/spot-follower/query-trader-symbols"
        params = {"traderId": traderId}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_copy_trade_symbol_settings(self, productType):
        request_path = "/api/v2/copy/mix-trader/config-query-symbols"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_copytrade_configuration(self):
        request_path = "/api/v2/copy/spot-trader/config-query-settings"
        return await self.client._send_request("GET", request_path, params={})

    async def get_current_copy_trade_orders(self, symbol=None, traderId=None, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/copy/spot-follower/query-current-orders"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if traderId:
            params["traderId"] = traderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_current_tracking_orders(self, productType, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None, symbol=None, traderId=None):
        request_path = "/api/v2/copy/mix-follower/query-current-orders"
        params = {"productType": productType}
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if symbol:
            params["symbol"] = symbol
        if traderId:
            params["traderId"] = traderId
        return await self.client._send_request("GET", request_path, params=params)

    async def get_tracking_order_summary(self):
        request_path = "/api/v2/copy/mix-trader/order-total-detail"
        return await self.client._send_request("GET", request_path, params={})

    async def get_data_indicator_statistics(self):
        request_path = "/api/v2/copy/spot-trader/order-total-detail"
        return await self.client._send_request("GET", request_path, params={})

    async def get_follow_configuration(self, traderId):
        request_path = "/api/v2/copy/spot-follower/query-settings"
        params = {"traderId": traderId}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_follow_limit(self, productType, symbol=None):
        request_path = "/api/v2/copy/mix-follower/query-quantity-limit"
        params = {"productType": productType}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_profit_share_detail(self, coin=None, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/copy/mix-trader/profit-history-details"
        params = {}
        if coin:
            params["coin"] = coin
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_profit_sharing_details(self, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None, coin=None):
        request_path = "/api/v2/copy/spot-trader/profit-history-details"
        params = {}
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_trader_profit_summary(self):
        request_path = "/api/v2/copy/spot-trader/profit-summarys"
        return await self.client._send_request("GET", request_path, params={})

    async def get_mix_trader_profit_history_summary(self):
        request_path = "/api/v2/copy/mix-trader/profit-history-summarys"
        return await self.client._send_request("GET", request_path, params={})

    async def get_history_tracking_orders(self, symbol=None, traderId=None, idLessThan=None, idGreaterThan=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/copy/spot-follower/query-history-orders"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if traderId:
            params["traderId"] = traderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if idGreaterThan:
            params["idGreaterThan"] = idGreaterThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_my_followers(self, pageNo=None, pageSize=None, startTime=None, endTime=None):
        request_path = "/api/v2/copy/mix-trader/config-query-followers"
        params = {}
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_my_traders(self, startTime=None, endTime=None, pageNo=None, pageSize=None):
        request_path = "/api/v2/copy/mix-follower/query-traders"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_my_followers(self, pageNo=None, pageSize=None, startTime=None, endTime=None):
        request_path = "/api/v2/copy/spot-trader/config-query-followers"
        params = {}
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_my_traders(self, startTime=None, endTime=None, pageNo=None, pageSize=None):
        request_path = "/api/v2/copy/spot-follower/query-traders"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return await self.client._send_request("GET", request_path, params=params)

    async def get_profit_share_detail(self, coin=None, pageSize=None, pageNo=None):
        request_path = "/api/v2/copy/mix-trader/profit-details"
        params = {}
        if coin:
            params["coin"] = coin
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)

    async def get_unrealized_profit_sharing_details(self, coin=None, pageNo=None, pageSize=None):
        request_path = "/api/v2/copy/spot-trader/profit-details"
        params = {}
        if coin:
            params["coin"] = coin
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return await self.client._send_request("GET", request_path, params=params)

    async def remove_follower(self, followerUid):
        request_path = "/api/v2/copy/mix-trader/config-remove-follower"
        body = {"followerUid": followerUid}
        return await self.client._send_request("POST", request_path, body=body)

    async def remove_followers(self, followerUid):
        request_path = "/api/v2/copy/spot-trader/config-remove-follower"
        body = {"followerUid": followerUid}
        return await self.client._send_request("POST", request_path, body=body)

    async def sell_and_sell_in_batch(self, trackingNoList, symbol):
        request_path = "/api/v2/copy/spot-follower/order-close-tracking"
        body = {"trackingNoList": trackingNoList, "symbol": symbol}
        return await self.client._send_request("POST", request_path, body=body)

    async def set_take_profit_and_stop_loss(self, trackingNo, stopSurplusPrice=None, stopLossPrice=None):
        request_path = "/api/v2/copy/spot-follower/setting-tpsl"
        body = {"trackingNo": trackingNo}
        if stopSurplusPrice:
            body["stopSurplusPrice"] = stopSurplusPrice
        if stopLossPrice:
            body["stopLossPrice"] = stopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def set_tpsl(self, trackingNo, productType, symbol=None, stopSurplusPrice=None, stopLossPrice=None):
        request_path = "/api/v2/copy/mix-follower/setting-tpsl"
        body = {"trackingNo": trackingNo, "productType": productType}
        if symbol:
            body["symbol"] = symbol
        if stopSurplusPrice:
            body["stopSurplusPrice"] = stopSurplusPrice
        if stopLossPrice:
            body["stopLossPrice"] = stopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def stop_the_order(self, trackingNoList):
        request_path = "/api/v2/copy/spot-follower/stop-order"
        body = {"trackingNoList": trackingNoList}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_profit_share_group_by_coin_date(self, pageSize=None, pageNo=None):
        request_path = "/api/v2/copy/mix-trader/profits-group-coin-date"
        params = {}
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)