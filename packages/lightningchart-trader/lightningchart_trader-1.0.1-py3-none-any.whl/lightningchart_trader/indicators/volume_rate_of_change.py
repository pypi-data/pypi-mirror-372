from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class VolumeRateOfChange(LineIndicator, PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addVolumeRateOfChange', {'traderID': trader.id})
