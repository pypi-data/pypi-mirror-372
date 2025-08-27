from dataclasses import dataclass
from .market_data import MarketData
from .trading import Trading
from .user_data import UserData

@dataclass
class Spot(MarketData, Trading, UserData):
  ...