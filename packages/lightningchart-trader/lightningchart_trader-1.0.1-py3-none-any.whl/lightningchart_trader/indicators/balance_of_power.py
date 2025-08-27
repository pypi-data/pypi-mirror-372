from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class BalanceOfPower(LineIndicator, PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addBalanceOfPower', {'traderID': trader.id})

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of Moving Average used to smooth the indicator.

        Args:
            moving_average_type (int): Moving Average type (use enumeration values).
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self
