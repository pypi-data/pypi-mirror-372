from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class MoneyFlowIndex(LineIndicator, PeriodIndicator):
    def __init__(self, trader, period_count=14):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addMoneyFlowIndex',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_overbought_color(self, color: str):
        """Sets the color for the overbought line in the Money Flow Index indicator.

        Args:
            color (str): The color to set for the overbought line.
        """
        self.instance.send(self.id, 'setOverboughtColor', {'color': color})
        return self

    def set_oversold_and_overbought_ranges(self, oversold: int, overbought: int):
        """Sets the oversold and overbought ranges for the Money Flow Index indicator.

        Args:
            oversold (int): The value to define the oversold threshold.
            overbought (int): The value to define the overbought threshold.
        """
        self.instance.send(
            self.id,
            'setOversoldAndOverboughtRanges',
            {'oversoldRange': oversold, 'overboughtRange': overbought},
        )
        return self

    def set_oversold_color(self, color: str):
        """Sets the color for the oversold line in the Money Flow Index indicator.

        Args:
            color (str): The color to set for the oversold line.
        """
        self.instance.send(self.id, 'setOversoldColor', {'color': color})
        return self
