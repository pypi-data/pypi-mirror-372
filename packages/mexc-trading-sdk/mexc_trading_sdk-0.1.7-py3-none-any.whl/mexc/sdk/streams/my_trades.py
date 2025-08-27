from typing_extensions import Literal
from dataclasses import dataclass, field
from decimal import Decimal
from collections import defaultdict
import asyncio
from trading_sdk.streams.my_trades import MyTrades as MyTradesTDK, Trade
from mexc.core import timestamp as ts
from mexc.spot.streams.user.my_trades import TradeType
from mexc.sdk.util import SdkMixin, wrap_exceptions

def level(limit: int | None) -> Literal[5, 10, 20]:
  if limit is None:
    return 20
  elif limit < 5:
    return 5
  elif limit < 10:
    return 10
  else:
    return 20

@dataclass
class MyTrades(MyTradesTDK, SdkMixin):
  _queues: defaultdict[str, asyncio.Queue[Trade]] = field(default_factory=lambda: defaultdict(asyncio.Queue))
  _listener: asyncio.Task | None = None

  async def __aexit__(self, exc_type, exc_value, traceback):
    if self._listener is not None:
      self._listener.cancel()
      self._listener = None
    await super().__aexit__(exc_type, exc_value, traceback)

  @wrap_exceptions
  async def my_trades(self, base: str, quote: str):
    symbol = f'{base}{quote}'
    if self._listener is None:
      async def listener():
        async for trade in self.client.spot.streams.my_trades():
            t = Trade(
              id=trade.tradeId,
              price=Decimal(trade.price),
              qty=Decimal(trade.quantity),
              time=ts.parse(trade.time),
              side='BUY' if trade.tradeType == TradeType.BUY else 'SELL',
            )
            self._queues[trade.symbol].put_nowait(t)
      self._listener = asyncio.create_task(listener())

    while True:
      yield await self._queues[symbol].get()