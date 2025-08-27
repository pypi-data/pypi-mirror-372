from lightningchart_trader.indicators import IndicatorBase


class KlingerVolumeOscillator(IndicatorBase):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addKlingerVolumeOscillator', {'traderID': trader.id})

    def set_histogram_color(self, color: str):
        """Sets the histogram color for the Klinger Volume Oscillator.

        Args:
            color (str): The color to set for the histogram (e.g., '#00FF00' for green).
        """
        self.instance.send(self.id, 'setHistogramColorKlingerVolumeOscillator', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the line width for the Klinger Volume Oscillator.

        Args:
            width (int | float): The width of the oscillator lines.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_moving_average_signal(self, moving_average_type: int):
        """Sets the moving average signal type for the Klinger Volume Oscillator.

        Args:
            moving_average_type (int): The type of moving average used for the signal line.
        """
        self.instance.send(
            self.id,
            'setMovingAverageSignal',
            {'movingAverageType': moving_average_type},
        )
        return self

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the moving average type for the Klinger Volume Oscillator.

        Args:
            moving_average_type (int): The type of moving average used in the calculation of the oscillator.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self

    def set_period_counts(self, short_period_count: int, long_period_count: int, signal_period_count: int):
        """Sets the period counts for the Klinger Volume Oscillator.

        Args:
            short_period_count (int): The number of periods for the short moving average.
            long_period_count (int): The number of periods for the long moving average.
            signal_period_count (int): The number of periods for the signal line moving average.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsKlingerVolumeOscillator',
            {
                'shortPeriodCount': short_period_count,
                'longPeriodCount': long_period_count,
                'signalPeriodCount': signal_period_count,
            },
        )
        return self

    def set_signal_line_color(self, color: str):
        """Sets the color of the signal line for the Klinger Volume Oscillator.

        Args:
            color (str): The color to set for the signal line (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setSignalLineColor', {'color': color})
        return self

    def set_vo_line_color(self, color: str):
        """Sets the color of the volume oscillator line.

        Args:
            color (str): The color to set for the volume oscillator line (e.g., '#0000FF' for blue).
        """
        self.instance.send(self.id, 'setKVOLineColor', {'color': color})
        return self
