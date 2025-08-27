from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class TimeSeriesMovingAverage(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=25):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addTimeSeriesMovingAverage',
            {'traderID': trader.id, 'periodCount': period_count},
        )
