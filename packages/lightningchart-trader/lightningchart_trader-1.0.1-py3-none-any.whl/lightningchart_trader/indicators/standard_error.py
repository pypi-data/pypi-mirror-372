from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class StandardError(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=14):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addStandardError',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of moving average used in the Standard Error calculation.

        Args:
            moving_average_type (int): The type of moving average to apply.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self
