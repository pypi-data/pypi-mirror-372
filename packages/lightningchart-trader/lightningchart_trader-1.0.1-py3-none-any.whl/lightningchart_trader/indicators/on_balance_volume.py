from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class OnBalanceVolume(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addOnBalanceVolume', {'traderID': trader.id})
