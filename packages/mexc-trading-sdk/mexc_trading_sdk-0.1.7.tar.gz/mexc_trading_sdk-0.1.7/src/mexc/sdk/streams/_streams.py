from dataclasses import dataclass
from .depth import Depth
from .my_trades import MyTrades

@dataclass
class Streams(Depth, MyTrades):
  ...