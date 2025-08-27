from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class HistoricalVolatilityIndex(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addHistoricalVolatilityIndex', {'traderID': trader.id})

    def set_periods_per_year(self, count: int):
        """Sets the number of periods per year for the Historical Volatility Index calculation.

        Args:
            count (int): The number of periods per year (e.g., 252 for trading days in a year).
        """
        self.instance.send(self.id, 'setPeriodsPerYear', {'periodsPerYear': int(count)})
        return self

    def set_standard_deviations(self, deviations: int | float):
        """Sets the number of standard deviations for the Historical Volatility Index.

        Args:
            deviations (int | float): The number of standard deviations.
        """
        self.instance.send(self.id, 'setStandardDeviations', {'standardDeviations': deviations})
        return self

    def set_use_moving_average(self, use_moving_average: bool):
        """Enables or disables the use of a moving average for the Historical Volatility Index.

        Args:
            use_moving_average (bool): True to use a moving average, False otherwise.
        """
        self.instance.send(self.id, 'setUseMovingAverage', {'useMovingAverage': use_moving_average})
        return self
