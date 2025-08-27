from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class RelativeStrengthIndex(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=14):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addRelativeStrengthIndex',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_high_color(self, color: str):
        """Sets the color for the overbought (high) threshold line.

        Args:
            color (str): The color for the high threshold line (overbought).
        """
        self.instance.send(self.id, 'setHighColor', {'color': color})
        return self

    def set_low_color(self, color: str):
        """Sets the color for the oversold (low) threshold line.

        Args:
            color (str): The color for the low threshold line (oversold).
        """
        self.instance.send(self.id, 'setLowColor', {'color': color})
        return self

    def set_thresholds(self, low_threshold: int | float, high_threshold: int | float):
        """Sets the low and high threshold levels for the RSI indicator.

        Args:
            low_threshold (int | float): The value for the oversold threshold.
            high_threshold (int | float): The value for the overbought threshold.
        """
        self.instance.send(
            self.id,
            'setThresholds',
            {'lowThreshold': low_threshold, 'highThreshold': high_threshold},
        )
        return self
