from lightningchart_trader.indicators import LineIndicator


class OpenInterest(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addOpenInterest', {'traderID': trader.id})
