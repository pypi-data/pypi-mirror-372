from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class TradeVolumeIndex(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addTradeVolumeIndex', {'traderID': trader.id})

    def set_minimum_tick_value(self, minimum_tick_value: int | float):
        """Sets the minimum tick value for the Trade Volume Index.

        Args:
            minimum_tick_value (int | float): The minimum price change required to count as a tick in the Trade Volume Index.
        """
        self.instance.send(self.id, 'setMinimumTickValue', {'minimumTickValue': minimum_tick_value})
        return self
