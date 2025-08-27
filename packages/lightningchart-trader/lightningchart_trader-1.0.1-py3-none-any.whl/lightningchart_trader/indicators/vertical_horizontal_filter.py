from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class VerticalHorizontalFilter(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=28):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addVerticalHorizontalFilter',
            {'traderID': trader.id, 'periodCount': period_count},
        )
