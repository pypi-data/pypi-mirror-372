from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class MomentumOscillator(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=10):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addMomentumOscillator',
            {'traderID': trader.id, 'periodCount': period_count},
        )
