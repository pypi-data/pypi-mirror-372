from .exceptions import BitgetAPIException

class Contract:
    def __init__(self, client):
        self.client = client

    async def adjust_position_margin(self, symbol, productType, marginCoin, holdSide, amount):
        request_path = "/api/v2/mix/account/set-margin"
        body = {
            "symbol": symbol,
            "productType": productType,
            "marginCoin": marginCoin,
            "holdSide": holdSide,
            "amount": amount
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_cancel(self, symbol, productType, orderIds=None, clientOids=None):
        request_path = "/api/v2/mix/trade/batch-cancel-order"
        body = {
            "symbol": symbol,
            "productType": productType
        }
        if orderIds:
            body["orderIds"] = orderIds
        if clientOids:
            body["clientOids"] = clientOids
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_order(self, symbol, productType, orderList):
        request_path = "/api/v2/mix/trade/batch-place-order"
        body = {
            "symbol": symbol,
            "productType": productType,
            "orderList": orderList
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_all_orders(self, productType, marginCoin=None, requestTime=None, receiveWindow=None):
        request_path = "/api/v2/mix/order/cancel-all-orders"
        body = {"productType": productType}
        if marginCoin:
            body["marginCoin"] = marginCoin
        if requestTime:
            body["requestTime"] = requestTime
        if receiveWindow:
            body["receiveWindow"] = receiveWindow
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_order(self, symbol, productType, orderId=None, clientOid=None, marginCoin=None):
        request_path = "/api/v2/mix/order/cancel-order"
        body = {
            "symbol": symbol,
            "productType": productType
        }
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if marginCoin:
            body["marginCoin"] = marginCoin
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_trigger_order(self, productType, orderIdList=None, symbol=None, marginCoin=None, planType=None):
        request_path = "/api/v2/mix/order/cancel-plan-order"
        body = {"productType": productType}
        if orderIdList:
            body["orderIdList"] = orderIdList
        if symbol:
            body["symbol"] = symbol
        if marginCoin:
            body["marginCoin"] = marginCoin
        if planType:
            body["planType"] = planType
        return await self.client._send_request("POST", request_path, body=body)

    async def change_leverage(self, symbol, productType, leverage, marginCoin=None):
        request_path = "/api/v2/mix/account/set-leverage"
        body = {
            "symbol": symbol,
            "productType": productType,
            "leverage": leverage
        }
        if marginCoin:
            body["marginCoin"] = marginCoin
        return await self.client._send_request("POST", request_path, body=body)

    async def change_margin_mode(self, symbol, productType, marginMode, marginCoin=None):
        request_path = "/api/v2/mix/account/set-margin-mode"
        body = {
            "symbol": symbol,
            "productType": productType,
            "marginMode": marginMode
        }
        if marginCoin:
            body["marginCoin"] = marginCoin
        return await self.client._send_request("POST", request_path, body=body)

    async def change_position_mode(self, productType, holdMode):
        request_path = "/api/v2/mix/account/set-position-mode"
        body = {
            "productType": productType,
            "holdMode": holdMode
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def change_the_product_line_leverage(self, productType, leverage, marginCoin=None):
        request_path = "/api/v2/mix/account/set-all-leverage"
        body = {
            "productType": productType,
            "leverage": leverage
        }
        if marginCoin:
            body["marginCoin"] = marginCoin
        return await self.client._send_request("POST", request_path, body=body)

    async def flash_close_position(self, symbol, productType, marginCoin, holdSide):
        request_path = "/api/v2/mix/trade/close-all-position"
        body = {
            "symbol": symbol,
            "productType": productType,
            "marginCoin": marginCoin,
            "holdSide": holdSide
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def get_account_bills(self, productType, marginCoin=None, startTime=None, endTime=None, bizType=None, bizSubType=None, limit=None, idLessThan=None):
        request_path = "/api/v2/mix/account/account-bill"
        params = {"productType": productType}
        if marginCoin:
            params["marginCoin"] = marginCoin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if bizType:
            params["bizType"] = bizType
        if bizSubType:
            params["bizSubType"] = bizSubType
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_account_list(self, productType):
        request_path = "/api/v2/mix/account/accounts"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_single_account(self, symbol, productType, marginCoin):
        request_path = "/api/v2/mix/account/account"
        params = {"symbol": symbol, "productType": productType, "marginCoin": marginCoin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_assets(self, productType):
        request_path = "/api/v2/mix/account/sub-account-assets"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_usdt_m_futures_interest_history(self, productType, coin=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/account/interest-history"
        params = {"productType": productType}
        if coin:
            params["coin"] = coin
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def my_estimated_open_count(self, symbol, productType, marginCoin, openAmount, openPrice, leverage=None):
        request_path = "/api/v2/mix/account/open-count"
        params = {
            "symbol": symbol,
            "productType": productType,
            "marginCoin": marginCoin,
            "openAmount": openAmount,
            "openPrice": openPrice
        }
        if leverage:
            params["leverage"] = leverage
        return await self.client._send_request("GET", request_path, params=params)

    async def set_isolated_position_auto_margin(self, symbol, autoMargin, marginCoin, holdSide):
        request_path = "/api/v2/mix/account/set-auto-margin"
        body = {
            "symbol": symbol,
            "autoMargin": autoMargin,
            "marginCoin": marginCoin,
            "holdSide": holdSide
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def set_usdt_m_futures_asset_mode(self, productType, assetMode):
        request_path = "/api/v2/mix/account/set-asset-mode"
        body = {
            "productType": productType,
            "assetMode": assetMode
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def simultaneous_stop_profit_and_stop_loss_plan_orders(self, marginCoin, productType, symbol, holdSide, stopSurplusTriggerPrice=None, stopSurplusSize=None, stopSurplusTriggerType=None, stopSurplusExecutePrice=None, stopLossTriggerPrice=None, stopLossSize=None, stopLossTriggerType=None, stopLossExecutePrice=None, stpMode=None, stopSurplusClientOid=None, stopLossClientOid=None):
        request_path = "/api/v2/mix/order/place-pos-tpsl"
        body = {
            "marginCoin": marginCoin,
            "productType": productType,
            "symbol": symbol,
            "holdSide": holdSide
        }
        if stopSurplusTriggerPrice:
            body["stopSurplusTriggerPrice"] = stopSurplusTriggerPrice
        if stopSurplusSize:
            body["stopSurplusSize"] = stopSurplusSize
        if stopSurplusTriggerType:
            body["stopSurplusTriggerType"] = stopSurplusTriggerType
        if stopSurplusExecutePrice:
            body["stopSurplusExecutePrice"] = stopSurplusExecutePrice
        if stopLossTriggerPrice:
            body["stopLossTriggerPrice"] = stopLossTriggerPrice
        if stopLossSize:
            body["stopLossSize"] = stopLossSize
        if stopLossTriggerType:
            body["stopLossTriggerType"] = stopLossTriggerType
        if stopLossExecutePrice:
            body["stopLossExecutePrice"] = stopLossExecutePrice
        if stpMode:
            body["stpMode"] = stpMode
        if stopSurplusClientOid:
            body["stopSurplusClientOid"] = stopSurplusClientOid
        if stopLossClientOid:
            body["stopLossClientOid"] = stopLossClientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def stop_profit_and_stop_loss_plan_orders(self, marginCoin, productType, symbol, planType, triggerPrice, holdSide, size, triggerType=None, executePrice=None, rangeRate=None, clientOid=None, stpMode=None):
        request_path = "/api/v2/mix/order/place-tpsl-order"
        body = {
            "marginCoin": marginCoin,
            "productType": productType,
            "symbol": symbol,
            "planType": planType,
            "triggerPrice": triggerPrice,
            "holdSide": holdSide,
            "size": size
        }
        if triggerType:
            body["triggerType"] = triggerType
        if executePrice:
            body["executePrice"] = executePrice
        if rangeRate:
            body["rangeRate"] = rangeRate
        if clientOid:
            body["clientOid"] = clientOid
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def trigger_sub_order(self, planType, planOrderId, productType):
        request_path = "/api/v2/mix/order/plan-sub-order"
        params = {"planType": planType, "planOrderId": planOrderId, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def vip_fee_rate(self):
        request_path = "/api/v2/mix/market/vip-fee-rate"
        return await self.client._send_request("GET", request_path, params={})

    async def place_order(self, symbol, productType, marginMode, marginCoin, size, side, orderType, price=None, tradeSide=None, force=None, clientOid=None, reduceOnly=None, presetStopSurplusPrice=None, presetStopLossPrice=None, presetStopSurplusExecutePrice=None, presetStopLossExecutePrice=None, stpMode=None):
        request_path = "/api/v2/mix/order/place-order"
        body = {
            "symbol": symbol,
            "productType": productType,
            "marginMode": marginMode,
            "marginCoin": marginCoin,
            "size": size,
            "side": side,
            "orderType": orderType
        }
        if price:
            body["price"] = price
        if tradeSide:
            body["tradeSide"] = tradeSide
        if force:
            body["force"] = force
        if clientOid:
            body["clientOid"] = clientOid
        if reduceOnly:
            body["reduceOnly"] = reduceOnly
        if presetStopSurplusPrice:
            body["presetStopSurplusPrice"] = presetStopSurplusPrice
        if presetStopLossPrice:
            body["presetStopLossPrice"] = presetStopLossPrice
        if presetStopSurplusExecutePrice:
            body["presetStopSurplusExecutePrice"] = presetStopSurplusExecutePrice
        if presetStopLossExecutePrice:
            body["presetStopLossExecutePrice"] = presetStopLossExecutePrice
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def place_trigger_order(self, planType, symbol, productType, marginMode, marginCoin, size, triggerPrice, triggerType, side, orderType, price=None, callbackRatio=None, tradeSide=None, clientOid=None, reduceOnly=None, stopSurplusTriggerPrice=None, stopSurplusExecutePrice=None, stopSurplusTriggerType=None, stopLossTriggerPrice=None, stopLossExecutePrice=None, stopLossTriggerType=None, stpMode=None):
        request_path = "/api/v2/mix/order/place-plan-order"
        body = {
            "planType": planType,
            "symbol": symbol,
            "productType": productType,
            "marginMode": marginMode,
            "marginCoin": marginCoin,
            "size": size,
            "triggerPrice": triggerPrice,
            "triggerType": triggerType,
            "side": side,
            "orderType": orderType
        }
        if price:
            body["price"] = price
        if callbackRatio:
            body["callbackRatio"] = callbackRatio
        if tradeSide:
            body["tradeSide"] = tradeSide
        if clientOid:
            body["clientOid"] = clientOid
        if reduceOnly:
            body["reduceOnly"] = reduceOnly
        if stopSurplusTriggerPrice:
            body["stopSurplusTriggerPrice"] = stopSurplusTriggerPrice
        if stopSurplusExecutePrice:
            body["stopSurplusExecutePrice"] = stopSurplusExecutePrice
        if stopSurplusTriggerType:
            body["stopSurplusTriggerType"] = stopSurplusTriggerType
        if stopLossTriggerPrice:
            body["stopLossTriggerPrice"] = stopLossTriggerPrice
        if stopLossExecutePrice:
            body["stopLossExecutePrice"] = stopLossExecutePrice
        if stopLossTriggerType:
            body["stopLossTriggerType"] = stopLossTriggerType
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def reversal(self, symbol, marginCoin, productType, side, size=None, tradeSide=None, clientOid=None):
        request_path = "/api/v2/mix/order/click-backhand"
        body = {
            "symbol": symbol,
            "marginCoin": marginCoin,
            "productType": productType,
            "side": side
        }
        if size:
            body["size"] = size
        if tradeSide:
            body["tradeSide"] = tradeSide
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def get_ticker(self, symbol, productType):
        request_path = "/api/v2/mix/market/ticker"
        params = {"symbol": symbol, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_all_positions(self, productType, marginCoin=None):
        request_path = "/api/v2/mix/position/all-position"
        params = {"productType": productType}
        if marginCoin:
            params["marginCoin"] = marginCoin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_all_tickers(self, productType):
        request_path = "/api/v2/mix/market/tickers"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_candlestick_data(self, symbol, productType, granularity, startTime=None, endTime=None, kLineType=None, limit=None):
        request_path = "/api/v2/mix/market/candles"
        params = {
            "symbol": symbol,
            "productType": productType,
            "granularity": granularity
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if kLineType:
            params["kLineType"] = kLineType
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_contract_config(self, productType, symbol=None):
        request_path = "/api/v2/mix/market/contracts"
        params = {"productType": productType}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_contract_oi_limit(self, productType, symbol=None):
        request_path = "/api/v2/mix/market/oi-limit"
        params = {"productType": productType}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_current_funding_rate(self, productType, symbol=None):
        request_path = "/api/v2/mix/market/current-fund-rate"
        params = {"productType": productType}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_discount_rate(self):
        request_path = "/api/v2/mix/market/discount-rate"
        return await self.client._send_request("GET", request_path, params={})

    async def get_historical_candlestick(self, symbol, productType, granularity, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/market/history-candles"
        params = {
            "symbol": symbol,
            "productType": productType,
            "granularity": granularity
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_funding_rates(self, symbol, productType, pageSize=None, pageNo=None):
        request_path = "/api/v2/mix/market/history-fund-rate"
        params = {
            "symbol": symbol,
            "productType": productType
        }
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_index_price_candlestick(self, symbol, productType, granularity, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/market/history-index-candles"
        params = {
            "symbol": symbol,
            "productType": productType,
            "granularity": granularity
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_mark_price_candlestick(self, symbol, productType, granularity, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/market/history-mark-candles"
        params = {
            "symbol": symbol,
            "productType": productType,
            "granularity": granularity
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_transaction_details(self, productType, orderId=None, symbol=None, startTime=None, endTime=None, idLessThan=None, limit=None):
        request_path = "/api/v2/mix/order/fill-history"
        params = {"productType": productType}
        if orderId:
            params["orderId"] = orderId
        if symbol:
            params["symbol"] = symbol
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_interest_exchange_rate(self):
        request_path = "/api/v2/mix/market/exchange-rate"
        return await self.client._send_request("GET", request_path, params={})

    async def get_interest_rate_history(self, coin):
        request_path = "/api/v2/mix/market/union-interest-rate-history"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_mark_index_market_prices(self, symbol, productType):
        request_path = "/api/v2/mix/market/symbol-price"
        params = {"symbol": symbol, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_merge_market_depth(self, symbol, productType, precision=None, limit=None):
        request_path = "/api/v2/mix/market/merge-depth"
        params = {"symbol": symbol, "productType": productType}
        if precision:
            params["precision"] = precision
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_next_funding_time(self, symbol, productType):
        request_path = "/api/v2/mix/market/funding-time"
        params = {"symbol": symbol, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_open_interest(self, symbol, productType):
        request_path = "/api/v2/mix/market/open-interest"
        params = {"symbol": symbol, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_recent_transactions(self, symbol, productType, limit=None):
        request_path = "/api/v2/mix/market/fills"
        params = {"symbol": symbol, "productType": productType}
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_order(self, productType, orderId=None, clientOid=None, symbol=None, idLessThan=None, orderSource=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/order/orders-history"
        params = {"productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if symbol:
            params["symbol"] = symbol
        if idLessThan:
            params["idLessThan"] = idLessThan
        if orderSource:
            params["orderSource"] = orderSource
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_trigger_order(self, planType, productType, orderId=None, clientOid=None, planStatus=None, symbol=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/order/orders-plan-history"
        params = {"planType": planType, "productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if planStatus:
            params["planStatus"] = planStatus
        if symbol:
            params["symbol"] = symbol
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def modify_order(self, symbol, productType, newClientOid, orderId=None, clientOid=None, newSize=None, newPrice=None, newPresetStopSurplusPrice=None, newPresetStopLossPrice=None):
        request_path = "/api/v2/mix/order/modify-order"
        body = {
            "symbol": symbol,
            "productType": productType,
            "newClientOid": newClientOid
        }
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if newSize:
            body["newSize"] = newSize
        if newPrice:
            body["newPrice"] = newPrice
        if newPresetStopSurplusPrice:
            body["newPresetStopSurplusPrice"] = newPresetStopSurplusPrice
        if newPresetStopLossPrice:
            body["newPresetStopLossPrice"] = newPresetStopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_the_stop_profit_and_stop_loss_plan_order(self, marginCoin, productType, symbol, triggerPrice, size, orderId=None, clientOid=None, triggerType=None, executePrice=None, rangeRate=None):
        request_path = "/api/v2/mix/order/modify-tpsl-order"
        body = {
            "marginCoin": marginCoin,
            "productType": productType,
            "symbol": symbol,
            "triggerPrice": triggerPrice,
            "size": size
        }
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if triggerType:
            body["triggerType"] = triggerType
        if executePrice:
            body["executePrice"] = executePrice
        if rangeRate is not None:
            body["rangeRate"] = rangeRate
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_trigger_order(self, productType, orderId=None, clientOid=None, newSize=None, newPrice=None, newCallbackRatio=None, newTriggerPrice=None, newTriggerType=None, newStopSurplusTriggerPrice=None, newStopSurplusExecutePrice=None, newStopSurplusTriggerType=None, newStopLossTriggerPrice=None, newStopLossExecutePrice=None, newStopLossTriggerType=None):
        request_path = "/api/v2/mix/order/modify-plan-order"
        body = {"productType": productType}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if newSize:
            body["newSize"] = newSize
        if newPrice:
            body["newPrice"] = newPrice
        if newCallbackRatio:
            body["newCallbackRatio"] = newCallbackRatio
        if newTriggerPrice:
            body["newTriggerPrice"] = newTriggerPrice
        if newTriggerType:
            body["newTriggerType"] = newTriggerType
        if newStopSurplusTriggerPrice:
            body["newStopSurplusTriggerPrice"] = newStopSurplusTriggerPrice
        if newStopSurplusExecutePrice:
            body["newStopSurplusExecutePrice"] = newStopSurplusExecutePrice
        if newStopSurplusTriggerType:
            body["newStopSurplusTriggerType"] = newStopSurplusTriggerType
        if newStopLossTriggerPrice:
            body["newStopLossTriggerPrice"] = newStopLossTriggerPrice
        if newStopLossExecutePrice:
            body["newStopLossExecutePrice"] = newStopLossExecutePrice
        if newStopLossTriggerType:
            body["newStopLossTriggerType"] = newStopLossTriggerType
        return await self.client._send_request("POST", request_path, body=body)

    async def get_order_detail(self, symbol, productType, orderId=None, clientOid=None):
        request_path = "/api/v2/mix/order/detail"
        params = {"symbol": symbol, "productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        return await self.client._send_request("GET", request_path, params=params)

    async def get_order_fill_details(self, productType, orderId=None, symbol=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/order/fills"
        params = {"productType": productType}
        if orderId:
            params["orderId"] = orderId
        if symbol:
            params["symbol"] = symbol
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_pending_orders(self, productType, orderId=None, clientOid=None, symbol=None, status=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/order/orders-pending"
        params = {"productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if symbol:
            params["symbol"] = symbol
        if status:
            params["status"] = status
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_pending_trigger_order(self, planType, productType, orderId=None, clientOid=None, symbol=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/order/orders-plan-pending"
        params = {"planType": planType, "productType": productType}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if symbol:
            params["symbol"] = symbol
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_position_adl_rank(self, productType):
        request_path = "/api/v2/mix/position/adlRank"
        params = {"productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_position_tier(self, productType, symbol):
        request_path = "/api/v2/mix/market/query-position-lever"
        params = {"productType": productType, "symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_single_position(self, productType, symbol, marginCoin):
        request_path = "/api/v2/mix/position/single-position"
        params = {"productType": productType, "symbol": symbol, "marginCoin": marginCoin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_historical_position(self, symbol=None, productType=None, idLessThan=None, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/mix/position/history-position"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if productType:
            params["productType"] = productType
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_transactions(self, symbol, productType, limit=None, idLessThan=None, startTime=None, endTime=None):
        request_path = "/api/v2/mix/market/fills-history"
        params = {"symbol": symbol, "productType": productType}
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)