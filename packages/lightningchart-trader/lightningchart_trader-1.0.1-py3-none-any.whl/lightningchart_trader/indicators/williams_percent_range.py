from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class WilliamsPercentRange(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=14):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addWilliamsPercentRange',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_overbought_color(self, color: str):
        """Sets the color used for the overbought region in the indicator.

        Args:
            color (str): The color to be used for the overbought region, specified as a hex string (e.g., '#FF0000').
        """
        self.instance.send(self.id, 'setOverboughtColor', {'color': color})
        return self

    def set_oversold_and_overbought_ranges(self, oversold_range: int | float, overbought_range: int | float):
        """Sets the ranges for oversold and overbought levels.

        Args:
            oversold_range (int | float): The threshold value for the oversold range.
            overbought_range (int | float): The threshold value for the overbought range.
        """
        self.instance.send(
            self.id,
            'setOversoldAndOverboughtRanges',
            {'oversoldRange': oversold_range, 'overboughtRange': overbought_range},
        )
        return self

    def set_oversold_color(self, color: str):
        """Sets the color used for the oversold region in the indicator.

        Args:
            color (str): The color to be used for the oversold region, specified as a hex string (e.g., '#00FF00').
        """
        self.instance.send(self.id, 'setOversoldColor', {'color': color})
        return self
