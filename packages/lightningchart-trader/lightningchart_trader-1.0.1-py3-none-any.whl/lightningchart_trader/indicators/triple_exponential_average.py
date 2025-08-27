from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class TripleExponentialAverage(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addTripleExponentialAverage', {'traderID': trader.id})

    def set_signal_color(self, color: str):
        """Sets the color for the signal line of the Triple Exponential Average indicator.

        Args:
            color (str): The color to be applied to the signal line in the indicator.
        """
        self.instance.send(self.id, 'setSignalColor', {'color': color})
        return self
