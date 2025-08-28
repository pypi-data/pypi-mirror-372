from datetime import datetime
import pandas as pd
import numpy as np
from munch import Munch

from .base_manager import BaseManager

class PositionManager(BaseManager):
    def __init__(self, main_trade) -> None:
        super().__init__(main_trade)

        self.symbol_position_map = {}

    def update_position(self, data):
        symbol = data.symbol
        self.symbol_position_map[symbol] = data
        self.main_trade.on_position_detail(data)

    def position(self, symbol):
        return self.symbol_position_map.get(symbol)