from lightningchart_trader.indicators import LineIndicator


class SwingIndex(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addSwingIndex', {'traderID': trader.id})

    def set_limit_move_value(self, limit_move_value: int | float):
        """Sets the limit move value for the Swing Index calculation.

        Args:
            limit_move_value (int | float): The maximum price movement value used in the Swing Index calculation.
        """
        self.instance.send(self.id, 'setLimitMoveValue', {'limitMoveValue': limit_move_value})
        return self
