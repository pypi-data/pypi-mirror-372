from lightningchart_trader.indicators import PeriodIndicator


class SuperTrend(PeriodIndicator):
    def __init__(self, trader, period_count: int = 10):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addSuperTrend',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_fill_enabled(self, enabled: bool):
        """Enables or disables the fill area for the SuperTrend indicator.

        Args:
            enabled (bool): True to enable the fill, False to disable it.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': enabled})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the SuperTrend line.

        Args:
            width (int | float): The width of the line in pixels.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_lower_color(self, color: str):
        """Sets the color for the lower part of the SuperTrend indicator.

        Args:
            color (str): The color for the lower trend line.
        """
        self.instance.send(self.id, 'setLowerColor', {'color': color})
        return self

    def set_multiplier(self, multiplier: float):
        """Sets the multiplier for the SuperTrend calculation.

        Args:
            multiplier (float): The multiplier used to calculate the SuperTrend levels.
        """
        self.instance.send(self.id, 'setMultiplierSuperTrend', {'Multiplier': multiplier})
        return self

    def set_upper_color(self, color: str):
        """Sets the color for the upper part of the SuperTrend indicator.

        Args:
            color (str): The color for the upper trend line.
        """
        self.instance.send(self.id, 'setUpperColor', {'color': color})
        return self
