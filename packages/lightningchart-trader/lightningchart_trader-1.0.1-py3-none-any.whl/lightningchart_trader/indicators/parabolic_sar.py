from lightningchart_trader.indicators import IndicatorBase


class ParabolicSAR(IndicatorBase):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addParabolicSAR', {'traderID': trader.id})

    def set_acceleration_factor(self, factor: int | float):
        """Sets the acceleration factor used in the Parabolic SAR calculation.

        Args:
            factor (float): The acceleration factor value (e.g., 0.02). This controls how quickly the indicator reacts to price changes.
        """
        self.instance.send(self.id, 'setAccelerationFactor', {'accelerationFactor': factor})
        return self

    def set_maximum_acceleration_factor(self, maximum: int | float):
        """Sets the maximum acceleration factor for the Parabolic SAR.

        Args:
            maximum (float): The maximum acceleration factor (e.g., 0.2). This limits the sensitivity of the indicator as it moves closer to the price.
        """
        self.instance.send(self.id, 'setMaximumAccelerationFactor', {'maximum': maximum})
        return self

    def set_point_color(self, color: str):
        """Sets the color of the points plotted by the Parabolic SAR.

        Args:
            color (str): The color of the points (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setPointColor', {'color': color})
        return self

    def set_point_size(self, size: int | float):
        """Sets the size of the points in the Parabolic SAR chart.

        Args:
            size (int | float): The size of the points (e.g., 2.5).
        """
        self.instance.send(self.id, 'setPointSize', {'size': size})
        return self
