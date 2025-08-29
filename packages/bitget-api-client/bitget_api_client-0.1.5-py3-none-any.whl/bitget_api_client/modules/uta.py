from .exceptions import BitgetAPIException
import time

class Uta:
    def __init__(self, client):
        self.client = client

    def get_account_info(self):
        request_path = "/api/v3/account/settings"
        return self.client._send_request("GET", request_path, params={})

    def get_account_assets(self):
        request_path = "/api/v3/account/assets"
        return self.client._send_request("GET", request_path, params={})

    def get_account_funding_assets(self, coin=None):
        request_path = "/api/v3/account/funding-assets"
        params = {}
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_account_fee_rate(self, symbol, category):
        request_path = "/api/v3/account/fee-rate"
        params = {"symbol": symbol, "category": category}
        return self.client._send_request("GET", request_path, params=params)

    def get_convert_records(self, fromCoin, toCoin, startTime=None, endTime=None, limit=None, cursor=None):
        request_path = "/api/v3/account/convert-records"
        params = {"fromCoin": fromCoin, "toCoin": toCoin}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_deduct_info(self):
        request_path = "/api/v3/account/deduct-info"
        return self.client._send_request("GET", request_path, params={})

    def get_financial_records(self, category, coin=None, type=None, startTime=None, endTime=None, limit=None, cursor=None):
        request_path = "/api/v3/account/financial-records"
        params = {"category": category}
        if coin:
            params["coin"] = coin
        if type:
            params["type"] = type
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def subscribe_account_channel(self):
        message = {
            "op": "subscribe",
            "args": [
                {
                    "instType": "UTA",
                    "topic": "account"
                }
            ]
        }
        return self.client._send_websocket_request(message)

    def get_payment_coins(self):
        request_path = "/api/v3/account/payment-coins"
        return self.client._send_request("GET", request_path, params={})

    def get_margin_coin_info(self, productId):
        request_path = "/api/v3/ins-loan/ensure-coins-convert"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_margin_loan(self, coin):
        request_path = "/api/v3/market/margin-loans"
        params = {"coin": coin}
        return self.client._send_request("GET", request_path, params=params)

    def get_ltv(self, riskUnitId=None):
        request_path = "/api/v3/ins-loan/ltv-convert"
        params = {}
        if riskUnitId:
            params["riskUnitId"] = riskUnitId
        return self.client._send_request("GET", request_path, params=params)

    def batch_cancel(self, orders):
        request_path = "/api/v3/trade/cancel-batch"
        return self.client._send_request("POST", request_path, body=orders)

    def batch_modify_orders(self, orderList):
        request_path = "/api/v3/trade/batch-modify-order"
        return self.client._send_request("POST", request_path, body=orderList)

    def batch_order(self, orderList):
        request_path = "/api/v3/trade/place-batch"
        return self.client._send_request("POST", request_path, body=orderList)

    def bind_unbind_uid_to_risk_unit(self, uid, operate, riskUnitId=None):
        request_path = "/api/v3/ins-loan/bind-uid"
        body = {
            "uid": uid,
            "operate": operate
        }
        if riskUnitId:
            body["riskUnitId"] = riskUnitId
        return self.client._send_request("POST", request_path, body=body)

    def batch_place_order_channel(self, category, orders):
        message = {
            "op": "trade",
            "id": str(int(time.time() * 1000)), # Generate a unique ID
            "category": category,
            "topic": "batch-place",
            "args": orders
        }
        return self.client._send_websocket_request(message)

    def cancel_all_orders(self, category, symbol=None):
        request_path = "/api/v3/trade/cancel-symbol-order"
        body = {"category": category}
        if symbol:
            body["symbol"] = symbol
        return self.client._send_request("POST", request_path, body=body)

    def cancel_order(self, orderId=None, clientOid=None):
        request_path = "/api/v3/trade/cancel-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return self.client._send_request("POST", request_path, body=body)

    def cancel_strategy_order(self, orderId=None, clientOid=None):
        request_path = "/api/v3/trade/cancel-strategy-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return self.client._send_request("POST", request_path, body=body)

    def close_all_positions(self, category, symbol=None, posSide=None):
        request_path = "/api/v3/trade/close-positions"
        body = {"category": category}
        if symbol:
            body["symbol"] = symbol
        if posSide:
            body["posSide"] = posSide
        return self.client._send_request("POST", request_path, body=body)

    def countdown_cancel_all(self, countdown):
        request_path = "/api/v3/trade/countdown-cancel-all"
        body = {"countdown": countdown}
        return self.client._send_request("POST", request_path, body=body)

    def create_sub_account_api_key(self, subUid, note, type, passphrase, permissions, ips):
        request_path = "/api/v3/user/create-sub-api"
        body = {
            "subUid": subUid,
            "note": note,
            "type": type,
            "passphrase": passphrase,
            "permissions": permissions,
            "ips": ips
        }
        return self.client._send_request("POST", request_path, body=body)

    def create_sub_account(self, username, accountMode=None, note=None):
        request_path = "/api/v3/user/create-sub"
        body = {"username": username}
        if accountMode:
            body["accountMode"] = accountMode
        if note:
            body["note"] = note
        return self.client._send_request("POST", request_path, body=body)

    def freeze_unfreeze_sub_account(self, subUid, operation):
        request_path = "/api/v3/user/freeze-sub"
        body = {
            "subUid": subUid,
            "operation": operation
        }
        return self.client._send_request("POST", request_path, body=body)

    def delete_sub_account_api_key(self, apiKey):
        request_path = "/api/v3/user/delete-sub-api"
        body = {"apiKey": apiKey}
        return self.client._send_request("POST", request_path, body=body)

    def get_current_funding_rate(self, symbol):
        request_path = "/api/v3/market/current-fund-rate"
        params = {"symbol": symbol}
        return self.client._send_request("GET", request_path, params=params)

    def get_deposit_address(self, coin, chain=None, size=None):
        request_path = "/api/v3/account/deposit-address"
        params = {"coin": coin}
        if chain:
            params["chain"] = chain
        if size:
            params["size"] = size
        return self.client._send_request("GET", request_path, params=params)

    def get_deposit_records(self, startTime, endTime, coin=None, orderId=None, limit=None, cursor=None):
        request_path = "/api/v3/account/deposit-records"
        params = {"startTime": startTime, "endTime": endTime}
        if coin:
            params["coin"] = coin
        if orderId:
            params["orderId"] = orderId
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_fill_history(self, startTime, endTime, category=None, orderId=None, limit=None, cursor=None):
        request_path = "/api/v3/trade/fills"
        params = {"startTime": startTime, "endTime": endTime}
        if category:
            params["category"] = category
        if orderId:
            params["orderId"] = orderId
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_funding_rate_history(self, category, symbol, cursor=None, limit=None):
        request_path = "/api/v3/market/history-fund-rate"
        params = {"category": category, "symbol": symbol}
        if cursor:
            params["cursor"] = cursor
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_instruments(self, category, symbol=None):
        request_path = "/api/v3/market/instruments"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_historical_candlestick_uta(self, category, symbol, interval, startTime=None, endTime=None, type=None, limit=None):
        request_path = "/api/v3/market/history-candles"
        params = {"category": category, "symbol": symbol, "interval": interval}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if type:
            params["type"] = type
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_kline_candlestick(self, category, symbol, interval, startTime=None, endTime=None, type=None, limit=None):
        request_path = "/api/v3/market/candles"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if type:
            params["type"] = type
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_loan_orders(self, orderId=None, startTime=None, endTime=None):
        request_path = "/api/v3/ins-loan/loan-order"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return self.client._send_request("GET", request_path, params=params)

    def get_max_open_available(self, category, symbol, orderType, side, price=None, size=None):
        request_path = "/api/v3/account/max-open-available"
        body = {
            "category": category,
            "symbol": symbol,
            "orderType": orderType,
            "side": side
        }
        if price:
            body["price"] = price
        if size:
            body["size"] = size
        return self.client._send_request("POST", request_path, body=body)

    def get_open_interest_limit(self, category, symbol=None):
        request_path = "/api/v3/market/oi-limit"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_open_interest(self, category, symbol=None):
        request_path = "/api/v3/market/open-interest"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_open_orders(self, category=None, symbol=None, startTime=None, endTime=None, limit=None, cursor=None):
        request_path = "/api/v3/trade/unfilled-orders"
        params = {}
        if category:
            params["category"] = category
        if symbol:
            params["symbol"] = symbol
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_order_details(self, orderId=None, clientOid=None):
        request_path = "/api/v3/trade/order-info"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        return self.client._send_request("GET", request_path, params=params)

    def get_order_history(self, category, symbol=None, startTime=None, endTime=None, limit=None, cursor=None):
        request_path = "/api/v3/trade/history-orders"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_orderbook(self, category, symbol, limit=None):
        request_path = "/api/v3/market/orderbook"
        params = {
            "category": category,
            "symbol": symbol
        }
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_position_adl_rank(self):
        request_path = "/api/v3/position/adlRank"
        return self.client._send_request("GET", request_path, params={})

    def get_position_info(self, category, symbol=None, posSide=None):
        request_path = "/api/v3/position/current-position"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if posSide:
            params["posSide"] = posSide
        return self.client._send_request("GET", request_path, params=params)

    def get_position_tier(self, category, symbol=None, coin=None):
        request_path = "/api/v3/market/position-tier"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_positions_history(self, category, symbol=None, startTime=None, endTime=None, limit=None, cursor=None):
        request_path = "/api/v3/position/history-position"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_proof_of_reserves(self):
        request_path = "/api/v3/market/proof-of-reserves"
        return self.client._send_request("GET", request_path, params={})

    def get_repayment_orders(self, startTime=None, endTime=None, limit=None):
        request_path = "/api/v3/ins-loan/repaid-history"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_risk_reserve(self, category, symbol):
        request_path = "/api/v3/market/risk-reserve"
        params = {
            "category": category,
            "symbol": symbol
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_risk_unit(self):
        request_path = "/api/v3/ins-loan/risk-unit"
        return self.client._send_request("GET", request_path, params={})

    def get_sub_account_api_keys(self, subUid, limit=None, cursor=None):
        request_path = "/api/v3/user/sub-api-list"
        params = {"subUid": subUid}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_sub_account_list(self, limit=None, cursor=None):
        request_path = "/api/v3/user/sub-list"
        params = {}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_subaccount_unified_assets(self, subUid=None, cursor=None, limit=None):
        request_path = "/api/v3/account/sub-unified-assets"
        params = {}
        if subUid:
            params["subUid"] = subUid
        if cursor:
            params["cursor"] = cursor
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_switch_status(self):
        request_path = "/api/v3/account/switch-status"
        return self.client._send_request("GET", request_path, params={})

    def get_main_sub_transfer_records(self, subUid=None, role=None, coin=None, startTime=None, endTime=None, clientOid=None, limit=None, cursor=None):
        request_path = "/api/v3/account/sub-transfer-record"
        params = {}
        if subUid:
            params["subUid"] = subUid
        if role:
            params["role"] = role
        if coin:
            params["coin"] = coin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if clientOid:
            params["clientOid"] = clientOid
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_tickers(self, category, symbol=None):
        request_path = "/api/v3/market/tickers"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_trade_symbols(self, productId):
        request_path = "/api/v3/ins-loan/symbols"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_transferable_coins(self, fromType, toType):
        request_path = "/api/v3/account/transferable-coins"
        params = {
            "fromType": fromType,
            "toType": toType
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_transferred_quantity(self, coin, userId=None):
        request_path = "/api/v3/ins-loan/transfered"
        params = {"coin": coin}
        if userId:
            params["userId"] = userId
        return self.client._send_request("GET", request_path, params=params)

    def get_withdrawal_records(self, startTime, endTime, coin=None, orderId=None, clientOid=None, limit=None, cursor=None):
        request_path = "/api/v3/account/withdrawal-records"
        params = {
            "startTime": startTime,
            "endTime": endTime
        }
        if coin:
            params["coin"] = coin
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def main_sub_account_transfer(self, fromType, toType, amount, coin, fromUserId, toUserId, clientOid):
        request_path = "/api/v3/account/sub-transfer"
        body = {
            "fromType": fromType,
            "toType": toType,
            "amount": amount,
            "coin": coin,
            "fromUserId": fromUserId,
            "toUserId": toUserId,
            "clientOid": clientOid
        }
        return self.client._send_request("POST", request_path, body=body)

    def transfer(self, fromType, toType, amount, coin, symbol=None):
        request_path = "/api/v3/account/transfer"
        body = {
            "fromType": fromType,
            "toType": toType,
            "amount": amount,
            "coin": coin
        }
        if symbol:
            body["symbol"] = symbol
        return self.client._send_request("POST", request_path, body=body)

    def modify_order(self, orderId=None, clientOid=None, qty=None, price=None, autoCancel=None):
        request_path = "/api/v3/trade/modify-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if qty:
            body["qty"] = qty
        if price:
            body["price"] = price
        if autoCancel:
            body["autoCancel"] = autoCancel
        return self.client._send_request("POST", request_path, body=body)

    def history_strategy_orders(self, category, type=None, startTime=None, endTime=None, limit=None, cursor=None):
        request_path = "/api/v3/trade/history-strategy-orders"
        params = {"category": category}
        if type:
            params["type"] = type
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def modify_strategy_order(self, orderId=None, clientOid=None, qty=None, tpTriggerBy=None, slTriggerBy=None, takeProfit=None, stopLoss=None, tpOrderType=None, slOrderType=None, tpLimitPrice=None, slLimitPrice=None):
        request_path = "/api/v3/trade/modify-strategy-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        if qty:
            body["qty"] = qty
        if tpTriggerBy:
            body["tpTriggerBy"] = tpTriggerBy
        if slTriggerBy:
            body["slTriggerBy"] = slTriggerBy
        if takeProfit:
            body["takeProfit"] = takeProfit
        if stopLoss:
            body["stopLoss"] = stopLoss
        if tpOrderType:
            body["tpOrderType"] = tpOrderType
        if slOrderType:
            body["slOrderType"] = slOrderType
        if tpLimitPrice:
            body["tpLimitPrice"] = tpLimitPrice
        if slLimitPrice:
            body["slLimitPrice"] = slLimitPrice
        return self.client._send_request("POST", request_path, body=body)

    def modify_sub_account_api_key(self, apiKey, passphrase, type=None, permissions=None, ips=None):
        request_path = "/api/v3/user/update-sub-api"
        body = {
            "apiKey": apiKey,
            "passphrase": passphrase
        }
        if type:
            body["type"] = type
        if permissions:
            body["permissions"] = permissions
        if ips:
            body["ips"] = ips
        return self.client._send_request("POST", request_path, body=body)

    def place_order(self, category, symbol, qty, side, orderType, price=None, timeInForce=None, posSide=None, clientOid=None, reduceOnly=None, stpMode=None, tpTriggerBy=None, slTriggerBy=None, takeProfit=None, stopLoss=None, tpOrderType=None, slOrderType=None, tpLimitPrice=None, slLimitPrice=None):
        request_path = "/api/v3/trade/place-order"
        body = {
            "category": category,
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "orderType": orderType
        }
        if price:
            body["price"] = price
        if timeInForce:
            body["timeInForce"] = timeInForce
        if posSide:
            body["posSide"] = posSide
        if clientOid:
            body["clientOid"] = clientOid
        if reduceOnly:
            body["reduceOnly"] = reduceOnly
        if stpMode:
            body["stpMode"] = stpMode
        if tpTriggerBy:
            body["tpTriggerBy"] = tpTriggerBy
        if slTriggerBy:
            body["slTriggerBy"] = slTriggerBy
        if takeProfit:
            body["takeProfit"] = takeProfit
        if stopLoss:
            body["stopLoss"] = stopLoss
        if tpOrderType:
            body["tpOrderType"] = tpOrderType
        if slOrderType:
            body["slOrderType"] = slOrderType
        if tpLimitPrice:
            body["tpLimitPrice"] = tpLimitPrice
        if slLimitPrice:
            body["slLimitPrice"] = slLimitPrice
        return self.client._send_request("POST", request_path, body=body)

    def place_strategy_order(self, category, symbol, posSide, clientOid=None, type=None, tpslMode=None, qty=None, tpTriggerBy=None, slTriggerBy=None, takeProfit=None, stopLoss=None, tpOrderType=None, slOrderType=None, tpLimitPrice=None, slLimitPrice=None):
        request_path = "/api/v3/trade/place-strategy-order"
        body = {
            "category": category,
            "symbol": symbol,
            "posSide": posSide
        }
        if clientOid:
            body["clientOid"] = clientOid
        if type:
            body["type"] = type
        if tpslMode:
            body["tpslMode"] = tpslMode
        if qty:
            body["qty"] = qty
        if tpTriggerBy:
            body["tpTriggerBy"] = tpTriggerBy
        if slTriggerBy:
            body["slTriggerBy"] = slTriggerBy
        if takeProfit:
            body["takeProfit"] = takeProfit
        if stopLoss:
            body["stopLoss"] = stopLoss
        if tpOrderType:
            body["tpOrderType"] = tpOrderType
        if slOrderType:
            body["slOrderType"] = slOrderType
        if tpLimitPrice:
            body["tpLimitPrice"] = tpLimitPrice
        if slLimitPrice:
            body["slLimitPrice"] = slLimitPrice
        return self.client._send_request("POST", request_path, body=body)

    def subscribe_position_channel(self):
        message = {
            "op": "subscribe",
            "args": [
                {
                    "instType": "UTA",
                    "topic": "position"
                }
            ]
        }
        return self.client._send_websocket_request(message)

    def subscribe_order_channel(self):
        message = {
            "op": "subscribe",
            "args": [
                {
                    "instType": "UTA",
                    "topic": "order"
                }
            ]
        }
        return self.client._send_websocket_request(message)

    def subscribe_public_trades_channel(self, instType, symbol):
        message = {
            "op": "subscribe",
            "args": [
                {
                    "instType": instType,
                    "topic": "publicTrade",
                    "symbol": symbol
                }
            ]
        }
        return self.client._send_websocket_request(message)

    def subscribe_tickers_channel(self, instType, symbol):
        message = {
            "op": "subscribe",
            "args": [
                {
                    "instType": instType,
                    "topic": "ticker",
                    "symbol": symbol
                }
            ]
        }
        return self.client._send_websocket_request(message)

    def repay(self, repayableCoinList, paymentCoinList):
        request_path = "/api/v3/account/repay"
        body = {
            "repayableCoinList": repayableCoinList,
            "paymentCoinList": paymentCoinList
        }
        return self.client._send_request("POST", request_path, body=body)

    def set_holding_mode(self, holdMode):
        request_path = "/api/v3/account/set-hold-mode"
        body = {
            "holdMode": holdMode
        }
        return self.client._send_request("POST", request_path, body=body)

    def set_leverage(self, category, leverage, symbol=None, coin=None, posSide=None):
        request_path = "/api/v3/account/set-leverage"
        body = {
            "category": category,
            "leverage": leverage
        }
        if symbol:
            body["symbol"] = symbol
        if coin:
            body["coin"] = coin
        if posSide:
            body["posSide"] = posSide
        return self.client._send_request("POST", request_path, body=body)

    def set_up_deposit_account(self, coin, accountType):
        request_path = "/api/v3/account/deposit-account"
        body = {
            "coin": coin,
            "accountType": accountType
        }
        return self.client._send_request("POST", request_path, body=body)

    def switch_account(self):
        request_path = "/api/v3/account/switch"
        body = {}
        return self.client._send_request("POST", request_path, body=body)

    def switch_deduct(self, deduct):
        request_path = "/api/v3/account/switch-deduct"
        body = {
            "deduct": deduct
        }
        return self.client._send_request("POST", request_path, body=body)

    def withdrawal(self, coin, transferType, address, size, chain=None, innerToType=None, areaCode=None, tag=None, remark=None, clientOid=None, memberCode=None, identityType=None, companyName=None, firstName=None, lastName=None):
        request_path = "/api/v3/account/withdrawal"
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
        if memberCode:
            body["memberCode"] = memberCode
        if identityType:
            body["identityType"] = identityType
        if companyName:
            body["companyName"] = companyName
        if firstName:
            body["firstName"] = firstName
        if lastName:
            body["lastName"] = lastName
        return self.client._send_request("POST", request_path, body=body)

    def get_recent_public_fills(self, category, symbol=None, limit=None):
        request_path = "/api/v3/market/fills"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_repayable_coins(self):
        request_path = "/api/v3/account/repayable-coins"
        return self.client._send_request("GET", request_path, params={})

    def get_product_info(self, productId):
        request_path = "/api/v3/ins-loan/product-infos"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)
