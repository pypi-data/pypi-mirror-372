from .exceptions import BitgetAPIException
import time

class Uta:
    def __init__(self, client):
        self.client = client

    def get_account_info(self):
        """
        Query account information, including the holding mode, margin mode, leverage multiple, and more.

        Returns:
            dict: Bitget API JSON response containing account information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/settings"
        return self.client._send_request("GET", request_path, params={})

    def get_account_assets(self):
        """
        Query account information and assets, with only non-zero balances being returned.

        Returns:
            dict: Bitget API JSON response containing account assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/assets"
        return self.client._send_request("GET", request_path, params={})

    def get_account_funding_assets(self, coin=None):
        """
        Obtain fund account information and only return the coins with assets.

        Args:
            coin (str, optional): Coin name.

        Returns:
            dict: Bitget API JSON response containing account funding assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/funding-assets"
        params = {}
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_account_fee_rate(self, symbol, category):
        """
        Get Account Fee Rate.

        Args:
            symbol (str): Symbol, e.g., `BTCUSDT`.
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).

        Returns:
            dict: Bitget API JSON response containing account fee rates.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/fee-rate"
        params = {"symbol": symbol, "category": category}
        return self.client._send_request("GET", request_path, params=params)

    def get_convert_records(self, fromCoin, toCoin, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query convert records within the last 90 days.

        Args:
            fromCoin (str): From coin (source coin). It refers to the coin being converted.
            toCoin (str): To coin (target coin). It refers to the coin being converted into (received).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing convert records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get BGB deduction status.

        Returns:
            dict: Bitget API JSON response containing BGB deduction status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/deduct-info"
        return self.client._send_request("GET", request_path, params={})

    def get_financial_records(self, category, coin=None, type=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query financial records within the last 90 days.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`, `OTHER`).
            coin (str, optional): Coin name e.g.,`BTC`.
            type (str, optional): Type (`TRANSFER_IN`/`TRANSFER_OUT`...... All enumeration values can be viewed under the Enumeration category).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing financial records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Subscribe to the account channel. Data will be pushed when the following events occur:
        1. Push on first-time subscription.
        2. Push when spot/margin/futures orders are filled in the unified trading account.
        3. Push when the fund settlement is done.
        4. Push when balance changes (transfers, airdrops, loans, etc.).

        Returns:
            dict: WebSocket message indicating subscription status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query payment coins.

        Returns:
            dict: Bitget API JSON response containing payment coin list and maximum selection.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/payment-coins"
        return self.client._send_request("GET", request_path, params={})

    def get_margin_coin_info(self, productId):
        """
        Get Margin Coin Info.

        Args:
            productId (str): Product Id.

        Returns:
            dict: Bitget API JSON response containing margin coin information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/ensure-coins-convert"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_margin_loan(self, coin):
        """
        Query interest rates for margin loans.

        Args:
            coin (str): Coin name e.g.,`BTC`.

        Returns:
            dict: Bitget API JSON response containing margin loan information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/margin-loans"
        params = {"coin": coin}
        return self.client._send_request("GET", request_path, params=params)

    def get_ltv(self, riskUnitId=None):
        """
        Get LTV.

        Args:
            riskUnitId (str, optional): Risk Unit ID.

        Returns:
            dict: Bitget API JSON response containing LTV information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/ltv-convert"
        params = {}
        if riskUnitId:
            params["riskUnitId"] = riskUnitId
        return self.client._send_request("GET", request_path, params=params)

    def batch_cancel(self, orders):
        """
        This endpoint allows you to cancel a multiple unfilled or partially filled order across spot, margin, and futures
        markets.
        When making a batch order cancellation, ensure that each request uses either orderId or clientOid for identification — never both. If both orderId and clientOid are provided in a single request, the clientOid will be ignored.
        Batch order cancellation allows partial success.

        Args:
            orders (list): A list of dictionaries, where each dictionary represents an order to be cancelled. Each order dictionary must contain:
                category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`). All orders must have the same category.
                symbol (str): Symbol name, e.g.,`BTCUSDT`.
                orderId (str, optional): Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
                clientOid (str, optional): Client order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed order cancellations.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-batch"
        return self.client._send_request("POST", request_path, body=orders)

    def batch_modify_orders(self, orderList):
        """
        Supports batch order modification via API, allowing simultaneous submission of multiple orders across different trading pairs (limited to orders within the same business line).
        Each request supports modification of up to 20 orders.
        Supports continuous order modification, meaning additional modification requests can be submitted before the previous modification request is completed. A maximum of 5 consecutive modification requests for in-progress orders can be submitted, and the matching engine will process the modification requests in sequence.
        Within the same batch of modification requests, each order can only appear once.
        Only fully unfilled orders can have their price and quantity modified.
        Partially filled orders can have their price and quantity modified (the modified quantity cannot be less than the already filled quantity).
        Modification of reduce-only orders is not supported.

        Args:
            orderList (list): A list of dictionaries, where each dictionary represents an order to be modified. Each order dictionary must contain:
                orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
                clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
                qty (str, optional): Order quantity. `Base coin`.
                price (str, optional): Order price.
                autoCancel (str, optional): Will the original order be canceled if the order modification fails (`yes` or `no`). Default: `no`.

        Returns:
            dict: Bitget API JSON response containing lists of modified orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/batch-modify-order"
        return self.client._send_request("POST", request_path, body=orderList)

    def batch_order(self, orderList):
        """
        This endpoint allows the order placement across spot, margin, or futures markets with customizable parameters, including
        price, quantity, and order type, etc.

        * **Upcoming Features** (currently not supported)
          + Isolated spot margin will be available soon.
          + Copy trading order placement will be available soon.
          + Take profit and stop loss will be available soon.

        * **Futures**
          For one-way mode, reduce-only orders are allowed to place. If a reduce only order already exists and the order
          quantity equals the position size, or if a new reduce only order exceeds the remaining position size, the previous
          reduction order will be automatically canceled and replaced. In this case, the returned orderId will be null.
          **It is recommended to always provide a `clientOid`. (currently,`reduce-only` orders are not supported)**

        * **Margin**
          Margin orders will automatically trigger fund borrowing.

        * **Order Check**

          + **Futures**:`price` must meet the price multiplier and be a multiple of `priceMultiplier`, and conform to the
            `pricePrecision` decimal places. `qty` must be greater than or equal to `minOrderAmount` and be a multiple of
            `sizeMultiplier`.
          + **Spot**:`price` must meet the decimal place requirement. `qty` must be greater than or equal to `minOrderAmount`.

        * **Open Position Logic**

          + **Hedge-mode**
            Open long: `side=buy` & `posSide=long`
            Open Short: `side=sell` & `posSide=short`
            Close long: `side=sell` & `posSide=long`
            Close short: `side=buy` & `posSide=short`
          + **One-way-mode**
            Open long: `side=buy`
            Open short: `side=sell`
            Close long: `side=sell` & `reduceOnly=yes`
            Close short: `side=buy` & `reduceOnly=yes`

        * **Order Limit**
          + **Futures**: 400 orders across all USDT, Coin-M, and USDC futures trading pairs.
          + **Spot**: 400 orders across all spot and margin trading pairs.

        * **ClientOid Constraints**
          Please ensure your clientOid matches the regular expression `^[\.A-Z\:/a-z0-9_-]{1,32}from .exceptions import BitgetAPIException
import time

class Uta:
    def __init__(self, client):
        self.client = client

    def get_account_info(self):
        """
        Query account information, including the holding mode, margin mode, leverage multiple, and more.

        Returns:
            dict: Bitget API JSON response containing account information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/settings"
        return self.client._send_request("GET", request_path, params={})

    def get_account_assets(self):
        """
        Query account information and assets, with only non-zero balances being returned.

        Returns:
            dict: Bitget API JSON response containing account assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/assets"
        return self.client._send_request("GET", request_path, params={})

    def get_account_funding_assets(self, coin=None):
        """
        Obtain fund account information and only return the coins with assets.

        Args:
            coin (str, optional): Coin name.

        Returns:
            dict: Bitget API JSON response containing account funding assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/funding-assets"
        params = {}
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_account_fee_rate(self, symbol, category):
        """
        Get Account Fee Rate.

        Args:
            symbol (str): Symbol, e.g., `BTCUSDT`.
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).

        Returns:
            dict: Bitget API JSON response containing account fee rates.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/fee-rate"
        params = {"symbol": symbol, "category": category}
        return self.client._send_request("GET", request_path, params=params)

    def get_convert_records(self, fromCoin, toCoin, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query convert records within the last 90 days.

        Args:
            fromCoin (str): From coin (source coin). It refers to the coin being converted.
            toCoin (str): To coin (target coin). It refers to the coin being converted into (received).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing convert records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get BGB deduction status.

        Returns:
            dict: Bitget API JSON response containing BGB deduction status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/deduct-info"
        return self.client._send_request("GET", request_path, params={})

    def get_financial_records(self, category, coin=None, type=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query financial records within the last 90 days.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`, `OTHER`).
            coin (str, optional): Coin name e.g.,`BTC`.
            type (str, optional): Type (`TRANSFER_IN`/`TRANSFER_OUT`...... All enumeration values can be viewed under the Enumeration category).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing financial records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Subscribe to the account channel. Data will be pushed when the following events occur:
        1. Push on first-time subscription.
        2. Push when spot/margin/futures orders are filled in the unified trading account.
        3. Push when the fund settlement is done.
        4. Push when balance changes (transfers, airdrops, loans, etc.).

        Returns:
            dict: WebSocket message indicating subscription status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query payment coins.

        Returns:
            dict: Bitget API JSON response containing payment coin list and maximum selection.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/payment-coins"
        return self.client._send_request("GET", request_path, params={})

    def get_margin_coin_info(self, productId):
        """
        Get Margin Coin Info.

        Args:
            productId (str): Product Id.

        Returns:
            dict: Bitget API JSON response containing margin coin information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/ensure-coins-convert"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_margin_loan(self, coin):
        """
        Query interest rates for margin loans.

        Args:
            coin (str): Coin name e.g.,`BTC`.

        Returns:
            dict: Bitget API JSON response containing margin loan information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/margin-loans"
        params = {"coin": coin}
        return self.client._send_request("GET", request_path, params=params)

    def get_ltv(self, riskUnitId=None):
        """
        Get LTV.

        Args:
            riskUnitId (str, optional): Risk Unit ID.

        Returns:
            dict: Bitget API JSON response containing LTV information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/ltv-convert"
        params = {}
        if riskUnitId:
            params["riskUnitId"] = riskUnitId
        return self.client._send_request("GET", request_path, params=params)

    def batch_cancel(self, orders):
        """
        This endpoint allows you to cancel a multiple unfilled or partially filled order across spot, margin, and futures
        markets.
        When making a batch order cancellation, ensure that each request uses either orderId or clientOid for identification — never both. If both orderId and clientOid are provided in a single request, the clientOid will be ignored.
        Batch order cancellation allows partial success.

        Args:
            orders (list): A list of dictionaries, where each dictionary represents an order to be cancelled. Each order dictionary must contain:
                category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`). All orders must have the same category.
                symbol (str): Symbol name, e.g.,`BTCUSDT`.
                orderId (str, optional): Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
                clientOid (str, optional): Client order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed order cancellations.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-batch"
        return self.client._send_request("POST", request_path, body=orders)

    def batch_modify_orders(self, orderList):
        """
        Supports batch order modification via API, allowing simultaneous submission of multiple orders across different trading pairs (limited to orders within the same business line).
        Each request supports modification of up to 20 orders.
        Supports continuous order modification, meaning additional modification requests can be submitted before the previous modification request is completed. A maximum of 5 consecutive modification requests for in-progress orders can be submitted, and the matching engine will process the modification requests in sequence.
        Within the same batch of modification requests, each order can only appear once.
        Only fully unfilled orders can have their price and quantity modified.
        Partially filled orders can have their price and quantity modified (the modified quantity cannot be less than the already filled quantity).
        Modification of reduce-only orders is not supported.

        Args:
            orderList (list): A list of dictionaries, where each dictionary represents an order to be modified. Each order dictionary must contain:
                orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
                clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
                qty (str, optional): Order quantity. `Base coin`.
                price (str, optional): Order price.
                autoCancel (str, optional): Will the original order be canceled if the order modification fails (`yes` or `no`). Default: `no`.

        Returns:
            dict: Bitget API JSON response containing lists of modified orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/batch-modify-order"
        return self.client._send_request("POST", request_path, body=orderList)

    , consisting of 1 to 32
          characters, including periods (.), uppercase letters, colons (:), lowercase letters, numbers, underscores (\_), and
          hyphens (-).

        * **Request Monitor**
          The API requests will be monitored. If the total number of orders for a single account (including master and
          sub-accounts) exceeds a set daily limit (UTC 00:00 - UTC 24:00), the platform reserves the right to issue reminders,
          warnings, and enforce necessary restrictions. By using the API, clients acknowledge and agree to comply with these
          terms.

        * **Error Sample**
          > { "code":"40762", "msg":"The order size is greater than the max open size", "requestTime":1627293504612 }
          >
          > This error code may occur in the following scenarios.
          >
          > + Insufficient account balance.
          > + The position tier for this symbol has reached its limit. For details on specific tiers, please
          >   refer [here](https://www.bitget.com/futures/introduction/position-tier?code=BTCUSDT_UMCBL?business=USDT_MIX_CONTRACT_BL) .

        Note: If the following errors occur when placing an order, please use `clientOid` to query the order details to confirm
        the final result of the operation.

        > { "code": "40010", "msg": "Request timed out", "requestTime": 1666268894074, "data": null }
        > { "code": "40725", "msg": "service return an error", "requestTime": 1666268894071, "data": null }
        > { "code": "45001", "msg": "Unknown error", "requestTime": 1666268894071, "data": null }

        Args:
            orderList (list): Collection of placing orders, maximum length: 50. Each item in the list should be a dictionary with the following keys:
                category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`). All orders must have the same category.
                symbol (str): Symbol name, e.g.,`BTCUSDT`.
                qty (str): Order quantity. For market buy orders, the unit is **quote coin**. For limit and market sell orders, the unit is **base coin**.
                side (str): Order side (`buy`/`sell`).
                orderType (str): Order type (`limit`/`market`).
                price (str, optional): Order price. This field is required when `orderType` is `limit`.
                timeInForce (str, optional): Time in force (`ioc`, `fok`, `gtc`, `post_only`). This field is required when `orderType` is `limit`. If omitted, it defaults to `gtc`.
                posSide (str, optional): Position side (`long`/`short`). This field is required in hedge-mode position. Available only for futures.
                clientOid (str, optional): Client order ID. The idempotent validity period is six hours (not fully guaranteed).

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/place-batch"
        return self.client._send_request("POST", request_path, body=orderList)

    def bind_unbind_uid_to_risk_unit(self, uid, operate, riskUnitId=None):
        """
        Bind/Unbind UID to Risk Unit.
        Binding:
        * The uid and riskUnitId belong to the same main account.
        * The uid is not bound to any other risk unit.
        Unbinding:
        * The API key used for the call must belong to the main account or the lending-exclusive sub-account UID within the risk
          unit.
        * The uid is within the risk unit and is not equal to riskUnitId.
        * The uid has a zero balance, or the riskUnitId has not_paid_off or in_progress loan orders.

        Args:
            uid (str): Sub UID (limit 50 UIDS for one Risk Unit).
            operate (str): `bind` Bind or `unbind` Unbind.
            riskUnitId (str, optional): Risk Unit ID (Required for parent account calls, not required for risk unit account calls).

        Returns:
            dict: Bitget API JSON response containing risk unit ID, UID, and operation.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/bind-uid"
        body = {
            "uid": uid,
            "operate": operate
        }
        if riskUnitId:
            body["riskUnitId"] = riskUnitId
        return self.client._send_request("POST", request_path, body=body)

    def batch_place_order_channel(self, category, orders):
        """
        Batch Place Order Channel.
        * Maximum 20 orders allowed in a single request.
        * Please contact your BD or RM to apply for access permissions.

        Args:
            category (str): Category (`spot`, `margin`, `usdt-futures`, `coin-futures`, `usdc-futures`).
            orders (list): List of order objects. Each order object should be a dictionary with the following keys:
                symbol (str): Symbol name.
                orderType (str): Order type (`limit` or `market`).
                qty (str): Order quantity. For market buy orders, the unit is quote coin. For limit and market sell orders, the unit is base coin. For futures, the unit is base coin.
                price (str, optional): Order price. This field is required when `orderType` is `limit`.
                side (str): Order side (`buy` or `sell`).
                posSide (str, optional): Position side (`long` or `short`). This field is required in hedge-mode positions. Available only for futures.
                timeInForce (str, optional): Time in force (`gtc`, `ioc`, `fok`, `post_only`). This field is required when `orderType` is `limit`. If omitted, it defaults to `gtc`.
                clientOid (str, optional): Client order ID.
                stpMode (str, optional): STP Mode (`none`, `cancel_taker`, `cancel_maker`, `cancel_both`).
                tpTriggerBy (str, optional): Preset Take-Profit Trigger Type (`market` or `mark`). If not specified, the default value is market price. Note: This field is only valid for the contract business lines: USDT-Futures, COIN-Futures, and USDC-Futures.
                slTriggerBy (str, optional): Preset Stop-Loss Trigger Type (`market` or `mark`). If not specified, the default value is market price. Note: This field is only valid for the contract business lines: USDT-Futures, COIN-Futures, and USDC-Futures.
                takeprofit (str, optional): Preset Take-Profit Trigger Price.
                stoploss (str, optional): Preset Stop-Loss Trigger Price.
                tpOrderType (str, optional): Take-Profit Trigger Strategy Order Type (`limit` or `market`).
                slOrderType (str, optional): Stop-Loss Trigger Strategy Order Type (`limit` or `market`).
                tpLimitPrice (str, optional): Take-Profit Strategy Order Execution Price. This field is only valid for limit orders (when `tpOrderType=limit`); it is ignored for market orders.
                slLimitPrice (str, optional): Stop-Loss Strategy Order Execution Price. This field is only valid for limit orders (when `slOrderType=limit`); it is ignored for market orders.

        Returns:
            dict: WebSocket message indicating the result of the batch place order operation.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        message = {
            "op": "trade",
            "id": str(int(time.time() * 1000)), # Generate a unique ID
            "category": category,
            "topic": "batch-place",
            "args": orders
        }
        return self.client._send_websocket_request(message)

    def cancel_all_orders(self, category, symbol=None):
        """
        Cancel unfilled or partially filled orders by symbol or category.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`. If no symbol is provided, all positions in the corresponding category will be closed.

        Returns:
            dict: Bitget API JSON response containing lists of cancelled orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-symbol-order"
        body = {"category": category}
        if symbol:
            body["symbol"] = symbol
        return self.client._send_request("POST", request_path, body=body)

    def cancel_order(self, orderId=None, clientOid=None):
        """
        This endpoint allows you to cancel a single unfilled or partially filled order across spot, margin, and futures markets.

        Args:
            orderId (str, optional): Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
            clientOid (str, optional): Client order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.

        Returns:
            dict: Bitget API JSON response containing the order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return self.client._send_request("POST", request_path, body=body)

    def cancel_strategy_order(self, orderId=None, clientOid=None):
        """
        Cancel strategy order.

        Args:
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-strategy-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return self.client._send_request("POST", request_path, body=body)

    def close_all_positions(self, category, symbol=None, posSide=None):
        """
        Close positions by position side or category. All positions will be closed at market price, subject to slippage.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`. If no symbol is provided, all positions in the corresponding category will be closed.
            posSide (str, optional): Position side (`long` or `short`). If this field is provided, only the position in the corresponding side will be closed.

        Returns:
            dict: Bitget API JSON response containing lists of closed positions.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/close-positions"
        body = {"category": category}
        if symbol:
            body["symbol"] = symbol
        if posSide:
            body["posSide"] = posSide
        return self.client._send_request("POST", request_path, body=body)

    def countdown_cancel_all(self, countdown):
        """
        In practical use, clients need to periodically send heartbeat requests to prevent uncontrolled open orders due to
        abnormal disconnections or system crashes.
        For example, if your expected heartbeat interval is 10 seconds, meaning if no heartbeat request is sent for over 10
        seconds, all orders must be canceled:

        * Under normal circumstances, you can call this interface every 3-5 seconds, set the countdown to 10, and repeatedly
          call it to reset the countdown.
        * Under abnormal circumstances, if no heartbeat request is sent for over 10 seconds, all orders under the account will
          be automatically canceled; after automatic cancellation, the Deadman Switch mechanism will automatically close.
        * To manually close the Deadman Switch mechanism, simply set the countdown to 0.
          P.S. This interface only supports canceling orders under UTA accounts, not classic accounts.

        Please contact your dedicated Business Development representative to apply for access to this interface.

        Args:
            countdown (str): Reconnect Window. Unit: seconds. Positive integer, range: [5, 60]. The minimum countdown is 5 second, and the maximum is 60 seconds. Filling in 0 cancels the countdown order cancellation function.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/countdown-cancel-all"
        body = {"countdown": countdown}
        return self.client._send_request("POST", request_path, body=body)

    def create_sub_account_api_key(self, subUid, note, type, passphrase, permissions, ips):
        """
        This API is used to create an API Key for a sub-account under a unified account. It is applicable when the main
        account is in a mix or unified account mode. If the current main account is in the classic account mode, this API
        cannot be called.

        Args:
            subUid (str): Sub-account ID.
            note (str): Note Name. The note needs to start with a letter and supports [0-9], [a-z], [A-Z], as well as [-,_].
            type (str): Permission Type (`read_write` or `read_only`).
            passphrase (str): Passphrase. A combination of 8 to 32 characters of letters and numbers.
            permissions (list): Permission values. Unified Account Permissions: `uta_mgt` Unified Account Management, `uta_trade` Unified Account Trading.
            ips (list): Withdrawal Whitelist IP. Multiple IP addresses are supported. A maximum of 30 IPs can be bound to a single key. **Only supports IPv4**.

        Returns:
            dict: Bitget API JSON response containing sub-account API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        This API is used for the main account to create a sub-account. It only supports creating unified account virtual sub-accounts and does not support creating regular sub-accounts.

        Args:
            username (str): Generate a virtual email address username. It can only contain lowercase letters and cannot exceed 20 characters.
            accountMode (str, optional): Sub-account Mode (`classic` Classic Account Sub-account or `unified` Unified Account Sub-account).
            note (str, optional): Note, cannot exceed 50 characters.

        Returns:
            dict: Bitget API JSON response containing sub-account details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/create-sub"
        body = {"username": username}
        if accountMode:
            body["accountMode"] = accountMode
        if note:
            body["note"] = note
        return self.client._send_request("POST", request_path, body=body)

    def freeze_unfreeze_sub_account(self, subUid, operation):
        """
        Freeze/Unfreeze Sub-account.

        Args:
            subUid (str): Sub-account ID to be frozen/unfrozen.
            operation (str): Operation Type (`freeze` or `unfreeze`).

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/freeze-sub"
        body = {
            "subUid": subUid,
            "operation": operation
        }
        return self.client._send_request("POST", request_path, body=body)

    def delete_sub_account_api_key(self, apiKey):
        """
        This API is used for the main account to delete a sub-account's API Key. It is not applicable for the main account or
        sub-account to delete their own API Key.

        Please note that once the deletion is completed, the sub-account API Key will be immediately invalid. Before performing
        the deletion, ensure that this operation will not cause any loss.

        This API only supports deleting API Keys of sub-accounts under a unified account, and does not support deleting API Keys
        of sub-accounts under a classic account.

        Args:
            apiKey (str): The sub-account API Key.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/delete-sub-api"
        body = {"apiKey": apiKey}
        return self.client._send_request("POST", request_path, body=body)

    def get_current_funding_rate(self, symbol):
        """
        Get current funding rate.

        Args:
            symbol (str): Trading pair, based on the symbolName, i.e. BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing current funding rate information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/current-fund-rate"
        params = {"symbol": symbol}
        return self.client._send_request("GET", request_path, params=params)

    def get_deposit_address(self, coin, chain=None, size=None):
        """
        Get deposit address.

        Args:
            coin (str): Coin name. The currency name can be obtained using the Get Currency Information API.
            chain (str, optional): Chain Name. The chain name can be obtained using the Get Currency Information API. If not filled, the system will automatically match a chain to generate a deposit address.
            size (str, optional): Deposit Quantity. Only applies to BTC Lightning Network. Limit range: 0.000001 - 0.01.

        Returns:
            dict: Bitget API JSON response containing deposit address information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/deposit-address"
        params = {"coin": coin}
        if chain:
            params["chain"] = chain
        if size:
            params["size"] = size
        return self.client._send_request("GET", request_path, params=params)

    def get_deposit_records(self, startTime, endTime, coin=None, orderId=None, limit=None, cursor=None):
        """
        Get deposit records.

        Args:
            startTime (str): Query record start time. Unix millisecond timestamp, e.g., 1690196141868.
            endTime (str): Query record end time. Unix millisecond timestamp, e.g., 1690196141868.
            coin (str, optional): Coin name. If left blank, all currency deposit records will be retrieved.
            orderId (str, optional): Order ID. Used for specifying order queries.
            limit (str, optional): Items per page. The default value is 20, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination to reduce query response time. Do not send for the initial query. When querying the second page and subsequent data, use the smallest orderId returned from the previous query. The results will return data less than that value.

        Returns:
            dict: Bitget API JSON response containing deposit records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query historical fills within the last 90 days.

        * **Query Range Constraint**
           Each individual query can only cover a maximum of 30 days within the 90-day window.

        Args:
            startTime (str): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            category (str, optional): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            orderId (str, optional): Order ID.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing fill history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query historical funding rate records. The Funding interval varies by symbol and can be retrieved via the Instruments endpoint.

        Args:
            category (str): Product Type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            cursor (str, optional): Page number. Default: `1`. Maximum: `100`.
            limit (str, optional): Limit per page. Default: `200`. Maximum: `200`.

        Returns:
            dict: Bitget API JSON response containing funding rate history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/history-fund-rate"
        params = {"category": category, "symbol": symbol}
        if cursor:
            params["cursor"] = cursor
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_instruments(self, category, symbol=None):
        """
        Query the specifications for online trading pair instruments.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.

        Returns:
            dict: Bitget API JSON response containing instrument information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/instruments"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_historical_candlestick_uta(self, category, symbol, interval, startTime=None, endTime=None, type=None, limit=None):
        """
        Query historical Kline/candlestick data within the last 90 days.

        Args:
            category (str): Product Type (`SPOT`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            interval (str): Granularity (`1m`,`3m`,`5m`,`15m`,`30m`,`1H`,`4H`,`6H`,`12H`,`1D`).
            startTime (str, optional): Start timestamp. A Unix millisecond timestamp, e.g.,`1672410780000`. Request data after this start time (the maximum time query range is 90 days).
            endTime (str, optional): End timestamp. A Unix millisecond timestamp, e.g.,`1672410781000`. Request data before this end time (the maximum time query range is 90 days).
            type (str, optional): Candlestick type (`MARKET`, `MARK`, `INDEX`). Default `MARKET`.
            limit (str, optional): Limit per page. Default:`100`. Maximum: `100`.

        Returns:
            dict: Bitget API JSON response containing historical candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query kline/candlestick data. This endpoint allows retrieving up to 1,000 candlesticks.

        Args:
            category (str): Product Type (`SPOT`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            interval (str): Granularity (`1m`,`3m`,`5m`,`15m`,`30m`,`1H`,`4H`,`6H`,`12H`,`1D`).
            startTime (str, optional): Start timestamp. A Unix millisecond timestamp, e.g.,`1672410780000`.
            endTime (str, optional): End timestamp. A Unix millisecond timestamp, e.g.,`1672410781000`.
            type (str, optional): Candlestick type (`market`, `mark`, `index`). Default: `market`.
            limit (str, optional): Limit per page. Default:`100`. Maximum: `100`.

        Returns:
            dict: Bitget API JSON response containing kline/candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get Loan Orders.

        Args:
            orderId (str, optional): Loan order id. If not passed, then return all orders, sort by `loanTime` in descend.
            startTime (str, optional): The start timestamp (ms).
            endTime (str, optional): The end timestamp (ms).

        Returns:
            dict: Bitget API JSON response containing loan orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get max open available.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            orderType (str): Order type (`limit`/`market`).
            side (str): Transaction direction (`buy`/`sell`).
            price (str, optional): Order price. This field is required when `orderType` is `limit`.
            size (str, optional): Order quantity, base coin.

        Returns:
            dict: Bitget API JSON response containing max open available information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Interface is used to get future contract OI Limit.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Trading pair, based on the symbolName, i.e. BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing open interest limit information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/oi-limit"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_open_interest(self, category, symbol=None):
        """
        Query the total number of unsettled or open futures.

        Args:
            category (str): Product Type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.

        Returns:
            dict: Bitget API JSON response containing open interest information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/open-interest"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_open_orders(self, category=None, symbol=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query unfilled or partially filled orders. To query closed orders, please use the order history endpoint.

        Args:
            category (str, optional): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing open orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query order details using either orderId or clientOid.

        Args:
            orderId (str, optional): Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
            clientOid (str, optional): Client order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/order-info"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        return self.client._send_request("GET", request_path, params=params)

    def get_order_history(self, category, symbol=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query historical orders within the last 90 days.

        * **Query Range Constraint**
           Each individual query can only cover a maximum of 30 days within the 90-day window.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing order history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query order book depth data.

        Args:
            category (str): Product Type (`SPOT`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            limit (str, optional): Limit per page. Default: `5`. Maximum: `200`.

        Returns:
            dict: Bitget API JSON response containing order book depth.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/orderbook"
        params = {
            "category": category,
            "symbol": symbol
        }
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_position_adl_rank(self):
        """
        Get Position ADL Rank.

        Returns:
            dict: Bitget API JSON response containing position ADL rank information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/position/adlRank"
        return self.client._send_request("GET", request_path, params={})

    def get_position_info(self, category, symbol=None, posSide=None):
        """
        Query real-time position data by symbol, side, or category.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name e.g.`BTCUSDT`. If no symbol is provided, all positions in the corresponding category will be returned.
            posSide (str, optional): Position side (`long`/`short`). If this field is provided, only the position in the corresponding side will be returned.

        Returns:
            dict: Bitget API JSON response containing position information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/position/current-position"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if posSide:
            params["posSide"] = posSide
        return self.client._send_request("GET", request_path, params=params)

    def get_position_tier(self, category, symbol=None, coin=None):
        """
        Query the position tier info.

        Args:
            category (str): Product type (`MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`, applies to `Futures`.
            coin (str, optional): Coin name, e.g.,`BTC`, applies to `Margin`.

        Returns:
            dict: Bitget API JSON response containing position tier information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/position-tier"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_positions_history(self, category, symbol=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query historical positions within the last 90 days.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name e.g.,`BTCUSDT`.
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing positions history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get Proof Of Reserves.

        Returns:
            dict: Bitget API JSON response containing proof of reserves information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/proof-of-reserves"
        return self.client._send_request("GET", request_path, params={})

    def get_repayment_orders(self, startTime=None, endTime=None, limit=None):
        """
        Get Repayment Orders.
        * By default, query the data of the past two years.
        * At most, support querying the data of the past two years.
        * Only display the data of successfully repaid orders.
        * Only display the repayment orders under the unified account. The orders under the spot account can be queried through
          the v2 version.

        Args:
            startTime (str, optional): The start timestamp (ms).
            endTime (str, optional): The end timestamp (ms).
            limit (str, optional): Limit default 100; max 100.

        Returns:
            dict: Bitget API JSON response containing repayment orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query risk reserve records.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.

        Returns:
            dict: Bitget API JSON response containing risk reserve information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/risk-reserve"
        params = {
            "category": category,
            "symbol": symbol
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_risk_unit(self):
        """
        Get Risk Unit. Only the parent account API Key can use this endpoint.

        Returns:
            dict: Bitget API JSON response containing all Risk Unit IDs.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/risk-unit"
        return self.client._send_request("GET", request_path, params={})

    def get_sub_account_api_keys(self, subUid, limit=None, cursor=None):
        """
        Supports querying the full API Key list under a single sub-account.

        Args:
            subUid (str): Sub-account UID.
            limit (str, optional): Items per page. The default value is 100, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination. Do not pass it for the first query. For subsequent queries (second page and beyond), use the cursor returned from the previous query.

        Returns:
            dict: Bitget API JSON response containing sub-account API keys.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/sub-api-list"
        params = {"subUid": subUid}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_sub_account_list(self, limit=None, cursor=None):
        """
        Query Sub-account List.

        Args:
            limit (str, optional): Items per page. The default value is 100, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination. Do not pass it for the first query. For subsequent queries (second page and beyond), use the cursor returned from the previous query.

        Returns:
            dict: Bitget API JSON response containing sub-account list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/sub-list"
        params = {}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_subaccount_unified_assets(self, subUid=None, cursor=None, limit=None):
        """
        Get SubAccount Unified Assets.

        Args:
            subUid (str, optional): Sub-account UID. Leave blank to return all sub-account asset lists.
            cursor (str, optional): Cursor ID. For pagination. Omit in first request. Pass previous cursor in subsequent requests.
            limit (str, optional): Sub-accounts per Page. Default value is 10, maximum is 50.

        Returns:
            dict: Bitget API JSON response containing sub-account unified assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get Switch Status. Only supports parent accounts.

        Returns:
            dict: Bitget API JSON response containing switch status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/switch-status"
        return self.client._send_request("GET", request_path, params={})

    def get_main_sub_transfer_records(self, subUid=None, role=None, coin=None, startTime=None, endTime=None, clientOid=None, limit=None, cursor=None):
        """
        This API supports retrieving transfer records between main and sub accounts.

        Args:
            subUid (str, optional): Sub-account UID. If not provided, transfer records of the main account will be retrieved.
            role (str, optional): Transfer-out account type (`initiator` or `receiver`). Default: `initiator`.
            coin (str, optional): Coin name.
            startTime (str, optional): Start time for querying transfer records. Unix millisecond timestamp, e.g., 1690196141868. The time interval between startTime and endTime should not exceed 90 days.
            endTime (str, optional): End time for querying transfer records. Unix millisecond timestamp, e.g., 1690196141868. The time interval between startTime and endTime should not exceed 90 days.
            clientOid (str, optional): clientOid, Cannot exceed 64 characters.
            limit (str, optional): Items per page. The default value is 100, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination. Do not pass it for the first query. For subsequent queries (second page and beyond), use the cursor returned from the previous query.

        Returns:
            dict: Bitget API JSON response containing main/sub transfer records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query real-time market data, including the latest price, 24-hour high/low, volume, bid, ask, and price change for available trading pairs.

        Args:
            category (str): Product type (`SPOT`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.

        Returns:
            dict: Bitget API JSON response containing ticker information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/tickers"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_trade_symbols(self, productId):
        """
        Get Trade Symbols.

        Args:
            productId (str): Product Id.

        Returns:
            dict: Bitget API JSON response containing trade symbols information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/symbols"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_transferable_coins(self, fromType, toType):
        """
        Query transferable coins **between Classic and UTA accounts**.
        *Classic accounts include Spot, Isolated Margin, Cross Margin, USDT Futures, USDC Futures, Coin-M Futures, and P2P accounts*

        Args:
            fromType (str): From (source) account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`, `uta`).
            toType (str): To (target) account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`, `uta`).

        Returns:
            dict: Bitget API JSON response containing a list of transferable coins.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/transferable-coins"
        params = {
            "fromType": fromType,
            "toType": toType
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_transferred_quantity(self, coin, userId=None):
        """
        Get Transferred Quantity.

        Args:
            coin (str): Coin.
            userId (str, optional): User Id (Master account or sub-accounts).

        Returns:
            dict: Bitget API JSON response containing transferred quantity information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/transfered"
        params = {"coin": coin}
        if userId:
            params["userId"] = userId
        return self.client._send_request("GET", request_path, params=params)

    def get_withdrawal_records(self, startTime, endTime, coin=None, orderId=None, clientOid=None, limit=None, cursor=None):
        """
        Get withdrawal records.

        Args:
            startTime (str): Query record start time. Unix millisecond timestamp, e.g., 1690196141868.
            endTime (str): Query record end time. Unix millisecond timestamp, e.g., 1690196141868.
            coin (str, optional): Coin name. If not filled in, all coin deposit records will be retrieved.
            orderId (str, optional): order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
            clientOid (str, optional): Client Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
            limit (str, optional): Items per page. The default value is 20, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination to reduce query response time. Do not send for the initial query. When querying the second page and subsequent data, use the smallest orderId returned from the previous query. The results will return data less than that value.

        Returns:
            dict: Bitget API JSON response containing withdrawal records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Sub-account to Main Account Asset Transfer. The transfer types supported by this API include:

        * Main account to sub-account (only the main account API Key has permission)
        * Sub-account to main account (only the main account API Key has permission)
        * Sub-account to sub-account (only the main account API Key has permission, and the sending and receiving sub-accounts must belong to the same main account)
        * Sub-account internal transfer (only the main account API Key has permission, and the sending and receiving sub-accounts must be the same sub-account)

        The UID of the transferring and receiving accounts in the request parameters must be in a main-sub or sibling
        relationship, and the caller must be the main account API Key.

        Args:
            fromType (str): Transferring Account Type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `uta`). The above enumerations apply to the main account. If it is a sub-account: Unified account sub-account only supports `uta` and `spot`. Classic account sub-account does not support `uta` and `p2p`.
            toType (str): Receiving Account Type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `uta`). The above enumerations apply to the main account. If it is a sub-account: Unified account sub-account only supports `uta` and `spot`. Classic account sub-account does not support `uta` and `p2p`.
            amount (str): Amount to Transfer In.
            coin (str): Transfer Currency, e.g., BTC.
            fromUserId (str): Transferring Account UID.
            toUserId (str): Receiving Account UID.
            clientOid (str): clientOid, Cannot exceed 64 characters.

        Returns:
            dict: Bitget API JSON response containing transfer ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Support for fund transfers in and out between unified accounts and classic accounts.

        Args:
            fromType (str): From (source) account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`, `uta`).
            toType (str): To (target) account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`, `uta`).
            amount (str): Transfer amount.
            coin (str): Transfer coin e.g: BTC.
            symbol (str, optional): Isolated spot margin e.g: BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing transfer ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Support modifying orders using either the order ID (orderId) or a custom order ID (clientOid).

        * Only orders that have not been fully filled can be modified. If an order has been completely filled, it cannot be modified through this interface.
        * After submitting a modification request and before receiving the result, repeated modification requests cannot be submitted.

        Args:
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            qty (str, optional): Order quantity. `Base coin`. Either `qty` or `price` must be provided.
            price (str, optional): Order price. Either `qty` or `price` must be provided.
            autoCancel (str, optional): Will the original order be canceled if the order modification fails (`yes` or `no`). Default: `no`.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get historical strategy orders.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            type (str, optional): Strategy Type (`tpsl` Take-Profit and Stop-Loss).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`.
            limit (str, optional): Limit per page Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing historical strategy orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Modify strategy order.

        Args:
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            qty (str, optional): Order Quantity. Can be modified under partial take-profit/stop-loss mode, and the unit is in the `base coin`.
            tpTriggerBy (str, optional): Take-Profit Trigger Type (`market` or `mark`).
            slTriggerBy (str, optional): Stop-Loss Trigger Type (`market` or `mark`).
            takeProfit (str, optional): Take-Profit Trigger Price.
            stopLoss (str, optional): Stop-Loss Trigger Price.
            tpOrderType (str, optional): Take-Profit Trigger Strategy Order Type (`limit` or `market`).
            slOrderType (str, optional): Stop-Loss Trigger Strategy Order Type (`limit` or `market`).
            tpLimitPrice (str, optional): Take-Profit Strategy Order Execution Price. This field is only valid for limit orders (when `tpOrderType=limit`); it is ignored for market orders.
            slLimitPrice (str, optional): Stop-Loss Strategy Order Execution Price. This field is only valid for limit orders (when `slOrderType=limit`); it is ignored for market orders.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        This API is used to modify the unified account sub-account API Key permissions and withdrawal whitelist IP addresses. It only supports modifying the API Key of a unified account sub-account and does not support creating an API Key for a classic account sub-account.

        Args:
            apiKey (str): Sub-account API Key.
            passphrase (str): Passphrase. A combination of 8 to 32 characters of letters and numbers.
            type (str, optional): Permission Type (`read_write` or `read_only`). **This parameter is required when `permissions` has a value.**
            permissions (list, optional): Permission values. Unified Account Permissions: `uta_mgt` Unified Account Management, `uta_trade` Unified Account Trading. **This parameter is required when `type` has a value.**
            ips (list, optional): Withdrawal Whitelist IP. If not provided, the IP address will not be modified. If an empty value is provided, the withdrawal whitelist will be deleted. Multiple IP addresses are supported. A maximum of 30 IPs can be bound to a single key. **Only supports IPv4**.

        Returns:
            dict: Bitget API JSON response containing modified sub-account API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        This endpoint allows the order placement across spot, margin, or futures markets with customizable parameters, including
        price, quantity, and order type, etc.

        * **Upcoming Features** (currently not supported)
          + Isolated spot margin will be available soon.
          + Copy trading order placement will be available soon.

        * **Futures**
          For one-way mode, reduce-only orders are allowed to place. If a reduce only order already exists and the order
          quantity equals the position size, or if a new reduce only order exceeds the remaining position size, the previous
          reduction order will be automatically canceled and replaced. In this case, the returned orderId will be null.
          **It is recommended to always provide a `clientOid`.**

        * **Margin**
          Margin orders will automatically trigger fund borrowing.

        * **Order Check**

          + **Futures**:`price` must meet the price multiplier and be a multiple of `priceMultiplier`, and conform to the `pricePrecision` decimal places. `qty` must be greater than or equal to `minOrderAmount` and be a multiple of `sizeMultiplier`.
          + **Spot**:`price` must meet the decimal place requirement. `qty` must be greater than or equal to `minOrderAmount`.

        * **Open Position Logic**

          + **Hedge-mode**
            Open long: `side=buy` & `posSide=long`
            Open Short: `side=sell` & `posSide=short`
            Close long: `side=sell` & `posSide=long`
            Close short: `side=buy` & `posSide=short`
          + **One-way-mode**
            Open long: `side=buy`
            Open short: `side=sell`
            Close long: `side=sell` & `reduceOnly=yes`
            Close short: `side=buy` & `reduceOnly=yes`

        * **Order Limit**
          + **Futures**: 400 orders across all USDT, Coin-M, and USDC futures trading pairs.
          + **Spot**: 400 orders across all spot and margin trading pairs.

        * **ClientOid Constraints**
          Please ensure your clientOid matches the regular expression `^[\.A-Z\:/a-z0-9_-]{1,32}from .exceptions import BitgetAPIException
import time

class Uta:
    def __init__(self, client):
        self.client = client

    def get_account_info(self):
        """
        Query account information, including the holding mode, margin mode, leverage multiple, and more.

        Returns:
            dict: Bitget API JSON response containing account information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/settings"
        return self.client._send_request("GET", request_path, params={})

    def get_account_assets(self):
        """
        Query account information and assets, with only non-zero balances being returned.

        Returns:
            dict: Bitget API JSON response containing account assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/assets"
        return self.client._send_request("GET", request_path, params={})

    def get_account_funding_assets(self, coin=None):
        """
        Obtain fund account information and only return the coins with assets.

        Args:
            coin (str, optional): Coin name.

        Returns:
            dict: Bitget API JSON response containing account funding assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/funding-assets"
        params = {}
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_account_fee_rate(self, symbol, category):
        """
        Get Account Fee Rate.

        Args:
            symbol (str): Symbol, e.g., `BTCUSDT`.
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).

        Returns:
            dict: Bitget API JSON response containing account fee rates.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/fee-rate"
        params = {"symbol": symbol, "category": category}
        return self.client._send_request("GET", request_path, params=params)

    def get_convert_records(self, fromCoin, toCoin, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query convert records within the last 90 days.

        Args:
            fromCoin (str): From coin (source coin). It refers to the coin being converted.
            toCoin (str): To coin (target coin). It refers to the coin being converted into (received).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing convert records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get BGB deduction status.

        Returns:
            dict: Bitget API JSON response containing BGB deduction status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/deduct-info"
        return self.client._send_request("GET", request_path, params={})

    def get_financial_records(self, category, coin=None, type=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query financial records within the last 90 days.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`, `OTHER`).
            coin (str, optional): Coin name e.g.,`BTC`.
            type (str, optional): Type (`TRANSFER_IN`/`TRANSFER_OUT`...... All enumeration values can be viewed under the Enumeration category).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing financial records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Subscribe to the account channel. Data will be pushed when the following events occur:
        1. Push on first-time subscription.
        2. Push when spot/margin/futures orders are filled in the unified trading account.
        3. Push when the fund settlement is done.
        4. Push when balance changes (transfers, airdrops, loans, etc.).

        Returns:
            dict: WebSocket message indicating subscription status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query payment coins.

        Returns:
            dict: Bitget API JSON response containing payment coin list and maximum selection.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/payment-coins"
        return self.client._send_request("GET", request_path, params={})

    def get_margin_coin_info(self, productId):
        """
        Get Margin Coin Info.

        Args:
            productId (str): Product Id.

        Returns:
            dict: Bitget API JSON response containing margin coin information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/ensure-coins-convert"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_margin_loan(self, coin):
        """
        Query interest rates for margin loans.

        Args:
            coin (str): Coin name e.g.,`BTC`.

        Returns:
            dict: Bitget API JSON response containing margin loan information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/margin-loans"
        params = {"coin": coin}
        return self.client._send_request("GET", request_path, params=params)

    def get_ltv(self, riskUnitId=None):
        """
        Get LTV.

        Args:
            riskUnitId (str, optional): Risk Unit ID.

        Returns:
            dict: Bitget API JSON response containing LTV information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/ltv-convert"
        params = {}
        if riskUnitId:
            params["riskUnitId"] = riskUnitId
        return self.client._send_request("GET", request_path, params=params)

    def batch_cancel(self, orders):
        """
        This endpoint allows you to cancel a multiple unfilled or partially filled order across spot, margin, and futures
        markets.
        When making a batch order cancellation, ensure that each request uses either orderId or clientOid for identification — never both. If both orderId and clientOid are provided in a single request, the clientOid will be ignored.
        Batch order cancellation allows partial success.

        Args:
            orders (list): A list of dictionaries, where each dictionary represents an order to be cancelled. Each order dictionary must contain:
                category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`). All orders must have the same category.
                symbol (str): Symbol name, e.g.,`BTCUSDT`.
                orderId (str, optional): Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
                clientOid (str, optional): Client order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed order cancellations.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-batch"
        return self.client._send_request("POST", request_path, body=orders)

    def batch_modify_orders(self, orderList):
        """
        Supports batch order modification via API, allowing simultaneous submission of multiple orders across different trading pairs (limited to orders within the same business line).
        Each request supports modification of up to 20 orders.
        Supports continuous order modification, meaning additional modification requests can be submitted before the previous modification request is completed. A maximum of 5 consecutive modification requests for in-progress orders can be submitted, and the matching engine will process the modification requests in sequence.
        Within the same batch of modification requests, each order can only appear once.
        Only fully unfilled orders can have their price and quantity modified.
        Partially filled orders can have their price and quantity modified (the modified quantity cannot be less than the already filled quantity).
        Modification of reduce-only orders is not supported.

        Args:
            orderList (list): A list of dictionaries, where each dictionary represents an order to be modified. Each order dictionary must contain:
                orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
                clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
                qty (str, optional): Order quantity. `Base coin`.
                price (str, optional): Order price.
                autoCancel (str, optional): Will the original order be canceled if the order modification fails (`yes` or `no`). Default: `no`.

        Returns:
            dict: Bitget API JSON response containing lists of modified orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/batch-modify-order"
        return self.client._send_request("POST", request_path, body=orderList)

    def batch_order(self, orderList):
        """
        This endpoint allows the order placement across spot, margin, or futures markets with customizable parameters, including
        price, quantity, and order type, etc.

        * **Upcoming Features** (currently not supported)
          + Isolated spot margin will be available soon.
          + Copy trading order placement will be available soon.
          + Take profit and stop loss will be available soon.

        * **Futures**
          For one-way mode, reduce-only orders are allowed to place. If a reduce only order already exists and the order
          quantity equals the position size, or if a new reduce only order exceeds the remaining position size, the previous
          reduction order will be automatically canceled and replaced. In this case, the returned orderId will be null.
          **It is recommended to always provide a `clientOid`. (currently,`reduce-only` orders are not supported)**

        * **Margin**
          Margin orders will automatically trigger fund borrowing.

        * **Order Check**

          + **Futures**:`price` must meet the price multiplier and be a multiple of `priceMultiplier`, and conform to the
            `pricePrecision` decimal places. `qty` must be greater than or equal to `minOrderAmount` and be a multiple of
            `sizeMultiplier`.
          + **Spot**:`price` must meet the decimal place requirement. `qty` must be greater than or equal to `minOrderAmount`.

        * **Open Position Logic**

          + **Hedge-mode**
            Open long: `side=buy` & `posSide=long`
            Open Short: `side=sell` & `posSide=short`
            Close long: `side=sell` & `posSide=long`
            Close short: `side=buy` & `posSide=short`
          + **One-way-mode**
            Open long: `side=buy`
            Open short: `side=sell`
            Close long: `side=sell` & `reduceOnly=yes`
            Close short: `side=buy` & `reduceOnly=yes`

        * **Order Limit**
          + **Futures**: 400 orders across all USDT, Coin-M, and USDC futures trading pairs.
          + **Spot**: 400 orders across all spot and margin trading pairs.

        * **ClientOid Constraints**
          Please ensure your clientOid matches the regular expression `^[\.A-Z\:/a-z0-9_-]{1,32}from .exceptions import BitgetAPIException
