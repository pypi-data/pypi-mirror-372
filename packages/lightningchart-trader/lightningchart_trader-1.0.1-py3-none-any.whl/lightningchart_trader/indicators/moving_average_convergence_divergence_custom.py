from lightningchart_trader.indicators import SourceIndicator


class MovingAverageConvergenceDivergenceCustom(SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addMovingAverageConvergenceDivergenceCustom',
            {'traderID': trader.id},
        )

    def set_histogram_colors(
        self,
        positive_strong_color: str,
        positive_weak_color: str,
        negative_strong_color: str,
        negative_weak_color: str,
    ):
        """Sets the colors for the histogram bars in the custom MACD indicator.

        Args:
            positive_strong_color (str): The color for strong positive values.
            positive_weak_color (str): The color for weak positive values.
            negative_strong_color (str): The color for strong negative values.
            negative_weak_color (str): The color for weak negative values.
        """
        self.instance.send(
            self.id,
            'setHistogramColorsMACDCustom',
            {
                'positiveStrongColor': positive_strong_color,
                'positiveWeakColor': positive_weak_color,
                'negativeStrongColor': negative_strong_color,
                'negativeWeakColor': negative_weak_color,
            },
        )
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the lines in the MACD custom indicator.

        Args:
            width (int | float): The width to set for the line.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_macd_line_color(self, color: str):
        """Sets the color of the MACD line in the custom MACD indicator.

        Args:
            color (str): The color to set for the MACD line.
        """
        self.instance.send(self.id, 'setMACDLineColor', {'color': color})
        return self

    def set_moving_average_types(
        self,
        short_moving_average: int,
        long_moving_average: int,
        signal_moving_average: int,
    ):
        """Sets the types of moving averages for the MACD custom indicator.

        Args:
            short_moving_average (int): The type of short-term moving average.
            long_moving_average (int): The type of long-term moving average.
            signal_moving_average (int): The type of signal moving average.
        """
        self.instance.send(
            self.id,
            'setMovingAverageTypesMACDCustom',
            {
                'shortMovingAverage': short_moving_average,
                'longMovingAverage': long_moving_average,
                'signalMovingAverage': signal_moving_average,
            },
        )
        return self

    def set_period_counts(self, long_period_count: int, short_period_count: int, signal_period_count: int):
        """Sets the period counts for the long-term, short-term, and signal moving averages in the MACD custom indicator.

        Args:
            long_period_count (int): The period count for the long-term moving average.
            short_period_count (int): The period count for the short-term moving average.
            signal_period_count (int): The period count for the signal moving average.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsMACDCustom',
            {
                'longPeriodCount': long_period_count,
                'shortPeriodCount': short_period_count,
                'signalPeriodCount': signal_period_count,
            },
        )
        return self

    def set_signal_line_color(self, color: str):
        """Sets the color of the signal line in the custom MACD indicator.

        Args:
            color (str): The color to set for the signal line.
        """
        self.instance.send(self.id, 'setSignalLineColor', {'color': color})
        return self
