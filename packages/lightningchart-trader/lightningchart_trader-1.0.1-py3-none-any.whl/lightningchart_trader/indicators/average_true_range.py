from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class AverageTrueRange(LineIndicator, PeriodIndicator):
    def __init__(self, trader, period_count=14):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addAverageTrueRange',
            {'traderID': trader.id, 'periodCount': period_count},
        )
