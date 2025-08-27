from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class SQNTrend(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addSQNTrend', {'traderID': trader.id})

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of moving average used in the SQN Trend calculation.

        Args:
            moving_average_type (int): The type of moving average to use, typically represented as an integer
            corresponding to different moving average calculation methods.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self
