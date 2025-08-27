from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class MovingAverageEnvelopes(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader, period_count: int):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addMovingAverageEnvelopes',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_fill_color(self, color: str):
        """Sets the fill color for the area between the moving average envelopes.

        Args:
            color (str): The color to fill the area between the envelopes (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_fill_enabled(self, fill_enabled: bool):
        """Enables or disables the filling of the area between the moving average envelopes.

        Args:
            fill_enabled (bool): If True, fills the area between the envelopes; if False, no fill is applied.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of moving average used to calculate the envelopes.

        Args:
            moving_average_type (int): The type of moving average to use (e.g., 0 for Simple Moving Average, 1 for Exponential Moving Average).
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self

    def set_percentage(self, percentage: int | float):
        """Sets the percentage distance from the moving average to create the upper and lower envelopes.

        Args:
            percentage (int | float): The percentage value used to calculate the envelopes (e.g., 2.5 for 2.5%).
        """
        self.instance.send(self.id, 'setPercentage', {'percentage': percentage})
        return self
