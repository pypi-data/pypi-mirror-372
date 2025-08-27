from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class QStick(LineIndicator, PeriodIndicator):
    def __init__(self, trader, period_count: int):
        super().__init__(trader)
        self.instance.send(self.id, 'addQStick', {'traderID': trader.id, 'periodCount': period_count})

    def set_moving_average_type(self, moving_average_type: int):
        """
        Sets the moving average type for the QStick indicator.

        Args:
            moving_average_type (int): The type of moving average to be applied (e.g., 0 for simple, 1 for exponential).
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self
