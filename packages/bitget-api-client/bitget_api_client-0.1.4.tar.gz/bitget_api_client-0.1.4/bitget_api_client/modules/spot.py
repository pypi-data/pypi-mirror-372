from .exceptions import BitgetAPIException

class Spot:
    def __init__(self, client):
        self.client = client

    async def get_server_time(self):
        request_path = "/api/v2/public/time"
        return await self.client._send_request("GET", request_path)

    async def get_symbol_config(self, symbol=None):
        request_path = "/api/v2/spot/public/symbols"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_currency_information(self, coin=None):
        request_path = "/api/v2/spot/public/coins"
        params = {}
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_deposit_address(self, coin, chain):
        request_path = "/api/v2/spot/wallet/deposit-address"
        params = {"coin": coin, "chain": chain}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_deposit_record(self, startTime, endTime, coin=None, orderId=None, idLessThan=None, limit=None):
        request_path = "/api/v2/spot/wallet/deposit-records"
        params = {"startTime": startTime, "endTime": endTime}
        if coin:
            params["coin"] = coin
        if orderId:
            params["orderId"] = orderId
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_withdraw_record(self, startTime, endTime, coin=None, clientOid=None, idLessThan=None, orderId=None, limit=None):
        request_path = "/api/v2/spot/wallet/withdrawal-records"
        params = {"startTime": startTime, "endTime": endTime}
        if coin:
            params["coin"] = coin
        if clientOid:
            params["clientOid"] = clientOid
        if idLessThan:
            params["idLessThan"] = idLessThan
        if orderId:
            params["orderId"] = orderId
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def withdraw(self, coin, transferType, address, size, chain=None, innerToType=None, areaCode=None, tag=None, remark=None, clientOid=None):
        request_path = "/api/v2/spot/wallet/withdrawal"
        body = {
            "coin": coin,
            "transferType": transferType,
            "address": address,
            "size": size
        }
        if chain:
            body["chain"] = chain
        if innerToType:
            body["innerToType"] = innerToType
        if areaCode:
            body["areaCode"] = areaCode
        if tag:
            body["tag"] = tag
        if remark:
            body["remark"] = remark
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def sub_transfer(self, fromType, toType, amount, coin, fromUserId, toUserId, symbol=None, clientOid=None):
        request_path = "/api/v2/spot/wallet/subaccount-transfer"
        body = {
            "fromType": fromType,
            "toType": toType,
            "amount": amount,
            "coin": coin,
            "fromUserId": fromUserId,
            "toUserId": toUserId
        }
        if symbol:
            body["symbol"] = symbol
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def transfer(self, fromType, toType, amount, coin, symbol, clientOid=None):
        request_path = "/api/v2/spot/wallet/transfer"
        body = {
            "fromType": fromType,
            "toType": toType,
            "amount": amount,
            "coin": coin,
            "symbol": symbol
        }
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_withdrawal(self, orderId):
        request_path = "/api/v2/spot/wallet/cancel-withdrawal"
        body = {"orderId": orderId}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_account_information(self):
        request_path = "/api/v2/spot/account/info"
        return await self.client._send_request("GET", request_path)

    async def get_account_assets(self, coin=None, assetType=None):
        request_path = "/api/v2/spot/account/assets"
        params = {}
        if coin:
            params["coin"] = coin
        if assetType:
            params["assetType"] = assetType
        return await self.client._send_request("GET", request_path, params=params)

    async def get_sub_accounts_assets(self, idLessThan=None, limit=None):
        request_path = "/api/v2/spot/account/subaccount-assets"
        params = {}
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def modify_deposit_account(self, accountType, coin):
        request_path = "/api/v2/spot/wallet/modify-deposit-account"
        body = {"accountType": accountType, "coin": coin}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_account_bills(self, coin=None, groupType=None, businessType=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/spot/account/bills"
        params = {}
        if coin:
            params["coin"] = coin
        if groupType:
            params["groupType"] = groupType
        if businessType:
            params["businessType"] = businessType
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_transferable_coin_list(self, fromType, toType):
        request_path = "/api/v2/spot/wallet/transfer-coin-info"
        params = {"fromType": fromType, "toType": toType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_main_sub_transfer_record(self, coin=None, role=None, subUid=None, startTime=None, endTime=None, clientOid=None, limit=None, idLessThan=None):
        request_path = "/api/v2/spot/account/sub-main-trans-record"
        params = {}
        if coin:
            params["coin"] = coin
        if role:
            params["role"] = role
        if subUid:
            params["subUid"] = subUid
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if clientOid:
            params["clientOid"] = clientOid
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_transfer_record(self, coin, fromType=None, startTime=None, endTime=None, clientOid=None, pageNum=None, limit=None, idLessThan=None):
        request_path = "/api/v2/spot/account/transferRecords"
        params = {"coin": coin}
        if fromType:
            params["fromType"] = fromType
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if clientOid:
            params["clientOid"] = clientOid
        if pageNum:
            params["pageNum"] = pageNum
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def switch_bgb_deduct(self, deduct):
        request_path = "/api/v2/spot/account/switch-deduct"
        body = {"deduct": deduct}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_sub_account_deposit_address(self, subUid, coin, chain=None, size=None):
        request_path = "/api/v2/spot/wallet/subaccount-deposit-address"
        params = {"subUid": subUid, "coin": coin}
        if chain:
            params["chain"] = chain
        if size:
            params["size"] = size
        return await self.client._send_request("GET", request_path, params=params)

    async def get_bgb_deduct_info(self):
        request_path = "/api/v2/spot/account/deduct-info"
        return await self.client._send_request("GET", request_path)

    async def get_sub_account_deposit_records(self, subUid, coin=None, startTime=None, endTime=None, idLessThan=None, limit=None):
        request_path = "/api/v2/spot/wallet/subaccount-deposit-records"
        params = {"subUid": subUid}
        if coin:
            params["coin"] = coin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def upgrade_account(self, subUid=None):
        request_path = "/api/v2/spot/account/upgrade"
        body = {}
        if subUid:
            body["subUid"] = subUid
        return await self.client._send_request("POST", request_path, body=body)

    async def get_upgrade_status(self, subUid=None):
        request_path = "/api/v2/spot/account/upgrade-status"
        params = {}
        if subUid:
            params["subUid"] = subUid
        return await self.client._send_request("GET", request_path, params=params)

    async def get_ticker_information(self, symbol=None):
        request_path = "/api/v2/spot/market/tickers"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self.client._send_request("GET", request_path, params=params)

    async def get_merge_depth(self, symbol, precision=None, limit=None):
        request_path = "/api/v2/spot/market/merge-depth"
        params = {"symbol": symbol}
        if precision:
            params["precision"] = precision
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_orderbook_depth(self, symbol, type=None, limit=None):
        request_path = "/api/v2/spot/market/orderbook"
        params = {"symbol": symbol}
        if type:
            params["type"] = type
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_candlestick_data(self, symbol, granularity, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/spot/market/candles"
        params = {"symbol": symbol, "granularity": granularity}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_call_auction_information(self, symbol):
        request_path = "/api/v2/spot/market/auction"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_candlestick_data(self, symbol, granularity, endTime, limit=None):
        request_path = "/api/v2/spot/market/history-candles"
        params = {"symbol": symbol, "granularity": granularity, "endTime": endTime}
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_recent_trades(self, symbol, limit=None):
        request_path = "/api/v2/spot/market/fills"
        params = {"symbol": symbol}
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_market_trades(self, symbol, limit=None, idLessThan=None, startTime=None, endTime=None):
        request_path = "/api/v2/spot/market/fills-history"
        params = {"symbol": symbol}
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_vip_fee_rate(self):
        request_path = "/api/v2/spot/market/vip-fee-rate"
        return await self.client._send_request("GET", request_path)

    async def place_order(self, symbol, side, orderType, force, size, price=None, clientOid=None, triggerPrice=None, tpslType=None, requestTime=None, receiveWindow=None, stpMode=None, presetTakeProfitPrice=None, executeTakeProfitPrice=None, presetStopLossPrice=None, executeStopLossPrice=None):
        request_path = "/api/v2/spot/trade/place-order"
        body = {
            "symbol": symbol,
            "side": side,
            "orderType": orderType,
            "force": force,
            "size": size
        }
        if price:
            body["price"] = price
        if clientOid:
            body["clientOid"] = clientOid
        if triggerPrice:
            body["triggerPrice"] = triggerPrice
        if tpslType:
            body["tpslType"] = tpslType
        if requestTime:
            body["requestTime"] = requestTime
        if receiveWindow:
            body["receiveWindow"] = receiveWindow
        if stpMode:
            body["stpMode"] = stpMode
        if presetTakeProfitPrice:
            body["presetTakeProfitPrice"] = presetTakeProfitPrice
        if executeTakeProfitPrice:
            body["executeTakeProfitPrice"] = executeTakeProfitPrice
        if presetStopLossPrice:
            body["presetStopLossPrice"] = presetStopLossPrice
        if executeStopLossPrice:
            body["executeStopLossPrice"] = executeStopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_replace_order(self, symbol, price, size, clientOid=None, orderId=None, newClientOid=None, presetTakeProfitPrice=None, executeTakeProfitPrice=None, presetStopLossPrice=None, executeStopLossPrice=None):
        request_path = "/api/v2/spot/trade/cancel-replace-order"
        body = {
            "symbol": symbol,
            "price": price,
            "size": size
        }
        if clientOid:
            body["clientOid"] = clientOid
        if orderId:
            body["orderId"] = orderId
        if newClientOid:
            body["newClientOid"] = newClientOid
        if presetTakeProfitPrice:
            body["presetTakeProfitPrice"] = presetTakeProfitPrice
        if executeTakeProfitPrice:
            body["executeTakeProfitPrice"] = executeTakeProfitPrice
        if presetStopLossPrice:
            body["presetStopLossPrice"] = presetStopLossPrice
        if executeStopLossPrice:
            body["executeStopLossPrice"] = executeStopLossPrice
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_cancel_replace_order(self, orderList):
        request_path = "/api/v2/spot/trade/batch-cancel-replace-order"
        body = {"orderList": orderList}
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_order(self, symbol, orderId=None, clientOid=None, tpslType=None):
        request_path = "/api/v2/spot/trade/cancel-order"
        body = {"symbol": symbol}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if tpslType:
            body["tpslType"] = tpslType
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_cancel_orders(self, orderList, symbol=None, batchMode=None):
        request_path = "/api/v2/spot/trade/batch-cancel-order"
        body = {"orderList": orderList}
        if symbol:
            body["symbol"] = symbol
        if batchMode:
            body["batchMode"] = batchMode
        return await self.client._send_request("POST", request_path, body=body)

    async def batch_place_orders(self, orderList, symbol=None, batchMode=None):
        request_path = "/api/v2/spot/trade/batch-orders"
        body = {"orderList": orderList}
        if symbol:
            body["symbol"] = symbol
        if batchMode:
            body["batchMode"] = batchMode
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_order_by_symbol(self, symbol):
        request_path = "/api/v2/spot/trade/cancel-symbol-order"
        body = {"symbol": symbol}
        return await self.client._send_request("POST", request_path, body=body)

    async def cancel_plan_order(self, orderId=None, clientOid=None):
        request_path = "/api/v2/spot/trade/cancel-plan-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)

    async def get_order_info(self, orderId=None, clientOid=None, requestTime=None, receiveWindow=None):
        request_path = "/api/v2/spot/trade/orderInfo"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if requestTime:
            params["requestTime"] = requestTime
        if receiveWindow:
            params["receiveWindow"] = receiveWindow
        return await self.client._send_request("GET", request_path, params=params)

    async def get_current_orders(self, symbol=None, startTime=None, endTime=None, idLessThan=None, limit=None, orderId=None, tpslType=None, requestTime=None, receiveWindow=None):
        request_path = "/api/v2/spot/trade/unfilled-orders"
        params = {}
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
        if orderId:
            params["orderId"] = orderId
        if tpslType:
            params["tpslType"] = tpslType
        if requestTime:
            params["requestTime"] = requestTime
        if receiveWindow:
            params["receiveWindow"] = receiveWindow
        return await self.client._send_request("GET", request_path, params=params)

    async def get_history_orders(self, symbol=None, startTime=None, endTime=None, idLessThan=None, limit=None, orderId=None, tpslType=None, requestTime=None, receiveWindow=None):
        request_path = "/api/v2/spot/trade/history-orders"
        params = {}
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
        if orderId:
            params["orderId"] = orderId
        if tpslType:
            params["tpslType"] = tpslType
        if requestTime:
            params["requestTime"] = requestTime
        if receiveWindow:
            params["receiveWindow"] = receiveWindow
        return await self.client._send_request("GET", request_path, params=params)

    async def get_fills(self, symbol=None, orderId=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/spot/trade/fills"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if orderId:
            params["orderId"] = orderId
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def place_plan_order(self, symbol, side, triggerPrice, orderType, size, executePrice=None, planType=None, triggerType=None, clientOid=None, stpMode=None):
        request_path = "/api/v2/spot/trade/place-plan-order"
        body = {
            "symbol": symbol,
            "side": side,
            "triggerPrice": triggerPrice,
            "orderType": orderType,
            "size": size
        }
        if executePrice:
            body["executePrice"] = executePrice
        if planType:
            body["planType"] = planType
        if triggerType:
            body["triggerType"] = triggerType
        if clientOid:
            body["clientOid"] = clientOid
        if stpMode:
            body["stpMode"] = stpMode
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_plan_order(self, triggerPrice, orderType, size, orderId=None, clientOid=None, executePrice=None):
        request_path = "/api/v2/spot/trade/modify-plan-order"
        body = {
            "triggerPrice": triggerPrice,
            "orderType": orderType,
            "size": size
        }
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if executePrice:
            body["executePrice"] = executePrice
        return await self.client._send_request("POST", request_path, body=body)

    async def get_current_plan_orders(self, symbol=None, limit=None, idLessThan=None, startTime=None, endTime=None):
        request_path = "/api/v2/spot/trade/current-plan-order"
        params = {}
        if symbol:
            params["symbol"] = symbol
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_plan_sub_order(self, planOrderId):
        request_path = "/api/v2/spot/trade/plan-sub-order"
        params = {"planOrderId": planOrderId}
        return await self.client._send_request("GET", request_path, params=params)

    def get_history_plan_orders(self, symbol, startTime, endTime, limit=None):
        request_path = "/api/v2/spot/trade/history-plan-order"
        params = {"symbol": symbol, "startTime": startTime, "endTime": endTime}
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def cancel_plan_orders_in_batch(self, symbolList=None):
        request_path = "/api/v2/spot/trade/batch-cancel-plan-order"
        body = {}
        if symbolList:
            body["symbolList"] = symbolList
        return self.client._send_request("POST", request_path, body=body)
