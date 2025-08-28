# Trading

Types:

```python
from sigma.types import Order, TradingListResponse
```

Methods:

- <code title="get /trading/orders">client.trading.<a href="./src/sigma/resources/trading.py">list</a>() -> <a href="./src/sigma/types/trading_list_response.py">TradingListResponse</a></code>
- <code title="post /trading/order">client.trading.<a href="./src/sigma/resources/trading.py">submit</a>(\*\*<a href="src/sigma/types/trading_submit_params.py">params</a>) -> <a href="./src/sigma/types/order.py">Order</a></code>

# Market

## Instrument

Types:

```python
from sigma.types.market import Instrument
```

Methods:

- <code title="get /market/instrument">client.market.instrument.<a href="./src/sigma/resources/market/instrument.py">retrieve</a>() -> <a href="./src/sigma/types/market/instrument.py">Instrument</a></code>
- <code title="get /market/instrument">client.market.instrument.<a href="./src/sigma/resources/market/instrument.py">get</a>() -> <a href="./src/sigma/types/market/instrument.py">Instrument</a></code>

## OrderBook

Types:

```python
from sigma.types.market import OrderBook
```

Methods:

- <code title="get /market/orderBook">client.market.order_book.<a href="./src/sigma/resources/market/order_book.py">retrieve</a>() -> <a href="./src/sigma/types/market/order_book.py">OrderBook</a></code>
- <code title="get /market/orderBook">client.market.order_book.<a href="./src/sigma/resources/market/order_book.py">get</a>() -> <a href="./src/sigma/types/market/order_book.py">OrderBook</a></code>

## Ticker

Types:

```python
from sigma.types.market import Ticker
```

Methods:

- <code title="get /market/ticker">client.market.ticker.<a href="./src/sigma/resources/market/ticker.py">retrieve</a>() -> <a href="./src/sigma/types/market/ticker.py">Ticker</a></code>
- <code title="get /market/ticker">client.market.ticker.<a href="./src/sigma/resources/market/ticker.py">get</a>() -> <a href="./src/sigma/types/market/ticker.py">Ticker</a></code>

## Kline

Types:

```python
from sigma.types.market import Kline
```

Methods:

- <code title="get /market/kline">client.market.kline.<a href="./src/sigma/resources/market/kline.py">retrieve</a>() -> <a href="./src/sigma/types/market/kline.py">Kline</a></code>
- <code title="get /market/kline">client.market.kline.<a href="./src/sigma/resources/market/kline.py">get</a>() -> <a href="./src/sigma/types/market/kline.py">Kline</a></code>

# Portfolio

Types:

```python
from sigma.types import Portfolio
```

Methods:

- <code title="get /portfolio">client.portfolio.<a href="./src/sigma/resources/portfolio/portfolio.py">retrieve</a>() -> <a href="./src/sigma/types/portfolio/portfolio.py">Portfolio</a></code>
- <code title="get /portfolio">client.portfolio.<a href="./src/sigma/resources/portfolio/portfolio.py">get</a>() -> <a href="./src/sigma/types/portfolio/portfolio.py">Portfolio</a></code>

## Balance

Types:

```python
from sigma.types.portfolio import Balance
```

Methods:

- <code title="get /portfolio/balance">client.portfolio.balance.<a href="./src/sigma/resources/portfolio/balance.py">retrieve</a>() -> <a href="./src/sigma/types/portfolio/balance.py">Balance</a></code>
- <code title="get /portfolio/balance">client.portfolio.balance.<a href="./src/sigma/resources/portfolio/balance.py">get</a>() -> <a href="./src/sigma/types/portfolio/balance.py">Balance</a></code>

## OpenPosition

Types:

```python
from sigma.types.portfolio import OpenPosition
```

Methods:

- <code title="get /portfolio/openPosition">client.portfolio.open_position.<a href="./src/sigma/resources/portfolio/open_position.py">retrieve</a>() -> <a href="./src/sigma/types/portfolio/open_position.py">OpenPosition</a></code>
- <code title="get /portfolio/openPosition">client.portfolio.open_position.<a href="./src/sigma/resources/portfolio/open_position.py">get</a>() -> <a href="./src/sigma/types/portfolio/open_position.py">OpenPosition</a></code>

## Credit

Types:

```python
from sigma.types.portfolio import Credit
```

Methods:

- <code title="get /portfolio/credit">client.portfolio.credit.<a href="./src/sigma/resources/portfolio/credit.py">retrieve</a>() -> <a href="./src/sigma/types/portfolio/credit.py">Credit</a></code>
- <code title="get /portfolio/credit">client.portfolio.credit.<a href="./src/sigma/resources/portfolio/credit.py">get</a>() -> <a href="./src/sigma/types/portfolio/credit.py">Credit</a></code>

# Account

## Userdata

Types:

```python
from sigma.types.account import UserData
```

Methods:

- <code title="get /account/userdata">client.account.userdata.<a href="./src/sigma/resources/account/userdata.py">retrieve</a>() -> <a href="./src/sigma/types/account/user_data.py">UserData</a></code>
