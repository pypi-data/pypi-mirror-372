from lightningchart_trader.indicators import IndicatorBase


class AwesomeOscillator(IndicatorBase):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addAwesomeOscillator', {'traderID': trader.id})

    def set_bar_colors(self, color_up: str, color_down: str):
        """Sets the colors of the bars.

        Args:
            color_up (str): The color of the bar, when its value is higher than the previous bar.
            color_down (str): The color of the bar, when its value is lower than the previous bar.
        """
        self.instance.send(
            self.id,
            'setBarColorsAwesome',
            {'colorUp': color_up, 'colorDown': color_down},
        )
        return self

    def set_period_counts(self, short_periods: int, long_periods: int):
        """Sets the number of short-term and long-term time periods used to calculate the indicator.

        Args:
            short_periods (int): Short-term period count.
            long_periods (int): Long-term period count.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsAwesome',
            {'shortPeriods': short_periods, 'longPeriods': long_periods},
        )
        return self
