from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class WilliamsVariableAccumulationDistribution(LineIndicator, PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addWilliamsVariableAccumulationDistribution',
            {'traderID': trader.id},
        )

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the moving average type for the indicator.

        Args:
            moving_average_type (int): The type of moving average to use.
            Typically, values represent different types of moving averages, such as:
                0 = Simple Moving Average (SMA)
                1 = Exponential Moving Average (EMA)
                2 = Weighted Moving Average (WMA)
                3 = Smoothed Moving Average (SMMA)
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self
