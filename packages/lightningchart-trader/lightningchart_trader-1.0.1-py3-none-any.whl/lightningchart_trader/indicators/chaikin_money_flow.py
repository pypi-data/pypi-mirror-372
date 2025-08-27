from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class ChaikinMoneyFlow(LineIndicator, PeriodIndicator):
    def __init__(self, trader, period_count=21):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addChaikinMoneyFlow',
            {'traderID': trader.id, 'periodCount': period_count},
        )
