from lightningchart_trader.indicators import LineIndicator


class WeightedClose(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addWeightedClose', {'traderID': trader.id})
