from lightningchart_trader.indicators import PeriodIndicator


class FractalChaosBands(PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addFractalChaosBands', {'traderID': trader.id})

    def set_fill_color(self, color: str):
        """Sets the fill color for the Fractal Chaos Bands.

        Args:
            color (str): The fill color (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_fill_enabled(self, fill_enabled: bool):
        """Enables or disables the fill for the Fractal Chaos Bands.

        Args:
            fill_enabled (bool): Whether the fill is enabled (True or False).
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the lines for the Fractal Chaos Bands.

        Args:
            width (int | float): The width of the lines (e.g., 1.5 for 1.5px width).
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_lower_line_color(self, color: str):
        """Sets the color of the lower line in the Fractal Chaos Bands.

        Args:
            color (str): The color of the lower line (e.g., '#00FF00' for green).
        """
        self.instance.send(self.id, 'setLowerLineColor', {'color': color})
        return self

    def set_upper_line_color(self, color: str):
        """Sets the color of the upper line in the Fractal Chaos Bands.

        Args:
            color (str): The color of the upper line (e.g., '#0000FF' for blue).
        """
        self.instance.send(self.id, 'setUpperLineColor', {'color': color})
        return self
