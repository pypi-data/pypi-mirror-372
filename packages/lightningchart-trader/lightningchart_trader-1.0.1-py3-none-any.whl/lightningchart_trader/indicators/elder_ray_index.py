from lightningchart_trader.indicators import PeriodIndicator, SourceIndicator


class ElderRayIndex(PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count=13):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addElderRayIndex',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_bear_power_color(self, color: str):
        """Sets the color for the Bear Power line in the Elder Ray Index.

        Args:
            color (str): The color for the Bear Power line (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setBearPowerColor', {'color': color})
        return self

    def set_bull_power_color(self, color: str):
        """Sets the color for the Bull Power line in the Elder Ray Index.

        Args:
            color (str): The color for the Bull Power line (e.g., '#00FF00' for green).
        """
        self.instance.send(self.id, 'setBullPowerColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the line width for the Elder Ray Index.

        Args:
            width (int | float): The width of the lines (e.g., 2 for a thicker line).
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the moving average type used for calculating the Elder Ray Index.

        Args:
            moving_average_type (int): The type of moving average (e.g., 0 for Simple Moving Average, 1 for Exponential).
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self
