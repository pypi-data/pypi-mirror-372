from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class EaseOfMovement(LineIndicator, PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addEaseOfMovement', {'traderID': trader.id})

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the moving average type for the Ease of Movement indicator.

        Args:
            moving_average_type (int): The type of moving average to be applied (e.g., 0 for Simple Moving Average, 1 for Exponential Moving Average).
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self

    def set_scale(self, scale: int | float):
        """Sets the scale for the Ease of Movement indicator.

        Args:
            scale (int | float): The scale factor to adjust the indicator's sensitivity. It can be an integer or float value.
        """
        self.instance.send(self.id, 'setScale', {'scale': scale})
        return self
