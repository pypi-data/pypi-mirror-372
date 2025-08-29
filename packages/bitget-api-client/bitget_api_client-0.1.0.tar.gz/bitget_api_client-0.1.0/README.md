# Bitget API Client

A Python client for the Bitget API V2.

## Installation

```bash
pip install bitget-api-client
```

## Usage

```python
import asyncio
from bitget_api_client.client import BitgetApiClient

async def main():
    api_key = "YOUR_API_KEY"
    secret_key = "YOUR_SECRET_KEY"
    passphrase = "YOUR_PASSPHRASE"

    client = BitgetApiClient(api_key, secret_key, passphrase)

    # Example: Get server time
    response = await client.common.get_server_time()
    print(response)

    # Example: Get spot ticker
    # response = await client.spot.get_ticker_information(symbol="BTCUSDT")
    # print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.