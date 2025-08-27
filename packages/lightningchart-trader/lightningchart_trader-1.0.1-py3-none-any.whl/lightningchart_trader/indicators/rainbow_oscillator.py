from lightningchart_trader.indicators import PeriodIndicator, SourceIndicator


class RainbowOscillator(PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addRainbowOscillator', {'traderID': trader.id})

    def set_fill_enabled(self, fill_enabled: bool):
        """Enables or disables fill for the Rainbow Oscillator.

        Args:
            fill_enabled (bool): Whether to enable or disable the fill.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self

    def set_line_width(self, width: int | float):
        """Sets the line width for the Rainbow Oscillator.

        Args:
            width (int | float): The width of the line.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_lookback_periods(self, lookback_periods: int):
        """Sets the number of lookback periods for the Rainbow Oscillator.

        Args:
            lookback_periods (int): The number of periods to look back.
        """
        self.instance.send(self.id, 'setLookbackPeriods', {'lookbackPeriods': lookback_periods})
        return self

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the moving average type for the Rainbow Oscillator.

        Args:
            moving_average_type (int): The type of moving average to apply.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self

    def set_oscillator_colors(self, color_up: str, color_down: str):
        """Sets the colors for the oscillator.

        Args:
            color_up (str): The color to use when the oscillator is moving up.
            color_down (str): The color to use when the oscillator is moving down.
        """
        self.instance.send(
            self.id,
            'setOscillatorColors',
            {'colorUp': color_up, 'colorDown': color_down},
        )
        return self

    def set_smoothing_levels(self, smoothing_levels: int):
        """Sets the number of smoothing levels for the Rainbow Oscillator.

        Args:
            smoothing_levels (int): The number of smoothing levels.
        """
        self.instance.send(self.id, 'setSmoothingLevels', {'smoothingLevels': smoothing_levels})
        return self
