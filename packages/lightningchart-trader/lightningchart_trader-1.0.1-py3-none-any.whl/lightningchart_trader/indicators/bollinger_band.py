from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class BollingerBand(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=14):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addBollingerBand',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_fill_enabled(self, fill_enabled: bool):
        """Enables or disables the filling of the Bollinger Band area.

        Args:
            fill_enabled (bool): If True, fills the area between the upper and lower Bollinger Bands.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self

    def set_fill_color(self, color: str):
        """Sets the fill color of the area between the upper and lower Bollinger Bands.

        Args:
            color (str): A string representing the color to be used for the fill (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_standard_deviation_number(self, number: int):
        """Sets the number of standard deviations used to calculate the upper and lower bands.

        Args:
            number (int): The number of standard deviations to apply for the Bollinger Bands.
        """
        self.instance.send(self.id, 'setStandardDeviationNumber', {'standardDeviationNumber': number})
        return self
