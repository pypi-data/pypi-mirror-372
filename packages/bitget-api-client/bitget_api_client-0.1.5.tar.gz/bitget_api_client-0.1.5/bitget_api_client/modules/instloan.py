from .exceptions import BitgetAPIException

class Instloan:
    def __init__(self, client):
        self.client = client

    def bind_unbind_sub_account_uid_to_risk_unit(self, uid, operate, riskUnitId=None):
        request_path = "/api/v2/spot/ins-loan/bind-uid"
        body = {
            "uid": uid,
            "operate": operate
        }
        if riskUnitId:
            body["riskUnitId"] = riskUnitId
        return self.client._send_request("POST", request_path, body=body)

    def get_loan_orders(self, orderId=None, startTime=None, endTime=None):
        request_path = "/api/v2/spot/ins-loan/loan-order"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return self.client._send_request("GET", request_path, params=params)

    def get_ltv(self, riskUnitId=None):
        request_path = "/api/v2/spot/ins-loan/ltv-convert"
        params = {}
        if riskUnitId:
            params["riskUnitId"] = riskUnitId
        return self.client._send_request("GET", request_path, params=params)

    def get_margin_coin_info(self, productId):
        request_path = "/api/v2/spot/ins-loan/ensure-coins-convert"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_product_info(self, productId):
        request_path = "/api/v2/spot/ins-loan/product-infos"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_repayment_orders(self, startTime=None, endTime=None, limit=None):
        request_path = "/api/v2/spot/ins-loan/repaid-history"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_risk_unit(self):
        request_path = "/api/v2/spot/ins-loan/risk-unit"
        return self.client._send_request("GET", request_path, params={})

    def get_spot_symbols(self, productId):
        request_path = "/api/v2/spot/ins-loan/symbols"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_transferable_amount(self, coin, userId=None):
        request_path = "/api/v2/spot/ins-loan/transfered"
        params = {
            "coin": coin
        }
        if userId:
            params["userId"] = userId
        return self.client._send_request("GET", request_path, params=params)