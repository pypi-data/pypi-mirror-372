from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class PrimeNumberOscillator(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addPrimeNumberOscillator', {'traderID': trader.id})
