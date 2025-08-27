from lightningchart_trader.indicators import LineIndicator


class MedianPrice(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addMedianPrice', {'traderID': trader.id})
