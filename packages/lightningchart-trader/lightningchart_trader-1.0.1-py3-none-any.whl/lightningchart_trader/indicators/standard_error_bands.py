from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class StandardErrorBands(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addStandardErrorBands', {'traderID': trader.id})

    def set_fill_color(self, color: str):
        """Sets the fill color for the standard error bands.

        Args:
            color (str): The color code for the fill.
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_fill_enabled(self, fill_enabled: bool):
        """Enables or disables the fill for the standard error bands.

        Args:
            fill_enabled (bool): Boolean value to enable or disable the fill.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of moving average used in the standard error bands calculation.

        Args:
            moving_average_type (int): The type of moving average to apply.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self

    def set_multiplier(self, multiplier: int | float):
        """Sets the multiplier for the standard error bands.

        Args:
            multiplier (int | float): The multiplier value to adjust the band width.
        """
        self.instance.send(self.id, 'setMultiplierStandardErrorBands', {'multiplier': multiplier})
        return self
