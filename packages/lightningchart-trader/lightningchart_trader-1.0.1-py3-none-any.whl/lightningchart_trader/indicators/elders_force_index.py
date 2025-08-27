from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class EldersForceIndex(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=13):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addEldersForceIndex',
            {'traderID': trader.id, 'periodCount': period_count},
        )
