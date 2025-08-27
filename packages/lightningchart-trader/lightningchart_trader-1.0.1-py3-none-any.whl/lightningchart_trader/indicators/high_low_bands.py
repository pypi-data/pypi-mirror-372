from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class HighLowBands(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addHighLowBands', {'traderID': trader.id})

    def set_fill_color(self, color: str):
        """Sets the fill color for the HighLowBands.

        Args:
            color (str): The fill color (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_fill_enabled(self, fill_enabled: bool):
        """Enables or disables the fill for the HighLowBands.

        Args:
            fill_enabled (bool): Whether the fill is enabled (True or False).
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self

    def set_percentage(self, percentage: int | float):
        """Sets the percentage for the HighLowBands.

        Args:
            percentage (int | float): The percentage used in the HighLowBands calculation (e.g., 10 for 10%).
        """
        self.instance.send(self.id, 'setPercentage', {'percentage': percentage})
        return self
