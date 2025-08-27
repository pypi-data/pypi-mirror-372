from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class StandardDeviation(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=20):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addStandardDeviation',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of moving average used in the Standard Deviation calculation.

        Args:
            moving_average_type (int): The type of moving average to apply, represented as an integer
            corresponding to different methods of calculation.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self
