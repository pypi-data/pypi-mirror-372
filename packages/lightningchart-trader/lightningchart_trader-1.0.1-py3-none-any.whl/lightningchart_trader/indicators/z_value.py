from lightningchart_trader.indicators import SourceIndicator


class ZValue(SourceIndicator):
    def __init__(self, trader, period_count=20):
        super().__init__(trader)
        self.instance.send(self.id, 'addZValue', {'traderID': trader.id, 'periodCount': period_count})

    def set_line_color(self, color: str):
        """Sets the color of the Z-Value line.

        Args:
            color (str): The color of the line in hex format, e.g., '#FF0000' for red.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Z-Value line.

        Args:
            width (int | float): The width of the line.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_offset(self, offset: int | float):
        """Sets the offset of the Z-Value line.

        Args:
            offset (int | float): The offset to apply to the Z-Value.
        """
        self.instance.send(self.id, 'setOffset', {'offset': offset})
        return self

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of moving average used to calculate the Z-Value.

        Args:
            moving_average_type (int): The type of moving average to use.
            Typically, values represent different types of moving averages:
                0 = Simple Moving Average (SMA)
                1 = Exponential Moving Average (EMA)
                2 = Weighted Moving Average (WMA)
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self

    def set_period_count(self, period_count: int):
        """Sets the number of periods for calculating the Z-Value.

        Args:
            period_count (int): The number of periods to use in the calculation.
        """
        self.instance.send(self.id, 'setPeriodCount', {'count': period_count})
        return self

    def set_visible(self, visible: bool):
        """Sets the visibility of the Z-Value indicator.

        Args:
            visible (bool): Whether the indicator is visible or not.
        """
        self.instance.send(self.id, 'setVisible', {'visible': visible})
        return self
