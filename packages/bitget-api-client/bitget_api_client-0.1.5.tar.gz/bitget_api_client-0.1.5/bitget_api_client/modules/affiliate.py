from .exceptions import BitgetAPIException

class Affiliate:
    def __init__(self, client):
        self.client = client

    async def get_agent_direct_commissions(self, startTime=None, endTime=None, idLessThan=None, limit=None, uid=None, coin=None, symbol=None):
        request_path = "/api/broker/v1/agent/customer-commissions"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if idLessThan:
            params["idLessThan"] = idLessThan
        if limit:
            params["limit"] = limit
        if uid:
            params["uid"] = uid
        if coin:
            params["coin"] = coin
        if symbol:
            params["symbol"] = symbol
        
        return await self.client._send_request("GET", request_path, params=params)

    async def get_agent_customer_trade_volume_list(self, startTime=None, endTime=None, pageNo=None, pageSize=None, uid=None):
        request_path = "/api/broker/v1/agent/customerTradeVolumnList"
        body = {}
        if startTime:
            body["startTime"] = startTime
        if endTime:
            body["endTime"] = endTime
        if pageNo:
            body["pageNo"] = pageNo
        if pageSize:
            body["pageSize"] = pageSize
        if uid:
            body["uid"] = uid

        return await self.client._send_request("POST", request_path, body=body)

    async def get_agent_customer_list(self, startTime=None, endTime=None, pageNo=None, pageSize=None, uid=None, referralCode=None):
        request_path = "/api/broker/v1/agent/customerList"
        body = {}
        if startTime:
            body["startTime"] = startTime
        if endTime:
            body["endTime"] = endTime
        if pageNo:
            body["pageNo"] = pageNo
        if pageSize:
            body["pageSize"] = pageSize
        if uid:
            body["uid"] = uid
        if referralCode:
            body["referralCode"] = referralCode

        return await self.client._send_request("POST", request_path, body=body)

    async def get_agent_customer_kyc_result(self, startTime=None, endTime=None, pageNo=None, pageSize=None, uid=None):
        request_path = "/api/broker/v1/agent/customer-kyc-result"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageNo:
            params["pageNo"] = pageNo
        if pageSize:
            params["pageSize"] = pageSize
        if uid:
            params["uid"] = uid

        return await self.client._send_request("GET", request_path, params=params)

    async def get_agent_customer_deposit_list(self, startTime=None, endTime=None, pageNo=None, pageSize=None, uid=None):
        request_path = "/api/broker/v1/agent/customerDepositList"
        body = {}
        if startTime:
            body["startTime"] = startTime
        if endTime:
            body["endTime"] = endTime
        if pageNo:
            body["pageNo"] = pageNo
        if pageSize:
            body["pageSize"] = pageSize
        if uid:
            body["uid"] = uid

        return await self.client._send_request("POST", request_path, body=body)

    async def get_agent_customer_assets_list(self, pageNo=None, pageSize=None, uid=None):
        request_path = "/api/broker/v1/agent/customerAccountAssetsList"
        body = {}
        if pageNo:
            body["pageNo"] = pageNo
        if pageSize:
            body["pageSize"] = pageSize
        if uid:
            body["uid"] = uid

        return await self.client._send_request("POST", request_path, body=body)

    async def get_agent_commission_detail(self, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/broker/v1/agent/commission-distribution"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)