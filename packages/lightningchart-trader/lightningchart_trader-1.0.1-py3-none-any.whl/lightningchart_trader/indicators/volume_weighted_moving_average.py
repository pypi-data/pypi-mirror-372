from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class VolumeWeightedMovingAverage(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=20):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addVolumeWeightedMovingAverage',
            {'traderID': trader.id, 'periodCount': period_count},
        )
