from lightningchart_trader.indicators import LineIndicator


class AccumulativeSwingIndex(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addAccumulativeSwingIndex', {'traderID': trader.id})

    def set_limit_move_value(self, limit_move_value: float):
        """Sets the maximum price change in one direction.

        Args:
            limit_move_value (float): Maximum price change.
        """
        self.instance.send(self.id, 'setLimitMoveValue', {'limitMoveValue': limit_move_value})
        return self
