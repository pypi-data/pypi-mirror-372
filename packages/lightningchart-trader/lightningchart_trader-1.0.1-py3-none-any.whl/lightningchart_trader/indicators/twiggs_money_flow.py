from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class TwiggsMoneyFlow(LineIndicator, PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addTwiggsMoneyFlow', {'traderID': trader.id})
