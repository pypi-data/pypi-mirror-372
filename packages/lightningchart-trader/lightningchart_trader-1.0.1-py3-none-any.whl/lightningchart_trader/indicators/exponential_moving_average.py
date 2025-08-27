from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class ExponentialMovingAverage(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=14):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addExponentialMovingAverage',
            {'traderID': trader.id, 'periodCount': period_count},
        )
