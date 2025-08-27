from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class Kurtosis(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addKurtosis', {'traderID': trader.id})

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the moving average type for the Kurtosis indicator.

        Args:
            moving_average_type (int): The type of moving average used in the Kurtosis calculation.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self

    def set_show_as_excess(self, show_as_excess: bool):
        """Determines whether the Kurtosis indicator should be shown as excess kurtosis.

        Args:
            show_as_excess (bool): Set to True to display excess kurtosis, or False to display regular kurtosis.
        """
        self.instance.send(self.id, 'setShowAsExcess', {'showAsExcess': show_as_excess})
        return self
