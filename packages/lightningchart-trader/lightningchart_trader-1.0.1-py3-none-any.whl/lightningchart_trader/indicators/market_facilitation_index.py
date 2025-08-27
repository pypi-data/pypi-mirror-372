from lightningchart_trader.indicators import IndicatorBase


class MarketFacilitationIndex(IndicatorBase):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addMarketFacilitationIndex', {'traderID': trader.id})
