from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class VariableMovingAverage(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=9):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addVariableMovingAverage',
            {'traderID': trader.id, 'periodCount': period_count},
        )
