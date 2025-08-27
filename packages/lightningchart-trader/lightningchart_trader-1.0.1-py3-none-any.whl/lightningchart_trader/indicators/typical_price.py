from lightningchart_trader.indicators import LineIndicator


class TypicalPrice(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addTypicalPrice', {'traderID': trader.id})
