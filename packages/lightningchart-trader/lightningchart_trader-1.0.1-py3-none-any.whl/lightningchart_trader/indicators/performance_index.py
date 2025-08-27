from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class PerformanceIndex(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addPerformanceIndex', {'traderID': trader.id})
