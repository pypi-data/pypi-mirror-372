from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class DetrendedPriceOscillator(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addDetrendedPriceOscillator',
            {
                'traderID': trader.id,
            },
        )

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of moving average to be used for the Detrended Price Oscillator.

        Args:
            moving_average_type (int): The type of moving average (e.g., 0 for simple moving average, 1 for exponential moving average).
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self
