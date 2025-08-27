from lightningchart_trader.indicators import LineIndicator


class AccumulationDistribution(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addAccumulationDistribution', {'traderID': trader.id})
