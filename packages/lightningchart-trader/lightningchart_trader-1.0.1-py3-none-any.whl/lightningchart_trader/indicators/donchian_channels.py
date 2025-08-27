from lightningchart_trader.indicators import PeriodIndicator


class DonchianChannels(PeriodIndicator):
    def __init__(self, trader, period_count=20):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addDonchianChannels',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_fill_color(self, color: str):
        """Sets the fill color for the Donchian Channels.

        Args:
            color (str): The color to use for filling the channel area.
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_fill_enabled(self, fill_enabled: bool):
        """Enables or disables the fill inside the Donchian Channels.

        Args:
            fill_enabled (bool): If True, the area between the lines will be filled with color.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Donchian Channels' lines.

        Args:
            width (int | float): The width of the lines (can be an integer or float value).
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_lower_line_color(self, color: str):
        """Sets the color of the lower line in the Donchian Channels.

        Args:
            color (str): The color to use for the lower line.
        """
        self.instance.send(self.id, 'setLowerLineColor', {'color': color})
        return self

    def set_mid_line_color(self, color: str):
        """Sets the color of the middle line in the Donchian Channels.

        Args:
            color (str): The color to use for the middle line.
        """
        self.instance.send(self.id, 'setMidLineColor', {'color': color})
        return self

    def set_upper_line_color(self, color: str):
        """Sets the color of the upper line in the Donchian Channels.

        Args:
            color (str): The color to use for the upper line.
        """
        self.instance.send(self.id, 'setUpperLineColor', {'color': color})
        return self
