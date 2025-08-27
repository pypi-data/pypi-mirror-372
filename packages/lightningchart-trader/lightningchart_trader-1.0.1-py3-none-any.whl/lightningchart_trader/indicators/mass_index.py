from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class MassIndex(LineIndicator, PeriodIndicator):
    def __init__(self, trader, period_count=25):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addMassIndex',
            {'traderID': trader.id, 'periodCount': period_count},
        )
