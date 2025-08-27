from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class VIDYA(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=9):
        super().__init__(trader)
        self.instance.send(self.id, 'addVIDYA', {'traderID': trader.id, 'periodCount': period_count})

    def set_standard_deviation_period_counts(self, short_period_count: int, long_period_count: int):
        """Sets the period counts for calculating the standard deviation for VIDYA.

        Args:
            short_period_count (int): The short period count for standard deviation.
            long_period_count (int): The long period count for standard deviation.
        """
        self.instance.send(
            self.id,
            'setStandardDeviationPeriodCounts',
            {
                'shortPeriodCount': short_period_count,
                'longPeriodCount': long_period_count,
            },
        )
        return self
