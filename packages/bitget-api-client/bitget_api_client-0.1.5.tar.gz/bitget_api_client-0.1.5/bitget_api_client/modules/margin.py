from .exceptions import BitgetAPIException

class Margin:
    def __init__(self, client):
        self.client = client

    async def cross_batch_cancel_orders(self, symbol, orderIdList):
        request_path = "/api/v2/margin/crossed/batch-cancel-order"
        body = {"symbol": symbol, "orderIdList": orderIdList}
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_batch_orders(self, symbol, orderList):
        request_path = "/api/v2/margin/crossed/batch-place-order"
        body = {"symbol": symbol, "orderList": orderList}
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_borrow(self, coin, borrowAmount, clientOid=None):
        request_path = "/api/v2/margin/crossed/account/borrow"
        body = {"coin": coin, "borrowAmount": borrowAmount}
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_cancel_order(self, symbol, orderId=None, clientOid=None):
        request_path = "/api/v2/margin/crossed/cancel-order"
        body = {"symbol": symbol}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_flash_repay(self, coin=None):
        request_path = "/api/v2/margin/crossed/account/flash-repay"
        body = {}
        if coin:
            body["coin"] = coin
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_place_order(self, symbol, orderType, loanType, force, side, price=None, baseSize=None, quoteSize=None, clientOid=None, stpMode=None):
        request_path = "/api/v2/margin/crossed/place-order"
        body = {
            "symbol": symbol,
            "orderType": orderType,
            "loanType": loanType,
            "force": force,
            "side": side
        }
        if price:
            body["price"] = price
        if baseSize:
            body["baseSize"] = baseSize
        if quoteSize:
            body["quoteSize"] = quoteSize
        if clientOid:
            body["clientOid"] = clientOid
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def cross_repay(self, coin, repayAmount):
        request_path = "/api/v2/margin/crossed/account/repay"
        body = {"coin": coin, "repayAmount": repayAmount}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_cross_tier_configuration(self, coin):
        request_path = "/api/v2/margin/crossed/tier-data"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_max_borrowable(self, coin):
        request_path = "/api/v2/margin/crossed/account/max-borrowable-amount"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_account_assets(self, coin=None):
        request_path = "/api/v2/margin/crossed/account/assets"
        params = {}
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_max_transferable(self, coin):
        request_path = "/api/v2/margin/crossed/account/max-transfer-out-amount"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_risk_rate(self):
        request_path = "/api/v2/margin/crossed/account/risk-rate"
        return await self.client._send_request("GET", request_path, params={})

    async def get_cross_borrow_history(self, startTime, loanId=None, coin=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/crossed/borrow-history"
        params = {"startTime": startTime}
        if loanId:
            params["loanId"] = loanId
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_repay_history(self, startTime, repayId=None, coin=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/crossed/repay-history"
        params = {"startTime": startTime}
        if repayId:
            params["repayId"] = repayId
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_financial_history(self, startTime, marginType=None, coin=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/crossed/financial-records"
        params = {"startTime": startTime}
        if marginType:
            params["marginType"] = marginType
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_liquidation_history(self, startTime, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/crossed/liquidation-history"
        params = {"startTime": startTime}
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_flash_repay_result(self, idList):
        request_path = "/api/v2/margin/crossed/account/query-flash-repay-status"
        body = {"idList": idList}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_cross_interest_rate_and_max_borrowable(self, coin):
        request_path = "/api/v2/margin/crossed/interest-rate-and-limit"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_current_orders(self, symbol, startTime, orderId=None, clientOid=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/crossed/open-orders"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_interest_history(self, startTime, coin=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/crossed/interest-history"
        params = {"startTime": startTime}
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_history_orders(self, symbol, startTime, orderId=None, enterPointSource=None, clientOid=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/crossed/history-orders"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if enterPointSource:
            params["enterPointSource"] = enterPointSource
        if clientOid:
            params["clientOid"] = clientOid
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_borrow_history(self, symbol, startTime, loanId=None, coin=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/isolated/borrow-history"
        params = {"symbol": symbol, "startTime": startTime}
        if loanId:
            params["loanId"] = loanId
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_interest_history(self, symbol, startTime, coin=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/isolated/interest-history"
        params = {"symbol": symbol, "startTime": startTime}
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_liquidation_history(self, symbol, startTime, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/isolated/liquidation-history"
        params = {"symbol": symbol, "startTime": startTime}
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_financial_history(self, symbol, startTime, marginType=None, coin=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/isolated/financial-records"
        params = {"symbol": symbol, "startTime": startTime}
        if marginType:
            params["marginType"] = marginType
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def isolated_batch_cancel_orders(self, symbol, orderIdList=None):
        request_path = "/api/v2/margin/isolated/batch-cancel-order"
        body = {"symbol": symbol}
        if orderIdList:
            body["orderIdList"] = orderIdList
        return await self.client._send_request("POST", request_path, body=body)

    async def get_cross_liquidation_orders(self, type=None, symbol=None, fromCoin=None, toCoin=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/crossed/liquidation-order"
        params = {}
        if type:
            params["type"] = type
        if symbol:
            params["symbol"] = symbol
        if fromCoin:
            params["fromCoin"] = fromCoin
        if toCoin:
            params["toCoin"] = toCoin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_cross_order_fills(self, symbol, startTime, orderId=None, idLessThan=None, endTime=None, limit=None):
        request_path = "/api/v2/margin/crossed/fills"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def isolated_place_order(self, symbol, orderType, loanType, force, side, price=None, baseSize=None, quoteSize=None, clientOid=None, stpMode=None):
        request_path = "/api/v2/margin/isolated/place-order"
        body = {
            "symbol": symbol,
            "orderType": orderType,
            "loanType": loanType,
            "force": force,
            "side": side
        }
        if price:
            body["price"] = price
        if baseSize:
            body["baseSize"] = baseSize
        if quoteSize:
            body["quoteSize"] = quoteSize
        if clientOid:
            body["clientOid"] = clientOid
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def isolated_batch_orders(self, symbol, orderList):
        request_path = "/api/v2/margin/isolated/batch-place-order"
        body = {
            "symbol": symbol,
            "orderList": orderList
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def isolated_cancel_order(self, symbol, orderId=None, clientOid=None):
        request_path = "/api/v2/margin/isolated/cancel-order"
        body = {"symbol": symbol}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_isolated_orders_in_batch(self, symbol, orderIdList=None):
        request_path = "/api/v2/margin/isolated/batch-cancel-order"
        body = {"symbol": symbol}
        if orderIdList:
            body["orderIdList"] = orderIdList
        return await self.client._send_request("POST", request_path, body=body)

    async def get_isolated_current_orders(self, symbol, startTime, orderId=None, clientOid=None, endTime=None, limit=None):
        request_path = "/api/v2/margin/isolated/open-orders"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_orders_history(self, symbol, startTime, orderId=None, enterPointSource=None, clientOid=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/isolated/history-orders"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if enterPointSource:
            params["enterPointSource"] = enterPointSource
        if clientOid:
            params["clientOid"] = clientOid
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_order_fills(self, symbol, startTime, orderId=None, idLessThan=None, endTime=None, limit=None):
        request_path = "/api/v2/margin/isolated/fills"
        params = {"symbol": symbol, "startTime": startTime}
        if orderId:
            params["orderId"] = orderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_liquidation_orders(self, type=None, symbol=None, fromCoin=None, toCoin=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/isolated/liquidation-order"
        params = {}
        if type:
            params["type"] = type
        if symbol:
            params["symbol"] = symbol
        if fromCoin:
            params["fromCoin"] = fromCoin
        if toCoin:
            params["toCoin"] = toCoin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_account_asset(self, symbol=None):
        request_path = "/api/v2/margin/isolated/account/assets"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def isolated_borrow(self, symbol, coin, borrowAmount, clientOid=None):
        request_path = "/api/v2/margin/isolated/account/borrow"
        body = {"symbol": symbol, "coin": coin, "borrowAmount": borrowAmount}
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def isolated_repay(self, symbol, coin, repayAmount, clientOid=None):
        request_path = "/api/v2/margin/isolated/account/repay"
        body = {"symbol": symbol, "coin": coin, "repayAmount": repayAmount}
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def get_isolated_risk_rate(self, symbol=None, pageNum=None, pageSize=None):
        request_path = "/api/v2/margin/isolated/account/risk-rate"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if pageNum:
            params["pageNum"] = pageNum
        if pageSize:
            params["pageSize"] = pageSize
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_interest_rate_and_max_borrowable(self, symbol):
        request_path = "/api/v2/margin/isolated/interest-rate-and-limit"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_tier_configuration(self, symbol):
        request_path = "/api/v2/margin/isolated/tier-data"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_max_borrowable(self, symbol):
        request_path = "/api/v2/margin/isolated/account/max-borrowable-amount"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_max_transferable(self, symbol):
        request_path = "/api/v2/margin/isolated/account/max-transfer-out-amount"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def isolated_flash_repay(self, symbolList=None):
        request_path = "/api/v2/margin/isolated/account/flash-repay"
        body = {}
        if symbolList:
            body["symbolList"] = symbolList
        return await self.client._send_request("POST", request_path, body=body)

    async def query_isolated_flash_repayment_result(self, idList):
        request_path = "/api/v2/margin/isolated/account/query-flash-repay-status"
        body = {"idList": idList}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_isolated_repay_history(self, symbol, startTime, repayId=None, coin=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/margin/isolated/repay-history"
        params = {"symbol": symbol, "startTime": startTime}
        if repayId:
            params["repayId"] = repayId
        if coin:
            params["coin"] = coin
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_support_currencies(self):
        request_path = "/api/v2/margin/currencies"
        return await self.client._send_request("GET", request_path, params={})

    async def get_the_leverage_interest_rate(self, coin):
        request_path = "/api/v2/margin/interest-rate-record"
        params = {"coin": coin}
        return await self.client._send_request("GET", request_path, params=params)