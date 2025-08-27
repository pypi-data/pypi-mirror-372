from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class PrimeNumberBands(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addPrimeNumberBands', {'traderID': trader.id})

    def set_fill_color(self, color: str):
        """Sets the fill color for the Prime Number Bands.

        Args:
            color (str): The color to set for the fill, in hex or standard color string format.
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_fill_enabled(self, fill_enabled: bool):
        """Enables or disables the fill for the Prime Number Bands.

        Args:
            fill_enabled (bool): A boolean to enable (True) or disable (False) the fill for the bands.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self
