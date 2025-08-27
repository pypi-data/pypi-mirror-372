from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class IntradayMomentumIndex(LineIndicator, PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addIntradayMomentumIndex', {'traderID': trader.id})

    def set_high_color(self, color: str):
        """Sets the color for the high threshold line of the Intraday Momentum Index.

        Args:
            color (str): The color for the high threshold line (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setHighColor', {'color': color})
        return self

    def set_low_color(self, color: str):
        """Sets the color for the low threshold line of the Intraday Momentum Index.

        Args:
            color (str): The color for the low threshold line.
        """
        self.instance.send(self.id, 'setLowColor', {'color': color})
        return self

    def set_thresholds(self, low_threshold: int | float, high_threshold: int | float):
        """Sets the thresholds for the Intraday Momentum Index.

        Args:
            low_threshold (int | float): The value for the low threshold.
            high_threshold (int | float): The value for the high threshold.
        """
        self.instance.send(
            self.id,
            'setThresholds',
            {'lowThreshold': low_threshold, 'highThreshold': high_threshold},
        )
        return self
