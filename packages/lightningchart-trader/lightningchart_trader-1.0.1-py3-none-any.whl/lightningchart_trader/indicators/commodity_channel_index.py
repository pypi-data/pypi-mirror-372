from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class CommodityChannelIndex(LineIndicator, PeriodIndicator):
    def __init__(self, trader, period_count=20):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addCommodityChannelIndex',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_fill_color(self, color: str):
        """Sets the fill color for the Commodity Channel Index (CCI) visualization.

        Args:
            color (str): The fill color in hexadecimal or RGB format.
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_overbought_and_sold_levels(self, overbought_level: int | float, oversold_level: int | float):
        """Sets the overbought and oversold levels for the Commodity Channel Index (CCI) indicator.

        Args:
            overbought_level (int | float): The overbought threshold level.
            oversold_level (int | float): The oversold threshold level.
        """
        self.instance.send(
            self.id,
            'setOverboughtAndSoldLevels',
            {'overboughtLevel': overbought_level, 'oversoldLevel': oversold_level},
        )
        return self
