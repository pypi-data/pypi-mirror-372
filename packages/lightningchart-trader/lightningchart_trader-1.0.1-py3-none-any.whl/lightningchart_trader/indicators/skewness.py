from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class Skewness(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addSkewness', {'traderID': trader.id})

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the moving average type used in the Skewness calculation.

        Args:
            moving_average_type (int): The type of moving average to use. This is typically represented as an integer
            corresponding to different moving average calculation methods (e.g., simple, exponential, weighted).
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self
