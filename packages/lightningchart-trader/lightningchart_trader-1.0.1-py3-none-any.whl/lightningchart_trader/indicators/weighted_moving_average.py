from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class WeightedMovingAverage(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=14):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addWeightedMovingAverage',
            {'traderID': trader.id, 'periodCount': period_count},
        )
