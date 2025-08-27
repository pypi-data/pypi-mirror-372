from lightningchart_trader.indicators import PeriodIndicator


class RandomWalkIndex(PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addRandomWalkIndex', {'traderID': trader.id})

    def set_line_width(self, width: int | float):
        """Sets the line width for the Random Walk Index.

        Args:
            width (int | float): The width of the line to be displayed.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_rwi_high_color(self, color: str):
        """Sets the color for the high line of the Random Walk Index.

        Args:
            color (str): The color of the high line.
        """
        self.instance.send(self.id, 'setRWIHighColor', {'color': color})
        return self

    def set_rwi_low_color(self, color: str):
        """Sets the color for the low line of the Random Walk Index.

        Args:
            color (str): The color of the low line.
        """
        self.instance.send(self.id, 'setRWILowColor', {'color': color})
        return self
