from .exceptions import BitgetAPIException

class Broker:
    def __init__(self, client):
        self.client = client

    async def create_subaccount(self, subaccountName, label=None):
        request_path = "/api/v2/broker/account/create-subaccount"
        body = {"subaccountName": subaccountName}
        if label:
            body["label"] = label

        return await self.client._send_request("POST", request_path, body=body)

    async def create_subaccount_apikey(self, subUid, passphrase, label, ipList, permType, permList):
        request_path = "/api/v2/broker/manage/create-subaccount-apikey"
        body = {
            "subUid": subUid,
            "passphrase": passphrase,
            "label": label,
            "ipList": ipList,
            "permType": permType,
            "permList": permList
        }
        return await self.client._send_request("POST", request_path, body=body)

    async def create_subaccount_deposit_address(self, subUid, coin, chain=None):
        request_path = "/api/v2/broker/account/subaccount-address"
        body = {"subUid": subUid, "coin": coin}
        if chain:
            body["chain"] = chain
        return await self.client._send_request("POST", request_path, body=body)

    async def delete_subaccount_apikey(self, subUid, apiKey):
        request_path = "/api/v2/broker/manage/delete-subaccount-apikey"
        body = {"subUid": subUid, "apiKey": apiKey}
        return await self.client._send_request("POST", request_path, body=body)

    async def get_broker_info(self):
        request_path = "/api/v2/broker/account/info"
        return await self.client._send_request("GET", request_path, params={})

    async def get_broker_subaccounts(self, startTime=None, endTime=None, pageSize=None, pageNo=None):
        request_path = "/api/broker/v2/subaccounts"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)

    async def get_broker_subaccounts_commissions(self, startTime=None, endTime=None, pageSize=None, pageNo=None, bizType=None, subBizType=None):
        request_path = "/api/broker/v2/commissions"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        if bizType:
            params["bizType"] = bizType
        if subBizType:
            params["subBizType"] = subBizType
        return await self.client._send_request("GET", request_path, params=params)

    async def get_broker_trade_volume(self, startTime=None, endTime=None, pageSize=None, pageNo=None):
        request_path = "/api/broker/v2/trade-volume"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if pageSize:
            params["pageSize"] = pageSize
        if pageNo:
            params["pageNo"] = pageNo
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccounts_deposit_and_withdrawal_records(self, startTime=None, endTime=None, limit=None, idLessThan=None, type=None):
        request_path = "/api/v2/broker/all-sub-deposit-withdrawal"
        params = {}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if type:
            params["type"] = type
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_apikey(self, subUid):
        request_path = "/api/v2/broker/manage/subaccount-apikey-list"
        params = {"subUid": subUid}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_email(self, subUid):
        request_path = "/api/v2/broker/account/subaccount-email"
        params = {"subUid": subUid}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_future_assets(self, subUid, productType):
        request_path = "/api/v2/broker/account/subaccount-future-assets"
        params = {"subUid": subUid, "productType": productType}
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_list(self, limit=None, idLessThan=None, status=None, startTime=None, endTime=None):
        request_path = "/api/v2/broker/account/subaccount-list"
        params = {}
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        if status:
            params["status"] = status
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        return await self.client._send_request("GET", request_path, params=params)

    async def get_subaccount_spot_assets(self, subUid, coin=None, assetType=None):
        request_path = "/api/v2/broker/account/subaccount-spot-assets"
        params = {"subUid": subUid}
        if coin:
            params["coin"] = coin
        if assetType:
            params["assetType"] = assetType
        return await self.client._send_request("GET", request_path, params=params)

    async def modify_subaccount(self, subUid, permList, status, language=None):
        request_path = "/api/v2/broker/account/modify-subaccount"
        body = {"subUid": subUid, "permList": permList, "status": status}
        if language:
            body["language"] = language
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_subaccount_apikey(self, subUid, apiKey, passphrase, label=None, ipList=None, permType=None, permList=None):
        request_path = "/api/v2/broker/manage/modify-subaccount-apikey"
        body = {
            "subUid": subUid,
            "apiKey": apiKey,
            "passphrase": passphrase
        }
        if label:
            body["label"] = label
        if ipList:
            body["ipList"] = ipList
        if permType:
            body["permType"] = permType
        if permList:
            body["permList"] = permList
        return await self.client._send_request("POST", request_path, body=body)

    async def modify_subaccount_email(self, subUid, subaccountEmail):
        request_path = "/api/v2/broker/account/modify-subaccount-email"
        body = {"subUid": subUid, "subaccountEmail": subaccountEmail}
        return await self.client._send_request("POST", request_path, body=body)

    async def sub_deposit_auto_transfer(self, subUid, coin, amount):
        request_path = "/api/v2/broker/account/sub-deposit-auto-transfer"
        body = {"subUid": subUid, "coin": coin, "amount": amount}
        return await self.client._send_request("POST", request_path, body=body)

    async def sub_deposit_records(self, orderId=None, userId=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/broker/subaccount-deposit"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if userId:
            params["userId"] = userId
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def sub_withdrawal_records(self, orderId=None, userId=None, startTime=None, endTime=None, limit=None, idLessThan=None):
        request_path = "/api/v2/broker/subaccount-withdrawal"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if userId:
            params["userId"] = userId
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if idLessThan:
            params["idLessThan"] = idLessThan
        return await self.client._send_request("GET", request_path, params=params)

    async def subaccount_withdrawal(self, subUid, coin, dest, address, amount, chain=None, tag=None, clientOid=None):
        request_path = "/api/v2/broker/account/subaccount-withdrawal"
        body = {
            "subUid": subUid,
            "coin": coin,
            "dest": dest,
            "address": address,
            "amount": amount
        }
        if chain:
            body["chain"] = chain
        if tag:
            body["tag"] = tag
        if clientOid:
            body["clientOid"] = clientOid
        return await self.client._send_request("POST", request_path, body=body)