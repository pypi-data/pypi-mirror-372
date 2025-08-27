from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)


class CenterOfGravity(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addCenterOfGravity', {'traderID': trader.id})

    def set_show_signal(self, show_signal: bool):
        """Toggles the visibility of the signal line on the Center of Gravity indicator.

        Args:
            show_signal (bool): If True, the signal line will be displayed; otherwise, it will be hidden.
        """
        self.instance.send(self.id, 'setShowSignal', {'showSignal': show_signal})
        return self

    def set_signal_color(self, color: str):
        """Sets the color of the signal line in the Center of Gravity indicator.

        Args:
            color (str): A string representing the color for the signal line (e.g., '#00FF00' for green).
        """
        self.instance.send(self.id, 'setSignalColor', {'color': color})
        return self

    def set_signal_period_count(self, count: int):
        """Defines the number of periods used for calculating the signal line.

        Args:
            count (int): The number of periods for the signal calculation.
        """
        self.instance.send(self.id, 'setSignalPeriodCount', {'count': count})
        return self
