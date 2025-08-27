from lightningchart_trader.indicators import LineIndicator


class HighMinusLow(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addHighMinusLow', {'traderID': trader.id})