import time

class Uta:
    def __init__(self, client):
        self.client = client

    def get_account_info(self):
        """
        Query account information, including the holding mode, margin mode, leverage multiple, and more.

        Returns:
            dict: Bitget API JSON response containing account information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/settings"
        return self.client._send_request("GET", request_path, params={})

    def get_account_assets(self):
        """
        Query account information and assets, with only non-zero balances being returned.

        Returns:
            dict: Bitget API JSON response containing account assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/assets"
        return self.client._send_request("GET", request_path, params={})

    def get_account_funding_assets(self, coin=None):
        """
        Obtain fund account information and only return the coins with assets.

        Args:
            coin (str, optional): Coin name.

        Returns:
            dict: Bitget API JSON response containing account funding assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/funding-assets"
        params = {}
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_account_fee_rate(self, symbol, category):
        """
        Get Account Fee Rate.

        Args:
            symbol (str): Symbol, e.g., `BTCUSDT`.
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).

        Returns:
            dict: Bitget API JSON response containing account fee rates.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/fee-rate"
        params = {"symbol": symbol, "category": category}
        return self.client._send_request("GET", request_path, params=params)

    def get_convert_records(self, fromCoin, toCoin, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query convert records within the last 90 days.

        Args:
            fromCoin (str): From coin (source coin). It refers to the coin being converted.
            toCoin (str): To coin (target coin). It refers to the coin being converted into (received).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing convert records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get BGB deduction status.

        Returns:
            dict: Bitget API JSON response containing BGB deduction status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/deduct-info"
        return self.client._send_request("GET", request_path, params={})

    def get_financial_records(self, category, coin=None, type=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query financial records within the last 90 days.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`, `OTHER`).
            coin (str, optional): Coin name e.g.,`BTC`.
            type (str, optional): Type (`TRANSFER_IN`/`TRANSFER_OUT`...... All enumeration values can be viewed under the Enumeration category).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing financial records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Subscribe to the account channel. Data will be pushed when the following events occur:
        1. Push on first-time subscription.
        2. Push when spot/margin/futures orders are filled in the unified trading account.
        3. Push when the fund settlement is done.
        4. Push when balance changes (transfers, airdrops, loans, etc.).

        Returns:
            dict: WebSocket message indicating subscription status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query payment coins.

        Returns:
            dict: Bitget API JSON response containing payment coin list and maximum selection.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/payment-coins"
        return self.client._send_request("GET", request_path, params={})

    def get_margin_coin_info(self, productId):
        """
        Get Margin Coin Info.

        Args:
            productId (str): Product Id.

        Returns:
            dict: Bitget API JSON response containing margin coin information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/ensure-coins-convert"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_margin_loan(self, coin):
        """
        Query interest rates for margin loans.

        Args:
            coin (str): Coin name e.g.,`BTC`.

        Returns:
            dict: Bitget API JSON response containing margin loan information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/margin-loans"
        params = {"coin": coin}
        return self.client._send_request("GET", request_path, params=params)

    def get_ltv(self, riskUnitId=None):
        """
        Get LTV.

        Args:
            riskUnitId (str, optional): Risk Unit ID.

        Returns:
            dict: Bitget API JSON response containing LTV information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/ltv-convert"
        params = {}
        if riskUnitId:
            params["riskUnitId"] = riskUnitId
        return self.client._send_request("GET", request_path, params=params)

    def batch_cancel(self, orders):
        """
        This endpoint allows you to cancel a multiple unfilled or partially filled order across spot, margin, and futures
        markets.
        When making a batch order cancellation, ensure that each request uses either orderId or clientOid for identification — never both. If both orderId and clientOid are provided in a single request, the clientOid will be ignored.
        Batch order cancellation allows partial success.

        Args:
            orders (list): A list of dictionaries, where each dictionary represents an order to be cancelled. Each order dictionary must contain:
                category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`). All orders must have the same category.
                symbol (str): Symbol name, e.g.,`BTCUSDT`.
                orderId (str, optional): Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
                clientOid (str, optional): Client order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed order cancellations.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-batch"
        return self.client._send_request("POST", request_path, body=orders)

    def batch_modify_orders(self, orderList):
        """
        Supports batch order modification via API, allowing simultaneous submission of multiple orders across different trading pairs (limited to orders within the same business line).
        Each request supports modification of up to 20 orders.
        Supports continuous order modification, meaning additional modification requests can be submitted before the previous modification request is completed. A maximum of 5 consecutive modification requests for in-progress orders can be submitted, and the matching engine will process the modification requests in sequence.
        Within the same batch of modification requests, each order can only appear once.
        Only fully unfilled orders can have their price and quantity modified.
        Partially filled orders can have their price and quantity modified (the modified quantity cannot be less than the already filled quantity).
        Modification of reduce-only orders is not supported.

        Args:
            orderList (list): A list of dictionaries, where each dictionary represents an order to be modified. Each order dictionary must contain:
                orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
                clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
                qty (str, optional): Order quantity. `Base coin`.
                price (str, optional): Order price.
                autoCancel (str, optional): Will the original order be canceled if the order modification fails (`yes` or `no`). Default: `no`.

        Returns:
            dict: Bitget API JSON response containing lists of modified orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/batch-modify-order"
        return self.client._send_request("POST", request_path, body=orderList)

    , consisting of 1 to 32
          characters, including periods (.), uppercase letters, colons (:), lowercase letters, numbers, underscores (\_), and
          hyphens (-).

        * **Request Monitor**
          The API requests will be monitored. If the total number of orders for a single account (including master and
          sub-accounts) exceeds a set daily limit (UTC 00:00 - UTC 24:00), the platform reserves the right to issue reminders,
          warnings, and enforce necessary restrictions. By using the API, clients acknowledge and agree to comply with these
          terms.

        * **Error Sample**
          > { "code":"40762", "msg":"The order size is greater than the max open size", "requestTime":1627293504612 }
          >
          > This error code may occur in the following scenarios.
          >
          > + Insufficient account balance.
          > + The position tier for this symbol has reached its limit. For details on specific tiers, please
          >   refer [here](https://www.bitget.com/futures/introduction/position-tier?code=BTCUSDT_UMCBL?business=USDT_MIX_CONTRACT_BL) .

        Note: If the following errors occur when placing an order, please use `clientOid` to query the order details to confirm
        the final result of the operation.

        > { "code": "40010", "msg": "Request timed out", "requestTime": 1666268894074, "data": null }
        > { "code": "40725", "msg": "service return an error", "requestTime": 1666268894071, "data": null }
        > { "code": "45001", "msg": "Unknown error", "requestTime": 1666268894071, "data": null }

        Args:
            orderList (list): Collection of placing orders, maximum length: 50. Each item in the list should be a dictionary with the following keys:
                category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`). All orders must have the same category.
                symbol (str): Symbol name, e.g.,`BTCUSDT`.
                qty (str): Order quantity. For market buy orders, the unit is **quote coin**. For limit and market sell orders, the unit is **base coin**.
                side (str): Order side (`buy`/`sell`).
                orderType (str): Order type (`limit`/`market`).
                price (str, optional): Order price. This field is required when `orderType` is `limit`.
                timeInForce (str, optional): Time in force (`ioc`, `fok`, `gtc`, `post_only`). This field is required when `orderType` is `limit`. If omitted, it defaults to `gtc`.
                posSide (str, optional): Position side (`long`/`short`). This field is required in hedge-mode position. Available only for futures.
                clientOid (str, optional): Client order ID. The idempotent validity period is six hours (not fully guaranteed).

        Returns:
            dict: Bitget API JSON response containing lists of successful and failed orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/place-batch"
        return self.client._send_request("POST", request_path, body=orderList)

    def bind_unbind_uid_to_risk_unit(self, uid, operate, riskUnitId=None):
        """
        Bind/Unbind UID to Risk Unit.
        Binding:
        * The uid and riskUnitId belong to the same main account.
        * The uid is not bound to any other risk unit.
        Unbinding:
        * The API key used for the call must belong to the main account or the lending-exclusive sub-account UID within the risk
          unit.
        * The uid is within the risk unit and is not equal to riskUnitId.
        * The uid has a zero balance, or the riskUnitId has not_paid_off or in_progress loan orders.

        Args:
            uid (str): Sub UID (limit 50 UIDS for one Risk Unit).
            operate (str): `bind` Bind or `unbind` Unbind.
            riskUnitId (str, optional): Risk Unit ID (Required for parent account calls, not required for risk unit account calls).

        Returns:
            dict: Bitget API JSON response containing risk unit ID, UID, and operation.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/bind-uid"
        body = {
            "uid": uid,
            "operate": operate
        }
        if riskUnitId:
            body["riskUnitId"] = riskUnitId
        return self.client._send_request("POST", request_path, body=body)

    def batch_place_order_channel(self, category, orders):
        """
        Batch Place Order Channel.
        * Maximum 20 orders allowed in a single request.
        * Please contact your BD or RM to apply for access permissions.

        Args:
            category (str): Category (`spot`, `margin`, `usdt-futures`, `coin-futures`, `usdc-futures`).
            orders (list): List of order objects. Each order object should be a dictionary with the following keys:
                symbol (str): Symbol name.
                orderType (str): Order type (`limit` or `market`).
                qty (str): Order quantity. For market buy orders, the unit is quote coin. For limit and market sell orders, the unit is base coin. For futures, the unit is base coin.
                price (str, optional): Order price. This field is required when `orderType` is `limit`.
                side (str): Order side (`buy` or `sell`).
                posSide (str, optional): Position side (`long` or `short`). This field is required in hedge-mode positions. Available only for futures.
                timeInForce (str, optional): Time in force (`gtc`, `ioc`, `fok`, `post_only`). This field is required when `orderType` is `limit`. If omitted, it defaults to `gtc`.
                clientOid (str, optional): Client order ID.
                stpMode (str, optional): STP Mode (`none`, `cancel_taker`, `cancel_maker`, `cancel_both`).
                tpTriggerBy (str, optional): Preset Take-Profit Trigger Type (`market` or `mark`). If not specified, the default value is market price. Note: This field is only valid for the contract business lines: USDT-Futures, COIN-Futures, and USDC-Futures.
                slTriggerBy (str, optional): Preset Stop-Loss Trigger Type (`market` or `mark`). If not specified, the default value is market price. Note: This field is only valid for the contract business lines: USDT-Futures, COIN-Futures, and USDC-Futures.
                takeprofit (str, optional): Preset Take-Profit Trigger Price.
                stoploss (str, optional): Preset Stop-Loss Trigger Price.
                tpOrderType (str, optional): Take-Profit Trigger Strategy Order Type (`limit` or `market`).
                slOrderType (str, optional): Stop-Loss Trigger Strategy Order Type (`limit` or `market`).
                tpLimitPrice (str, optional): Take-Profit Strategy Order Execution Price. This field is only valid for limit orders (when `tpOrderType=limit`); it is ignored for market orders.
                slLimitPrice (str, optional): Stop-Loss Strategy Order Execution Price. This field is only valid for limit orders (when `slOrderType=limit`); it is ignored for market orders.

        Returns:
            dict: WebSocket message indicating the result of the batch place order operation.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        message = {
            "op": "trade",
            "id": str(int(time.time() * 1000)), # Generate a unique ID
            "category": category,
            "topic": "batch-place",
            "args": orders
        }
        return self.client._send_websocket_request(message)

    def cancel_all_orders(self, category, symbol=None):
        """
        Cancel unfilled or partially filled orders by symbol or category.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`. If no symbol is provided, all positions in the corresponding category will be closed.

        Returns:
            dict: Bitget API JSON response containing lists of cancelled orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-symbol-order"
        body = {"category": category}
        if symbol:
            body["symbol"] = symbol
        return self.client._send_request("POST", request_path, body=body)

    def cancel_order(self, orderId=None, clientOid=None):
        """
        This endpoint allows you to cancel a single unfilled or partially filled order across spot, margin, and futures markets.

        Args:
            orderId (str, optional): Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
            clientOid (str, optional): Client order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.

        Returns:
            dict: Bitget API JSON response containing the order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return self.client._send_request("POST", request_path, body=body)

    def cancel_strategy_order(self, orderId=None, clientOid=None):
        """
        Cancel strategy order.

        Args:
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/cancel-strategy-order"
        body = {}
        if orderId:
            body["orderId"] = orderId
        if clientOid:
            body["clientOid"] = clientOid
        return self.client._send_request("POST", request_path, body=body)

    def close_all_positions(self, category, symbol=None, posSide=None):
        """
        Close positions by position side or category. All positions will be closed at market price, subject to slippage.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`. If no symbol is provided, all positions in the corresponding category will be closed.
            posSide (str, optional): Position side (`long` or `short`). If this field is provided, only the position in the corresponding side will be closed.

        Returns:
            dict: Bitget API JSON response containing lists of closed positions.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/close-positions"
        body = {"category": category}
        if symbol:
            body["symbol"] = symbol
        if posSide:
            body["posSide"] = posSide
        return self.client._send_request("POST", request_path, body=body)

    def countdown_cancel_all(self, countdown):
        """
        In practical use, clients need to periodically send heartbeat requests to prevent uncontrolled open orders due to
        abnormal disconnections or system crashes.
        For example, if your expected heartbeat interval is 10 seconds, meaning if no heartbeat request is sent for over 10
        seconds, all orders must be canceled:

        * Under normal circumstances, you can call this interface every 3-5 seconds, set the countdown to 10, and repeatedly
          call it to reset the countdown.
        * Under abnormal circumstances, if no heartbeat request is sent for over 10 seconds, all orders under the account will
          be automatically canceled; after automatic cancellation, the Deadman Switch mechanism will automatically close.
        * To manually close the Deadman Switch mechanism, simply set the countdown to 0.
          P.S. This interface only supports canceling orders under UTA accounts, not classic accounts.

        Please contact your dedicated Business Development representative to apply for access to this interface.

        Args:
            countdown (str): Reconnect Window. Unit: seconds. Positive integer, range: [5, 60]. The minimum countdown is 5 second, and the maximum is 60 seconds. Filling in 0 cancels the countdown order cancellation function.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/countdown-cancel-all"
        body = {"countdown": countdown}
        return self.client._send_request("POST", request_path, body=body)

    def create_sub_account_api_key(self, subUid, note, type, passphrase, permissions, ips):
        """
        This API is used to create an API Key for a sub-account under a unified account. It is applicable when the main
        account is in a mix or unified account mode. If the current main account is in the classic account mode, this API
        cannot be called.

        Args:
            subUid (str): Sub-account ID.
            note (str): Note Name. The note needs to start with a letter and supports [0-9], [a-z], [A-Z], as well as [-,_].
            type (str): Permission Type (`read_write` or `read_only`).
            passphrase (str): Passphrase. A combination of 8 to 32 characters of letters and numbers.
            permissions (list): Permission values. Unified Account Permissions: `uta_mgt` Unified Account Management, `uta_trade` Unified Account Trading.
            ips (list): Withdrawal Whitelist IP. Multiple IP addresses are supported. A maximum of 30 IPs can be bound to a single key. **Only supports IPv4**.

        Returns:
            dict: Bitget API JSON response containing sub-account API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        This API is used for the main account to create a sub-account. It only supports creating unified account virtual sub-accounts and does not support creating regular sub-accounts.

        Args:
            username (str): Generate a virtual email address username. It can only contain lowercase letters and cannot exceed 20 characters.
            accountMode (str, optional): Sub-account Mode (`classic` Classic Account Sub-account or `unified` Unified Account Sub-account).
            note (str, optional): Note, cannot exceed 50 characters.

        Returns:
            dict: Bitget API JSON response containing sub-account details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/create-sub"
        body = {"username": username}
        if accountMode:
            body["accountMode"] = accountMode
        if note:
            body["note"] = note
        return self.client._send_request("POST", request_path, body=body)

    def freeze_unfreeze_sub_account(self, subUid, operation):
        """
        Freeze/Unfreeze Sub-account.

        Args:
            subUid (str): Sub-account ID to be frozen/unfrozen.
            operation (str): Operation Type (`freeze` or `unfreeze`).

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/freeze-sub"
        body = {
            "subUid": subUid,
            "operation": operation
        }
        return self.client._send_request("POST", request_path, body=body)

    def delete_sub_account_api_key(self, apiKey):
        """
        This API is used for the main account to delete a sub-account's API Key. It is not applicable for the main account or
        sub-account to delete their own API Key.

        Please note that once the deletion is completed, the sub-account API Key will be immediately invalid. Before performing
        the deletion, ensure that this operation will not cause any loss.

        This API only supports deleting API Keys of sub-accounts under a unified account, and does not support deleting API Keys
        of sub-accounts under a classic account.

        Args:
            apiKey (str): The sub-account API Key.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/delete-sub-api"
        body = {"apiKey": apiKey}
        return self.client._send_request("POST", request_path, body=body)

    def get_current_funding_rate(self, symbol):
        """
        Get current funding rate.

        Args:
            symbol (str): Trading pair, based on the symbolName, i.e. BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing current funding rate information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/current-fund-rate"
        params = {"symbol": symbol}
        return self.client._send_request("GET", request_path, params=params)

    def get_deposit_address(self, coin, chain=None, size=None):
        """
        Get deposit address.

        Args:
            coin (str): Coin name. The currency name can be obtained using the Get Currency Information API.
            chain (str, optional): Chain Name. The chain name can be obtained using the Get Currency Information API. If not filled, the system will automatically match a chain to generate a deposit address.
            size (str, optional): Deposit Quantity. Only applies to BTC Lightning Network. Limit range: 0.000001 - 0.01.

        Returns:
            dict: Bitget API JSON response containing deposit address information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/deposit-address"
        params = {"coin": coin}
        if chain:
            params["chain"] = chain
        if size:
            params["size"] = size
        return self.client._send_request("GET", request_path, params=params)

    def get_deposit_records(self, startTime, endTime, coin=None, orderId=None, limit=None, cursor=None):
        """
        Get deposit records.

        Args:
            startTime (str): Query record start time. Unix millisecond timestamp, e.g., 1690196141868.
            endTime (str): Query record end time. Unix millisecond timestamp, e.g., 1690196141868.
            coin (str, optional): Coin name. If left blank, all currency deposit records will be retrieved.
            orderId (str, optional): Order ID. Used for specifying order queries.
            limit (str, optional): Items per page. The default value is 20, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination to reduce query response time. Do not send for the initial query. When querying the second page and subsequent data, use the smallest orderId returned from the previous query. The results will return data less than that value.

        Returns:
            dict: Bitget API JSON response containing deposit records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query historical fills within the last 90 days.

        * **Query Range Constraint**
           Each individual query can only cover a maximum of 30 days within the 90-day window.

        Args:
            startTime (str): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            category (str, optional): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            orderId (str, optional): Order ID.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing fill history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query historical funding rate records. The Funding interval varies by symbol and can be retrieved via the Instruments endpoint.

        Args:
            category (str): Product Type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            cursor (str, optional): Page number. Default: `1`. Maximum: `100`.
            limit (str, optional): Limit per page. Default: `200`. Maximum: `200`.

        Returns:
            dict: Bitget API JSON response containing funding rate history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/history-fund-rate"
        params = {"category": category, "symbol": symbol}
        if cursor:
            params["cursor"] = cursor
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_instruments(self, category, symbol=None):
        """
        Query the specifications for online trading pair instruments.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.

        Returns:
            dict: Bitget API JSON response containing instrument information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/instruments"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_historical_candlestick_uta(self, category, symbol, interval, startTime=None, endTime=None, type=None, limit=None):
        """
        Query historical Kline/candlestick data within the last 90 days.

        Args:
            category (str): Product Type (`SPOT`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            interval (str): Granularity (`1m`,`3m`,`5m`,`15m`,`30m`,`1H`,`4H`,`6H`,`12H`,`1D`).
            startTime (str, optional): Start timestamp. A Unix millisecond timestamp, e.g.,`1672410780000`. Request data after this start time (the maximum time query range is 90 days).
            endTime (str, optional): End timestamp. A Unix millisecond timestamp, e.g.,`1672410781000`. Request data before this end time (the maximum time query range is 90 days).
            type (str, optional): Candlestick type (`MARKET`, `MARK`, `INDEX`). Default `MARKET`.
            limit (str, optional): Limit per page. Default:`100`. Maximum: `100`.

        Returns:
            dict: Bitget API JSON response containing historical candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query kline/candlestick data. This endpoint allows retrieving up to 1,000 candlesticks.

        Args:
            category (str): Product Type (`SPOT`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            interval (str): Granularity (`1m`,`3m`,`5m`,`15m`,`30m`,`1H`,`4H`,`6H`,`12H`,`1D`).
            startTime (str, optional): Start timestamp. A Unix millisecond timestamp, e.g.,`1672410780000`.
            endTime (str, optional): End timestamp. A Unix millisecond timestamp, e.g.,`1672410781000`.
            type (str, optional): Candlestick type (`market`, `mark`, `index`). Default: `market`.
            limit (str, optional): Limit per page. Default:`100`. Maximum: `100`.

        Returns:
            dict: Bitget API JSON response containing kline/candlestick data.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get Loan Orders.

        Args:
            orderId (str, optional): Loan order id. If not passed, then return all orders, sort by `loanTime` in descend.
            startTime (str, optional): The start timestamp (ms).
            endTime (str, optional): The end timestamp (ms).

        Returns:
            dict: Bitget API JSON response containing loan orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get max open available.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            orderType (str): Order type (`limit`/`market`).
            side (str): Transaction direction (`buy`/`sell`).
            price (str, optional): Order price. This field is required when `orderType` is `limit`.
            size (str, optional): Order quantity, base coin.

        Returns:
            dict: Bitget API JSON response containing max open available information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Interface is used to get future contract OI Limit.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Trading pair, based on the symbolName, i.e. BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing open interest limit information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/oi-limit"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_open_interest(self, category, symbol=None):
        """
        Query the total number of unsettled or open futures.

        Args:
            category (str): Product Type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.

        Returns:
            dict: Bitget API JSON response containing open interest information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/open-interest"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_open_orders(self, category=None, symbol=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query unfilled or partially filled orders. To query closed orders, please use the order history endpoint.

        Args:
            category (str, optional): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing open orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query order details using either orderId or clientOid.

        Args:
            orderId (str, optional): Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
            clientOid (str, optional): Client order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.

        Returns:
            dict: Bitget API JSON response containing order details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/trade/order-info"
        params = {}
        if orderId:
            params["orderId"] = orderId
        if clientOid:
            params["clientOid"] = clientOid
        return self.client._send_request("GET", request_path, params=params)

    def get_order_history(self, category, symbol=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query historical orders within the last 90 days.

        * **Query Range Constraint**
           Each individual query can only cover a maximum of 30 days within the 90-day window.

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page. Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing order history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query order book depth data.

        Args:
            category (str): Product Type (`SPOT`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            limit (str, optional): Limit per page. Default: `5`. Maximum: `200`.

        Returns:
            dict: Bitget API JSON response containing order book depth.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/orderbook"
        params = {
            "category": category,
            "symbol": symbol
        }
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_position_adl_rank(self):
        """
        Get Position ADL Rank.

        Returns:
            dict: Bitget API JSON response containing position ADL rank information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/position/adlRank"
        return self.client._send_request("GET", request_path, params={})

    def get_position_info(self, category, symbol=None, posSide=None):
        """
        Query real-time position data by symbol, side, or category.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name e.g.`BTCUSDT`. If no symbol is provided, all positions in the corresponding category will be returned.
            posSide (str, optional): Position side (`long`/`short`). If this field is provided, only the position in the corresponding side will be returned.

        Returns:
            dict: Bitget API JSON response containing position information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/position/current-position"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if posSide:
            params["posSide"] = posSide
        return self.client._send_request("GET", request_path, params=params)

    def get_position_tier(self, category, symbol=None, coin=None):
        """
        Query the position tier info.

        Args:
            category (str): Product type (`MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`, applies to `Futures`.
            coin (str, optional): Coin name, e.g.,`BTC`, applies to `Margin`.

        Returns:
            dict: Bitget API JSON response containing position tier information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/position-tier"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if coin:
            params["coin"] = coin
        return self.client._send_request("GET", request_path, params=params)

    def get_positions_history(self, category, symbol=None, startTime=None, endTime=None, limit=None, cursor=None):
        """
        Query historical positions within the last 90 days.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name e.g.,`BTCUSDT`.
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`. The access window is 90 days.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383185`. The time range between `startTime` and `endTime` must not exceed 30 days.
            limit (str, optional): Limit per page Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing positions history.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get Proof Of Reserves.

        Returns:
            dict: Bitget API JSON response containing proof of reserves information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/proof-of-reserves"
        return self.client._send_request("GET", request_path, params={})

    def get_repayment_orders(self, startTime=None, endTime=None, limit=None):
        """
        Get Repayment Orders.
        * By default, query the data of the past two years.
        * At most, support querying the data of the past two years.
        * Only display the data of successfully repaid orders.
        * Only display the repayment orders under the unified account. The orders under the spot account can be queried through
          the v2 version.

        Args:
            startTime (str, optional): The start timestamp (ms).
            endTime (str, optional): The end timestamp (ms).
            limit (str, optional): Limit default 100; max 100.

        Returns:
            dict: Bitget API JSON response containing repayment orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query risk reserve records.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.

        Returns:
            dict: Bitget API JSON response containing risk reserve information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/risk-reserve"
        params = {
            "category": category,
            "symbol": symbol
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_risk_unit(self):
        """
        Get Risk Unit. Only the parent account API Key can use this endpoint.

        Returns:
            dict: Bitget API JSON response containing all Risk Unit IDs.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/risk-unit"
        return self.client._send_request("GET", request_path, params={})

    def get_sub_account_api_keys(self, subUid, limit=None, cursor=None):
        """
        Supports querying the full API Key list under a single sub-account.

        Args:
            subUid (str): Sub-account UID.
            limit (str, optional): Items per page. The default value is 100, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination. Do not pass it for the first query. For subsequent queries (second page and beyond), use the cursor returned from the previous query.

        Returns:
            dict: Bitget API JSON response containing sub-account API keys.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/sub-api-list"
        params = {"subUid": subUid}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_sub_account_list(self, limit=None, cursor=None):
        """
        Query Sub-account List.

        Args:
            limit (str, optional): Items per page. The default value is 100, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination. Do not pass it for the first query. For subsequent queries (second page and beyond), use the cursor returned from the previous query.

        Returns:
            dict: Bitget API JSON response containing sub-account list.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/user/sub-list"
        params = {}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        return self.client._send_request("GET", request_path, params=params)

    def get_subaccount_unified_assets(self, subUid=None, cursor=None, limit=None):
        """
        Get SubAccount Unified Assets.

        Args:
            subUid (str, optional): Sub-account UID. Leave blank to return all sub-account asset lists.
            cursor (str, optional): Cursor ID. For pagination. Omit in first request. Pass previous cursor in subsequent requests.
            limit (str, optional): Sub-accounts per Page. Default value is 10, maximum is 50.

        Returns:
            dict: Bitget API JSON response containing sub-account unified assets.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get Switch Status. Only supports parent accounts.

        Returns:
            dict: Bitget API JSON response containing switch status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/switch-status"
        return self.client._send_request("GET", request_path, params={})

    def get_main_sub_transfer_records(self, subUid=None, role=None, coin=None, startTime=None, endTime=None, clientOid=None, limit=None, cursor=None):
        """
        This API supports retrieving transfer records between main and sub accounts.

        Args:
            subUid (str, optional): Sub-account UID. If not provided, transfer records of the main account will be retrieved.
            role (str, optional): Transfer-out account type (`initiator` or `receiver`). Default: `initiator`.
            coin (str, optional): Coin name.
            startTime (str, optional): Start time for querying transfer records. Unix millisecond timestamp, e.g., 1690196141868. The time interval between startTime and endTime should not exceed 90 days.
            endTime (str, optional): End time for querying transfer records. Unix millisecond timestamp, e.g., 1690196141868. The time interval between startTime and endTime should not exceed 90 days.
            clientOid (str, optional): clientOid, Cannot exceed 64 characters.
            limit (str, optional): Items per page. The default value is 100, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination. Do not pass it for the first query. For subsequent queries (second page and beyond), use the cursor returned from the previous query.

        Returns:
            dict: Bitget API JSON response containing main/sub transfer records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query real-time market data, including the latest price, 24-hour high/low, volume, bid, ask, and price change for available trading pairs.

        Args:
            category (str): Product type (`SPOT`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.

        Returns:
            dict: Bitget API JSON response containing ticker information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/tickers"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        return self.client._send_request("GET", request_path, params=params)

    def get_trade_symbols(self, productId):
        """
        Get Trade Symbols.

        Args:
            productId (str): Product Id.

        Returns:
            dict: Bitget API JSON response containing trade symbols information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/symbols"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)

    def get_transferable_coins(self, fromType, toType):
        """
        Query transferable coins **between Classic and UTA accounts**.
        *Classic accounts include Spot, Isolated Margin, Cross Margin, USDT Futures, USDC Futures, Coin-M Futures, and P2P accounts*

        Args:
            fromType (str): From (source) account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`, `uta`).
            toType (str): To (target) account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`, `uta`).

        Returns:
            dict: Bitget API JSON response containing a list of transferable coins.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/transferable-coins"
        params = {
            "fromType": fromType,
            "toType": toType
        }
        return self.client._send_request("GET", request_path, params=params)

    def get_transferred_quantity(self, coin, userId=None):
        """
        Get Transferred Quantity.

        Args:
            coin (str): Coin.
            userId (str, optional): User Id (Master account or sub-accounts).

        Returns:
            dict: Bitget API JSON response containing transferred quantity information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/transfered"
        params = {"coin": coin}
        if userId:
            params["userId"] = userId
        return self.client._send_request("GET", request_path, params=params)

    def get_withdrawal_records(self, startTime, endTime, coin=None, orderId=None, clientOid=None, limit=None, cursor=None):
        """
        Get withdrawal records.

        Args:
            startTime (str): Query record start time. Unix millisecond timestamp, e.g., 1690196141868.
            endTime (str): Query record end time. Unix millisecond timestamp, e.g., 1690196141868.
            coin (str, optional): Coin name. If not filled in, all coin deposit records will be retrieved.
            orderId (str, optional): order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
            clientOid (str, optional): Client Order ID. Either `clientOid` or `orderId` must be provided. If both are present or do not match, `orderId` will take priority.
            limit (str, optional): Items per page. The default value is 20, and the maximum value is 100.
            cursor (str, optional): Cursor ID. Used for pagination to reduce query response time. Do not send for the initial query. When querying the second page and subsequent data, use the smallest orderId returned from the previous query. The results will return data less than that value.

        Returns:
            dict: Bitget API JSON response containing withdrawal records.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Sub-account to Main Account Asset Transfer. The transfer types supported by this API include:

        * Main account to sub-account (only the main account API Key has permission)
        * Sub-account to main account (only the main account API Key has permission)
        * Sub-account to sub-account (only the main account API Key has permission, and the sending and receiving sub-accounts must belong to the same main account)
        * Sub-account internal transfer (only the main account API Key has permission, and the sending and receiving sub-accounts must be the same sub-account)

        The UID of the transferring and receiving accounts in the request parameters must be in a main-sub or sibling
        relationship, and the caller must be the main account API Key.

        Args:
            fromType (str): Transferring Account Type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `uta`). The above enumerations apply to the main account. If it is a sub-account: Unified account sub-account only supports `uta` and `spot`. Classic account sub-account does not support `uta` and `p2p`.
            toType (str): Receiving Account Type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `uta`). The above enumerations apply to the main account. If it is a sub-account: Unified account sub-account only supports `uta` and `spot`. Classic account sub-account does not support `uta` and `p2p`.
            amount (str): Amount to Transfer In.
            coin (str): Transfer Currency, e.g., BTC.
            fromUserId (str): Transferring Account UID.
            toUserId (str): Receiving Account UID.
            clientOid (str): clientOid, Cannot exceed 64 characters.

        Returns:
            dict: Bitget API JSON response containing transfer ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Support for fund transfers in and out between unified accounts and classic accounts.

        Args:
            fromType (str): From (source) account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`, `uta`).
            toType (str): To (target) account type (`spot`, `p2p`, `coin_futures`, `usdt_futures`, `usdc_futures`, `crossed_margin`, `isolated_margin`, `uta`).
            amount (str): Transfer amount.
            coin (str): Transfer coin e.g: BTC.
            symbol (str, optional): Isolated spot margin e.g: BTCUSDT.

        Returns:
            dict: Bitget API JSON response containing transfer ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Support modifying orders using either the order ID (orderId) or a custom order ID (clientOid).

        * Only orders that have not been fully filled can be modified. If an order has been completely filled, it cannot be modified through this interface.
        * After submitting a modification request and before receiving the result, repeated modification requests cannot be submitted.

        Args:
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            qty (str, optional): Order quantity. `Base coin`. Either `qty` or `price` must be provided.
            price (str, optional): Order price. Either `qty` or `price` must be provided.
            autoCancel (str, optional): Will the original order be canceled if the order modification fails (`yes` or `no`). Default: `no`.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get historical strategy orders.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            type (str, optional): Strategy Type (`tpsl` Take-Profit and Stop-Loss).
            startTime (str, optional): Start timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`.
            endTime (str, optional): End timestamp. A Unix timestamp in milliseconds e.g.,`1597026383085`.
            limit (str, optional): Limit per page Default:`100`. Maximum:`100`.
            cursor (str, optional): Cursor. Pagination is implemented by omitting the cursor in the first query and applying the cursor from the previous query for subsequent pages.

        Returns:
            dict: Bitget API JSON response containing historical strategy orders.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Modify strategy order.

        Args:
            orderId (str, optional): Order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            clientOid (str, optional): Client order ID. Either `orderId` or `clientOid` must be provided. If both are provided, `orderId` takes higher priority.
            qty (str, optional): Order Quantity. Can be modified under partial take-profit/stop-loss mode, and the unit is in the `base coin`.
            tpTriggerBy (str, optional): Take-Profit Trigger Type (`market` or `mark`).
            slTriggerBy (str, optional): Stop-Loss Trigger Type (`market` or `mark`).
            takeProfit (str, optional): Take-Profit Trigger Price.
            stopLoss (str, optional): Stop-Loss Trigger Price.
            tpOrderType (str, optional): Take-Profit Trigger Strategy Order Type (`limit` or `market`).
            slOrderType (str, optional): Stop-Loss Trigger Strategy Order Type (`limit` or `market`).
            tpLimitPrice (str, optional): Take-Profit Strategy Order Execution Price. This field is only valid for limit orders (when `tpOrderType=limit`); it is ignored for market orders.
            slLimitPrice (str, optional): Stop-Loss Strategy Order Execution Price. This field is only valid for limit orders (when `slOrderType=limit`); it is ignored for market orders.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        This API is used to modify the unified account sub-account API Key permissions and withdrawal whitelist IP addresses. It only supports modifying the API Key of a unified account sub-account and does not support creating an API Key for a classic account sub-account.

        Args:
            apiKey (str): Sub-account API Key.
            passphrase (str): Passphrase. A combination of 8 to 32 characters of letters and numbers.
            type (str, optional): Permission Type (`read_write` or `read_only`). **This parameter is required when `permissions` has a value.**
            permissions (list, optional): Permission values. Unified Account Permissions: `uta_mgt` Unified Account Management, `uta_trade` Unified Account Trading. **This parameter is required when `type` has a value.**
            ips (list, optional): Withdrawal Whitelist IP. If not provided, the IP address will not be modified. If an empty value is provided, the withdrawal whitelist will be deleted. Multiple IP addresses are supported. A maximum of 30 IPs can be bound to a single key. **Only supports IPv4**.

        Returns:
            dict: Bitget API JSON response containing modified sub-account API key details.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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

    , consisting of 1 to 32 characters, including periods (.), uppercase letters, colons (:), lowercase letters, numbers, underscores (\_), and hyphens (-).

        * **Request Monitor**
          The API requests will be monitored. If the total number of orders for a single account (including master and
          sub-accounts) exceeds a set daily limit (UTC 00:00 - UTC 24:00), the platform reserves the right to issue reminders,
          warnings, and enforce necessary restrictions. By using the API, clients acknowledge and agree to comply with these
          terms.

        * **Error Sample**
          > { "code":"40762", "msg":"The order size is greater than the max open size", "requestTime":1627293504612 }
          >
          > This error code may occur in the following scenarios.
          >
          > + Insufficient account balance.
          > + The position tier for this symbol has reached its limit. For details on specific tiers, please refer [here](https://www.bitget.com/futures/introduction/position-tier?code=BTCUSDT_UMCBL?business=USDT_MIX_CONTRACT_BL) .

        Note: If the following errors occur when placing an order, please use `clientOid` to query the order details to confirm the final result of the operation.

        > { "code": "40010", "msg": "Request timed out", "requestTime": 1666268894074, "data": null }
        > { "code": "40725", "msg": "service return an error", "requestTime": 1666268894071, "data": null }
        > { "code": "45001", "msg": "Unknown error", "requestTime": 1666268894071, "data": null }

        Args:
            category (str): Product type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            qty (str): Order quantity. `Spot/Margin`: For market buy orders, the unit is **quote coin**. For limit and market sell orders, the unit is **base coin**. `Futures`: The unit is **base coin**.
            side (str): Order side (`buy`/`sell`).
            orderType (str): Order type (`limit`/`market`).
            price (str, optional): Order price. This field is required when `orderType` is `limit`.
            timeInForce (str, optional): Time in force (`ioc`, `fok`, `gtc`, `post_only`). This field is required when `orderType` is `limit`. If omitted, it defaults to `gtc`.
            posSide (str, optional): Position side (`long`/`short`). This field is required in hedge-mode position. Available only for futures.
            clientOid (str, optional): Client order ID. The idempotent validity period is six hours (not fully guaranteed).
            reduceOnly (str, optional): Reduce-only identifier (`yes`/`no`), default `no`. `yes` indicates that your position may only be reduced in size upon the activation of this order.
            stpMode (str, optional): STP Mode (Self Trade Prevention) (`none`, `cancel_taker`, `cancel_maker`, `cancel_both`).
            tpTriggerBy (str, optional): Preset Take-Profit Trigger Type (`market` or `mark`). If not specified, the default value is market price. Note: This field is only valid for the contract business lines: USDT-Futures, COIN-FUTURES, and USDC-FUTURES.
            slTriggerBy (str, optional): Preset Stop-Loss Trigger Type (`market` or `mark`). If not filled in, the default value is market price. Note: This field is only valid for the contract business lines: USDT-Futures, COIN-FUTURES, and USDC-FUTURES.
            takeProfit (str, optional): Preset Take-Profit Trigger Price.
            stopLoss (str, optional): Preset Stop-Loss Trigger Price.
            tpOrderType (str, optional): Take-Profit Trigger Strategy Order Type (`limit` or `market`).
            slOrderType (str, optional): Stop-Loss Trigger Strategy Order Type (`limit` or `market`).
            tpLimitPrice (str, optional): Take-Profit Strategy Order Execution Price. This field is only valid for limit orders (when `tpOrderType=limit`); it is ignored for market orders.
            slLimitPrice (str, optional): Stop-Loss Strategy Order Execution Price. This field is only valid for limit orders (when `slOrderType=limit`); it is ignored for market orders.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Place a strategy order.

        Args:
            category (str): Product type (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str): Symbol name, e.g.,`BTCUSDT`.
            posSide (str): Position side (`long`/`short`).
            clientOid (str, optional): Client order ID. The idempotent validity period is six hours (not fully guaranteed).
            type (str, optional): Strategy Type (`tpsl` Take-Profit and Stop-Loss). Default:`tpsl`.
            tpslMode (str, optional): Take-Profit and Stop-Loss Mode (`full` All Positions Take-Profit and Stop-Loss or `partial` Partial Position Take-Profit and Stop-Loss). If left blank, the default value is `full`.
            qty (str, optional): Order Quantity. This is a required field when `tpslMode=partial`, and the unit is in the `base coin`.
            tpTriggerBy (str, optional): Take-Profit Trigger Type (`market`: Market Price or `mark`: Mark Price). If not specified, the default value is market price.
            slTriggerBy (str, optional): Stop-Loss Trigger Type (`market`: Market Price or `mark`: Mark Price). If not filled in, the default value is market price.
            takeProfit (str, optional): Preset Take-Profit Trigger Price.
            stopLoss (str, optional): Preset Stop-Loss Trigger Price.
            tpOrderType (str, optional): Take-Profit Trigger Strategy Order Type (`limit`: Limit Order or `market`: Market Order). If not filled in, the default value is market price.
            slOrderType (str, optional): Stop-Loss Trigger Strategy Order Type (`limit`: Limit Order or `market`: Market Order). If not filled in, the default value is market price.
            tpLimitPrice (str, optional): Take-Profit Strategy Order Execution Price. This field is only valid for limit orders (when `tpOrderType=limit`); it is ignored for market orders.
            slLimitPrice (str, optional): Stop-Loss Strategy Order Execution Price. This field is only valid for limit orders (when `slOrderType=limit`); it is ignored for market orders.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Subscribe to the position channel. Data will be pushed when the following events occur:

        1. Push on the first-time subscription.
        2. Push incremental data when close-position orders are placed in the unified trading account.
        3. Push incremental data when futures positions are opened in the unified trading account.
        4. Push incremental data when futures positions are closed in the unified trading account.
        5. Push incremental data when futures close-position orders are modified in the unified trading account.
        6. Push incremental data when futures close-position orders are cancelled in the unified trading account.

        Returns:
            dict: WebSocket message indicating subscription status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Subscribe to the order channel. The following events will trigger a data push:

        1. No Push on first-time subscription.
        2. Push when spot/margin/futures orders are placed in the unified trading account.
        3. Push when spot/margin/futures orders are filled in the unified trading account.
        4. Push when spot/margin/futures orders are cancelled in the unified trading account.

        Returns:
            dict: WebSocket message indicating subscription status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        To subscribe the public trades channel.

        Args:
            instType (str): Product type (`spot`, `usdt-futures`, `coin-futures`, `usdc-futures`).
            symbol (str): Symbol name, e.g. `BTCUSDT`.

        Returns:
            dict: WebSocket message indicating subscription status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Get the latest transaction price, best bid, best ask, and 24-hour trading volume for the product. When there are
        changes (transactions, best bid/ask updates), the push frequency is:

        * Spot push frequency: 100ms
        * Futures push frequency: 100ms

        Args:
            instType (str): Product type (`spot`, `usdt-futures`, `coin-futures`, `usdc-futures`).
            symbol (str): Trading pair, e.g. `BTCUSDT`.

        Returns:
            dict: WebSocket message indicating subscription status.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        This endpoint enables manual repayment in the Unified Trading Account.

        Args:
            repayableCoinList (list): Repayable coin list. Each item in the list should be a string representing the repayable coin name, e.g.,`USDT`.
            paymentCoinList (list): Payment coin list. Each item in the list should be a string representing the payment coin name, e.g.,`ETH`.

        Returns:
            dict: Bitget API JSON response containing repayment result and amount.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/repay"
        body = {
            "repayableCoinList": repayableCoinList,
            "paymentCoinList": paymentCoinList
        }
        return self.client._send_request("POST", request_path, body=body)

    def set_holding_mode(self, holdMode):
        """
        This endpoint allows you to set the position holding mode between one-way and hedge mode.

        Args:
            holdMode (str): Holding mode (`one_way_mode` This mode allows holding positions in a single direction, either long or short, but not both at the same time or `hedge_mode` This mode allows holding both long and short positions simultaneously).

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/set-hold-mode"
        body = {
            "holdMode": holdMode
        }
        return self.client._send_request("POST", request_path, body=body)

    def set_leverage(self, category, leverage, symbol=None, coin=None, posSide=None):
        """
        This endpoint allows you to set leverage.

        Args:
            category (str): Product type (`MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            leverage (str): Leverage multiple.
            symbol (str, optional): Symbol name. This field is required to set leverage for futures.
            coin (str, optional): Coin name. This field is required to set leverage for margin trading.
            posSide (str, optional): Position side (`long`/`short`). This field is required to set leverage for isolated margin.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        This configuration item remains valid for a long time. That is, once a user sets a default recharge account for a
        certain symbol, it will be retained permanently, and there is no need to reconfigure it.

        Args:
            coin (str): Recharge coin, e.g.,`BTC`.
            accountType (str): Account type (`funding` Funding account, `unified` Unified account, `otc` OTC account). The current default is the funding account, and it can be modified to a unified account or an OTC account.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/deposit-account"
        body = {
            "coin": coin,
            "accountType": accountType
        }
        return self.client._send_request("POST", request_path, body=body)

    def switch_account(self):
        """
        Switch Account.
        1. Only supports parent accounts.
        2. This endpoint is only used for switching to classic account mode.
        3. Please note that since the account switching process takes approximately 1 minute, the successful response you receive only indicates that the request has been received, and does not mean that the account has been successfully switched to the classic account.
        4. Please use the query switching status interface to confirm whether the account switching is successful.

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/switch"
        body = {}
        return self.client._send_request("POST", request_path, body=body)

    def switch_deduct(self, deduct):
        """
        Set BGB deduction.

        Args:
            deduct (str): Is it enabled (`on` or `off`).

        Returns:
            dict: Bitget API JSON response.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/switch-deduct"
        body = {
            "deduct": deduct
        }
        return self.client._send_request("POST", request_path, body=body)

    def withdrawal(self, coin, transferType, address, size, chain=None, innerToType=None, areaCode=None, tag=None, remark=None, clientOid=None, memberCode=None, identityType=None, companyName=None, firstName=None, lastName=None):
        """
        Includes on-chain withdrawals and internal transfers.

        Args:
            coin (str): Coin name.
            transferType (str): Withdrawal Type (`on_chain` On-chain deposit or `internal_transfer` Internal transfer).
            address (str): Withdrawal Address. When `transferType` is `on_chain`, fill in the chain address. When `transferType` is `internal_transfer`, fill in the UID, email, or mobile number based on innerToType.
            size (str): Withdrawal Quantity. Special Notes for Bitcoin Lightning Network Withdrawals: This parameter must exactly match the amount on the Bitcoin Lightning Network deposit invoice; The withdrawal quantity for Bitcoin Lightning Network represents the amount received, excluding fees; The quantity precision can be obtained via the "Get Currency Information" API.
            chain (str, optional): Blockchain Network. For example, `erc20`, `trc20`, etc. This parameter is required when `transferType`=`on_chain`. The chain name can be obtained using the Get Currency Information API.
            innerToType (str, optional): Internal Withdrawal Address Type (`uid` User ID, `email` Email, `mobile` Mobile phone number). If not filled, the default value is `uid`.
            areaCode (str, optional): Area Code. This parameter is required when `innerToType` = `mobile`.
            tag (str, optional): Address Tag. This is required for withdrawals of certain cryptocurrencies, like EOS.
            remark (str, optional): Remark.
            clientOid (str, optional): Client Order ID.
            memberCode (str, optional): Member Code (`bithumb`, `korbit`, `coinone`).
            identityType (str, optional): Identity Type (`company` Institutional Company or `user` Individual User).
            companyName (str, optional): Company Name. Fill in this parameter when `identity`=`company`.
            firstName (str, optional): First Name. Fill in this parameter when `identity`=`user`.
            lastName (str, optional): Last Name. Fill in this parameter when `identity`=`user`.

        Returns:
            dict: Bitget API JSON response containing order ID and client customized ID.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
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
        """
        Query recent public fill data on Bitget.

        Args:
            category (str): Product Type (`SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
            symbol (str, optional): Symbol name, e.g.,`BTCUSDT`.
            limit (str, optional): Limit per page. Default: `100`. Maximum: `100`.

        Returns:
            dict: Bitget API JSON response containing recent public fills.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/market/fills"
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        if limit:
            params["limit"] = limit
        return self.client._send_request("GET", request_path, params=params)

    def get_repayable_coins(self):
        """
        Query repayable coins.

        Returns:
            dict: Bitget API JSON response containing repayable coin list and maximum selection.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/account/repayable-coins"
        return self.client._send_request("GET", request_path, params={})

    def get_product_info(self, productId):
        """
        Get Product Info.

        Args:
            productId (str): Product Id.

        Returns:
            dict: Bitget API JSON response containing product information.

        Raises:
            BitgetAPIParameterException: If parameters are invalid.
            BitgetAPIAuthException: If authentication fails.
            BitgetAPIException: For other API errors.
        """
        request_path = "/api/v3/ins-loan/product-infos"
        params = {"productId": productId}
        return self.client._send_request("GET", request_path, params=params)
