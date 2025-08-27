from lightningchart_trader.indicators import SourceIndicator


class MovingAverageConvergenceDivergence(SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addMovingAverageConvergenceDivergence', {'traderID': trader.id})

    def set_histogram_colors(
        self,
        positive_strong_color: str,
        positive_weak_color: str,
        negative_strong_color: str,
        negative_weak_color: str,
    ):
        """Sets the colors for the MACD histogram bars.

        Args:
            positive_strong_color (str): Color for the strong positive values in the histogram.
            positive_weak_color (str): Color for the weak positive values in the histogram.
            negative_strong_color (str): Color for the strong negative values in the histogram.
            negative_weak_color (str): Color for the weak negative values in the histogram.
        """
        self.instance.send(
            self.id,
            'setHistogramColorsMACD',
            {
                'positiveStrongColor': positive_strong_color,
                'positiveWeakColor': positive_weak_color,
                'negativeStrongColor': negative_strong_color,
                'negativeWeakColor': negative_weak_color,
            },
        )
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the MACD line.

        Args:
            width (int | float): Width of the MACD line.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_macd_line_color(self, color: str):
        """Sets the color of the MACD line.

        Args:
            color (str): Color to be set for the MACD line.
        """
        self.instance.send(self.id, 'setMACDLineColor', {'color': color})
        return self

    def set_period_counts(self, long_period_count: int, short_period_count: int, signal_period_count: int):
        """Sets the period counts for the MACD indicator.

        Args:
            long_period_count (int): Number of periods for the long-term moving average.
            short_period_count (int): Number of periods for the short-term moving average.
            signal_period_count (int): Number of periods for the signal moving average.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsMACD',
            {
                'longPeriodCount': long_period_count,
                'shortPeriodCount': short_period_count,
                'signalPeriodCount': signal_period_count,
            },
        )
        return self

    def set_signal_line_color(self, color: str):
        """Sets the color of the signal line.

        Args:
            color (str): Color to be set for the signal line.
        """
        self.instance.send(self.id, 'setSignalLineColor', {'color': color})
        return self
