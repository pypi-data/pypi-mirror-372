from lightningchart_trader.indicators import SourceIndicator


class PercentagePriceOscillator(SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addPercentagePriceOscillator', {'traderID': trader.id})

    def set_histogram_color(self, color: str):
        """Sets the color of the histogram bars in the Percentage Price Oscillator (PPO) chart.

        Args:
            color (str): The color to set for the histogram bars (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setHistogramColorPercentagePrice', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the PPO line.

        Args:
            width (int | float): The width of the PPO line (e.g., 2.5).
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_ppo_line_color(self, color: str):
        """Sets the color of the Percentage Price Oscillator line.

        Args:
            color (str): The color to set for the PPO line (e.g., '#00FF00' for green).
        """
        self.instance.send(self.id, 'setPPOLineColor', {'color': color})
        return self

    def set_period_counts(self, long_period: int, short_period: int, signal_period: int):
        """Sets the period counts for the long, short, and signal lines of the PPO.

        Args:
            long_period (int): The period for the long line.
            short_period (int): The period for the short line.
            signal_period (int): The period for the signal line.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsPercentagePrice',
            {
                'longPeriodCount': long_period,
                'shortPeriodCount': short_period,
                'signalPeriodCount': signal_period,
            },
        )
        return self

    def set_signal_line_color(self, color: str):
        """Sets the color of the signal line in the PPO chart.

        Args:
            color (str): The color to set for the signal line (e.g., '#0000FF' for blue).
        """
        self.instance.send(self.id, 'setSignalLineColor', {'color': color})
        return self
