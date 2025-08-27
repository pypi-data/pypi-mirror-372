from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class EhlerFisherTransform(LineIndicator, PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addEhlerFisherTransform', {'traderID': trader.id})

    def set_signal_color(self, color: str):
        """Sets the color for the signal line in the Ehler Fisher Transform indicator.

        Args:
            color (str): The color for the signal line (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setSignalColor', {'color': color})
        return self

    def set_signal_period_count(self, count: int):
        """Sets the number of periods used for calculating the signal line.

        Args:
            count (int): The number of periods to use for the signal calculation.
        """
        self.instance.send(self.id, 'setSignalPeriodCount', {'count': count})
        return self

    def set_smoothing_period_counts(self, raw_smoothing_periods: int, fisher_smoothing_periods: int):
        """Sets the smoothing period counts for the Ehler Fisher Transform.

        Args:
            raw_smoothing_periods (int): The number of periods used for raw data smoothing.
            fisher_smoothing_periods (int): The number of periods used for Fisher Transform smoothing.
        """
        self.instance.send(
            self.id,
            'setSmoothingPeriodCounts',
            {
                'rawSmoothingPeriods': raw_smoothing_periods,
                'fisherSmoothingPeriods': fisher_smoothing_periods,
            },
        )
        return self
