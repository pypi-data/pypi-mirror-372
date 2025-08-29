from .exceptions import BitgetAPIException

class Common:
    def __init__(self, client):
        self.client = client

    async def get_assets_overview(self):
        request_path = "/api/v2/account/all-account-balance"
        return await self.client._send_request("GET", request_path, params={})

    async def get_bot_account_assets(self, accountType=None):
        request_path = "/api/v2/account/bot-assets"
        params = {}
        if accountType:
            params["accountType"] = accountType
        return await self.client._send_request("GET", request_path, params=params)

    async def get_funding_assets(self, coin=None):
        request_path = "/api/v2/account/funding-assets"
        params = {}
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def batch_create_virtual_subaccount_and_apikey(self, subaccounts):
        request_path = "/api/v2/user/batch-create-subaccount-and-apikey"
        return await self.client._send_request("POST", request_path, body=subaccounts)

    async def get_bgb_convert_coins(self):
        request_path = "/api/v2/mix/market/bgb-convert-coins"
        return await self.client._send_request("GET", request_path, params={})

    async def convert(self, fromCoin, fromCoinSize, cnvtPrice, toCoin, toCoinSize, traceId):
        request_path = "/api/v2/convert/trade"
        body = {
            "fromCoin": fromCoin,
            "fromCoinSize": fromCoinSize,
            "cnvtPrice": cnvtPrice,
            "toCoin": toCoin,
            "toCoinSize": toCoinSize,
            "traceId": traceId
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def convert_bgb(self, coinList):
        request_path = "/api/v2/convert/bgb-convert"
        body = {"coinList": coinList}
        return await self.client._send_request("POST", request_path, body=body)

    async def create_virtual_subaccount(self, subAccountList):
        request_path = "/api/v2/user/create-virtual-subaccount"
        body = {"subAccountList": subAccountList}
        return await self.client._send_request("POST", request_path, body=body)

    async def create_virtual_subaccount_apikey(self, subAccountUid, passphrase, label, permType, ipList=None, permList=None):
        request_path = "/api/v2/user/create-virtual-subaccount-apikey"
        body = {
            "subAccountUid": subAccountUid,
            "passphrase": passphrase,
            "label": label,
            "permType": permType
        }
        if ipList:
            body["ipList"] = ipList
        if permList:
            body["permList"] = permList
        return await self.client._send_request("POST", request_path, body=body)

    async def get_convert_history(self, startTime=None, endTime=None, pageNo=None, pageSize=None):
        request_path = "/api/v2/convert/record"
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

    async def get_futures_transaction_records(self, startTime, endTime, productType=None, marginCoin=None, limit=None, idLessThan=None):
        request_path = "/api/v2/tax/future-record"
        params = {"startTime": startTime, "endTime": endTime}
        if productType:
            params["productType"] = productType
        if marginCoin:
            params["marginCoin"] = marginCoin
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_margin_transaction_history(self, startTime, endTime, marginType=None, coin=None, limit=None, idLessThan=None):
        request_path = "/api/v2/tax/margin-record"
        params = {"startTime": startTime, "endTime": endTime}
        if marginType:
            params["marginType"] = marginType
        if coin:
            params["coin"] = coin
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_p2p_transaction_records(self, startTime, endTime, coin=None, limit=None, idLessThan=None):
        request_path = "/api/v2/tax/p2p-record"
        params = {"startTime": startTime, "endTime": endTime}
        if coin:
            params["coin"] = coin
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def query_announcements(self, language, annType=None, startTime=None, endTime=None, cursor=None, limit=None):
        request_path = "/api/v2/public/annoucements"
        params = {"language": language}
        if annType:
            params["annType"] = annType
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if cursor:
            params["cursor"] = cursor
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_transaction_records(self, startTime, endTime, coin=None, limit=None, idLessThan=None):
        request_path = "/api/v2/tax/spot-record"
        params = {"startTime": startTime, "endTime": endTime}
        if coin:
            params["coin"] = coin
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def get_business_line_all_symbol_trade_rate(self, symbol, businessType):
        request_path = "/api/v2/common/all-trade-rate"
        params = {"symbol": symbol, "businessType": businessType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_convert_coins(self):
        request_path = "/api/v2/convert/currencies"
        return await self.client._send_request("GET", request_path, params={})

    async def get_futures_active_buy_sell_volume_data(self, symbol, period=None):
        request_path = "/api/v2/mix/market/taker-buy-sell"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_futures_active_long_short_account_data(self, symbol, period=None):
        request_path = "/api/v2/mix/market/account-long-short"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_futures_active_long_short_position_data(self, symbol, period=None):
        request_path = "/api/v2/mix/market/position-long-short"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_futures_long_and_short_ratio_data(self, symbol, period=None):
        request_path = "/api/v2/mix/market/long-short"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_leveraged_long_short_ratio_data(self, symbol, period=None, coin=None):
        request_path = "/api/v2/margin/market/long-short-ratio"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        if coin:
            params["coin"] = coin
        return await self.client._send_request("GET", request_path, params=params)

    async def get_isolated_margin_borrowing_ratio_data(self, symbol, period=None):
        request_path = "/api/v2/mix/market/isolated-borrow-rate"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_margin_loan_growth_rate_data(self, symbol, period=None):
        request_path = "/api/v2/mix/market/margin-loan-ratio"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_merchant_advertisement_list(self, buySell, country=None, pageNo=None, pageSize=None, currency=None):
        request_path = "/api/v2/p2p/merchant/adv-list"
        params = {"buySell": buySell}
        if country:
            params["country"] = country
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        if currency:
            params["currency"] = currency
        return await self.client._send_request("GET", request_path, params=params)

    async def get_merchant_information(self):
        request_path = "/api/v2/p2p/merchantInfo"
        return await self.client._send_request("GET", request_path, params={})

    async def get_merchant_p2p_orders(self, startTime=None, endTime=None, pageNo=None, pageSize=None, orderType=None, status=None, currency=None):
        request_path = "/api/v2/p2p/merchant/order-list"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        if orderType:
            params["orderType"] = orderType
        if status:
            params["status"] = status
        if currency:
            params["currency"] = currency
        return await self.client._send_request("GET", request_path, params=params)

    async def get_p2p_merchant_list(self, online=None, idLessThan=None, limit=None):
        request_path = "/api/v2/p2p/merchantList"
        params = {}
        if online:
            params["online"] = online
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        return await self.client._send_request("GET", request_path, params=params)

    async def get_quoted_price(self, fromCoin, toCoin, fromCoinSize=None, toCoinSize=None):
        request_path = "/api/v2/convert/quoted-price"
        params = {"fromCoin": fromCoin, "toCoin": toCoin}
        if fromCoinSize:
            params["fromCoinSize"] = fromCoinSize
        if toCoinSize:
            params["toCoinSize"] = toCoinSize
        return await self.client._send_request("GET", request_path, params=params)

    async def get_server_time(self):
        request_path = "/api/v2/common/time"
        return await self.client._send_request("GET", request_path, params={})

    async def get_spot_fund_flow(self, symbol, period=None):
        request_path = "/api/v2/spot/market/fund-flow"
        params = {"symbol": symbol}
        if period:
            params["period"] = period
        return await self.client._send_request("GET", request_path, params=params)

    async def get_spot_whale_net_flow_data(self, symbol):
        request_path = "/api/v2/spot/market/fund-net-flow"
        params = {"symbol": symbol}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_trade_data_support_symbols(self):
        request_path = "/api/v2/spot/market/support-symbols"
        return await self.client._send_request("GET", request_path, params={})

    async def get_trade_rate(self, symbol, businessType):
        request_path = "/api/v2/common/trade-rate"
        params = {"symbol": symbol, "businessType": businessType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_virtual_subaccounts(self):
        request_path = "/api/v2/user/virtual-subaccount-list"
        return await self.client._send_request("GET", request_path, params={})

    async def get_subaccount_apikey_list(self, subAccountUid):
        request_path = "/api/v2/user/virtual-subaccount-apikey-list"
        params = {"subAccountUid": subAccountUid}
        return await self.client._send_request("GET", request_path, params=params)

    async def modify_virtual_subaccount(self, subAccountUid, label=None, status=None, permList=None, language=None):
        request_path = "/api/v2/user/modify-virtual-subaccount"
        body = {"subAccountUid": subAccountUid}
        if label:
            body["label"] = label
        if status:
            body["status"] = status
        if permList:
            body["permList"] = permList
        if language:
            body["language"] = language
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_virtual_subaccount_apikey(self, subAccountUid, subAccountApiKey, passphrase, permType, label=None, ipList=None, permList=None):
        request_path = "/api/v2/user/modify-virtual-subaccount-apikey"
        body = {
            "subAccountUid": subAccountUid,
            "subAccountApiKey": subAccountApiKey,
            "passphrase": passphrase,
            "permType": permType
        }
        if label:
            body["label"] = label
        if ipList:
            body["ipList"] = ipList
        if permList:
            body["permList"] = permList
        return await self.client._send_request("POST", request_path, body=body)