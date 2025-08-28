# purpletrader

A lightweight Python client for the Live Trading Engine HTTP API.

## Installation

```bash
pip install purpletrader
```

## Usage

```python
from purpletrader import TradingEngineClient, Order, Timeframe

# Optionally set a default user_id so you don't have to provide it per order
client = TradingEngineClient(base_url="http://localhost:8080", user_id="trader_123")

# Submit order
resp = client.submit_order(Order(
    id="order_001",
    symbol="AAPL",
    type="LIMIT",
    side="BUY",
    quantity=100,
    price=150.25,
))
print(resp)

# Fetch data
print(client.get_orderbook("AAPL"))
print(client.get_stats("AAPL"))
print(client.get_stats_timeframe("AAPL", Timeframe.ONE_MINUTE))
print(client.get_all_stats())
print(client.get_stats_summary())
print(client.get_leaderboard())
print(client.health())
```

## Notes
- Raises `HTTPError` on non-2xx responses with `status_code`, `message`, and `body`.
- Default timeout is 30s; override via `TradingEngineClient(timeout=...)`.
- You can still override `userId` per order by passing it in the `Order`.
