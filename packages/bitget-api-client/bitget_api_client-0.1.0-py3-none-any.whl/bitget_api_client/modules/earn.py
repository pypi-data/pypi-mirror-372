from .exceptions import BitgetAPIException

class Earn:
    def __init__(self, client):
        self.client = client

    def borrow(self, loanCoin, pledgeCoin, daily, pledgeAmount=None, loanAmount=None):
        request_path = "/api/v2/earn/loan/borrow"
        body = {
            "loanCoin": loanCoin,
            "pledgeCoin": pledgeCoin,
            "daily": daily
        }
        if pledgeAmount:
            body["pledgeAmount"] = pledgeAmount
        if loanAmount:
            body["loanAmount"] = loanAmount
        
        # Ensure either pledgeAmount or loanAmount is provided
        if pledgeAmount is None and loanAmount is None:
            raise ValueError("Either 'pledgeAmount' or 'loanAmount' must be provided.")

        return self.client._send_request("POST", request_path, body=body)

    def get_earn_account_assets(self, coin=None):
        request_path = "/api/v2/earn/account/assets"
        params = {}
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_currency_list(self, coin=None):
        request_path = "/api/v2/earn/loan/public/coinInfos"
        params = {}
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_debts(self):
        request_path = "/api/v2/earn/loan/debts"
        return self.client._send_request("GET", request_path, params={})

    def get_est_interest_and_borrowable(self, loanCoin, pledgeCoin, daily, pledgeAmount):
        request_path = "/api/v2/earn/loan/public/hour-interest"
        params = {
            "loanCoin": loanCoin,
            "pledgeCoin": pledgeCoin,
            "daily": daily,
            "pledgeAmount": pledgeAmount
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_liquidation_records(self, startTime, endTime, orderId=None, loanCoin=None, pledgeCoin=None, status=None, pageNo=None, pageSize=None):
        request_path = "/api/v2/earn/loan/reduces"
        params = {
            "startTime": startTime,
            "endTime": endTime
        }
        if orderId:
            params["orderId"] = orderId
        if loanCoin:
            params["loanCoin"] = loanCoin
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        if status:
            params["status"] = status
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return self.client._send_request("GET", request_path, params=params)

    def get_loan_history(self, startTime, endTime, orderId=None, loanCoin=None, pledgeCoin=None, status=None, pageNo=None, pageSize=None):
        request_path = "/api/v2/earn/loan/borrow-history"
        params = {
            "startTime": startTime,
            "endTime": endTime
        }
        if orderId:
            params["orderId"] = orderId
        if loanCoin:
            params["loanCoin"] = loanCoin
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        if status:
            params["status"] = status
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return self.client._send_request("GET", request_path, params=params)

    def get_loan_orders(self, orderId=None, loanCoin=None, pledgeCoin=None):
        request_path = "/api/v2/earn/loan/ongoing-orders"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if loanCoin:
            params["loanCoin"] = loanCoin
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        return self.client._send_request("GET", request_path, params=params)

    def get_pledge_rate_history(self, startTime, endTime, orderId=None, reviseSide=None, pledgeCoin=None, pageNo=None, pageSize=None):
        request_path = "/api/v2/earn/loan/revise-history"
        params = {
            "startTime": startTime,
            "endTime": endTime
        }
        if orderId:
            params["orderId"] = orderId
        if reviseSide:
            params["reviseSide"] = reviseSide
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return self.client._send_request("GET", request_path, params=params)

    def get_repay_history(self, startTime, endTime, orderId=None, loanCoin=None, pledgeCoin=None, pageNo=None, pageSize=None):
        request_path = "/api/v2/earn/loan/repay-history"
        params = {
            "startTime": startTime,
            "endTime": endTime
        }
        if orderId:
            params["orderId"] = orderId
        if loanCoin:
            params["loanCoin"] = loanCoin
        if pledgeCoin:
            params["pledgeCoin"] = pledgeCoin
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        return self.client._send_request("GET", request_path, params=params)

    def modify_pledge_rate(self, orderId, amount, pledgeCoin, reviseType):
        request_path = "/api/v2/earn/loan/revise-pledge"
        body = {
            "orderId": orderId,
            "amount": amount,
            "pledgeCoin": pledgeCoin,
            "reviseType": reviseType
        }
        return self.client._send_request("POST", request_path, body=body)

    def redeem_savings(self, productId, periodType, amount, orderId=None):
        request_path = "/api/v2/earn/savings/redeem"
        body = {
            "productId": productId,
            "periodType": periodType,
            "amount": amount
        }
        if orderId:
            body["orderId"] = orderId
        return self.client._send_request("POST", request_path, body=body)

    def repay(self, orderId, repayAll, amount=None, repayUnlock=None):
        request_path = "/api/v2/earn/loan/repay"
        body = {
            "orderId": orderId,
            "repayAll": repayAll
        }
        if amount:
            body["amount"] = amount
        if repayUnlock:
            body["repayUnlock"] = repayUnlock
        return self.client._send_request("POST", request_path, body=body)

    def get_savings_account(self):
        request_path = "/api/v2/earn/savings/account"
        return self.client._send_request("GET", request_path, params={})

    def get_savings_product_list(self, coin=None, filter=None):
        request_path = "/api/v2/earn/savings/product"
        params = {}
        if coin:
            params["coin"] = coin
        if filter:
            params["filter"] = filter
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_records(self, periodType, coin=None, orderType=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/earn/savings/records"
        params = {
            "periodType": periodType
        }
        if coin:
            params["coin"] = coin
        if orderType:
            params["orderType"] = orderType
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_subscription_detail(self, productId, periodType):
        request_path = "/api/v2/earn/savings/subscribe-info"
        params = {
            "productId": productId,
            "periodType": periodType
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_subscription_result(self, productId, periodType):
        request_path = "/api/v2/earn/savings/subscribe-result"
        params = {
            "productId": productId,
            "periodType": periodType
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_redemption_results(self, orderId, periodType):
        request_path = "/api/v2/earn/savings/redeem-result"
        params = {
            "orderId": orderId,
            "periodType": periodType
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_sharkfin_account(self):
        request_path = "/api/v2/earn/sharkfin/account"
        return self.client._send_request("GET", request_path, params={})

    def get_sharkfin_assets(self, status, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/earn/sharkfin/assets"
        params = {
            "status": status
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)

    def get_sharkfin_products(self, coin, limit=None, idLessThan=None):
        request_path = "/api/v2/earn/sharkfin/product"
        params = {
            "coin": coin
        }
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)

    def get_sharkfin_subscription_result(self, orderId):
        request_path = "/api/v2/earn/sharkfin/subscribe-result"
        params = {
            "orderId": orderId
        }
        return self.client._send_request("GET", request_path, params=params)

    def subscribe_savings(self, productId, periodType, amount):
        request_path = "/api/v2/earn/savings/subscribe"
        body = {
            "productId": productId,
            "periodType": periodType,
            "amount": amount
        }
        return self.client._send_request("POST", request_path, body=body)

    def subscribe_sharkfin(self, productId, amount):
        request_path = "/api/v2/earn/sharkfin/subscribe"
        body = {
            "productId": productId,
            "amount": amount
        }
        return self.client._send_request("POST", request_path, body=body)

    def get_sharkfin_records(self, type, coin=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/earn/sharkfin/records"
        params = {
            "type": type
        }
        if coin:
            params["coin"] = coin
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)

    def get_sharkfin_subscription_detail(self, productId):
        request_path = "/api/v2/earn/sharkfin/subscribe-info"
        params = {
            "productId": productId
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_savings_assets(self, periodType, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/earn/savings/assets"
        params = {
            "periodType": periodType
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return self.client._send_request("GET", request_path, params=params)