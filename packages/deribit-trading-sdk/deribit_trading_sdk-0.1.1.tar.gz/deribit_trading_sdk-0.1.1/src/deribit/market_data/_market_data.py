from dataclasses import dataclass

from .get_contract_size import GetContractSize
from .get_index_price import GetIndexPrice
from .get_instrument import GetInstrument
from .get_instruments import GetInstruments
from .get_order_book import GetOrderBook
from .get_last_trades_by_instrument import GetLastTradesByInstrument

@dataclass(frozen=True)
class MarketData(
  GetContractSize,
  GetIndexPrice,
  GetInstrument,
  GetInstruments,
  GetOrderBook,
  GetLastTradesByInstrument,
):
  ...