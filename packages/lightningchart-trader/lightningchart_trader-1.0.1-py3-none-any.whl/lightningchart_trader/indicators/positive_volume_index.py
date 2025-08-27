from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class PositiveVolumeIndex(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addPositiveVolumeIndex', {'traderID': trader.id})
