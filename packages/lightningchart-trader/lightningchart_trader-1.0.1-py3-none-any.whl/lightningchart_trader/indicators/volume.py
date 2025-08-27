from lightningchart_trader.indicators import IndicatorBase


class Volume(IndicatorBase):
    def __init__(
        self,
        trader,
        add_as_overlay: bool = True,
        two_colored_bars: bool = True,
        bar_color: str = None,
        offset: int = 0,
    ):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addVolume',
            {
                'traderID': trader.id,
                'addAsOverlay': add_as_overlay,
                'twoColoredBars': two_colored_bars,
                'barColor': bar_color,
                'offset': offset,
            },
        )

    def set_bar_color(self, color: str):
        """Sets the color of the volume bars.

        Args:
            color (str): The color to use for the volume bars.
        """
        self.instance.send(self.id, 'setBarColor', {'color': color})
        return self

    def set_show_as_overlay(self, show_as_overlay: bool):
        """Sets whether the volume indicator is displayed as an overlay.

        Args:
            show_as_overlay (bool): Whether to show the volume bars as an overlay on the price chart.
        """
        self.instance.send(self.id, 'setShowAsOverlay', {'showAsOverlay': show_as_overlay})
        return self

    def set_two_colored_bars(self, use_two_colors: bool):
        """Enables or disables two-colored volume bars.

        Args:
            use_two_colors (bool): Whether to use two colors for volume bars (e.g., for up and down movements).
        """
        self.instance.send(self.id, 'setTwoColoredBars', {'useTwoColors': use_two_colors})
        return self
