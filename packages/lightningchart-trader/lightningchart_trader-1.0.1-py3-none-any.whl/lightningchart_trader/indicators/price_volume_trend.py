from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class PriceVolumeTrend(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addPriceVolumeTrend', {'traderID': trader.id})
