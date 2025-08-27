from lightningchart_trader.indicators import IndicatorBase


class VolumeOscillator(IndicatorBase):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addVolumeOscillator', {'traderID': trader.id})

    def set_calculate_as_percentage(self, calculate_as_percentage: bool):
        """Sets whether to calculate the oscillator as a percentage.

        Args:
            calculate_as_percentage (bool): Whether to calculate the oscillator as a percentage.
        """
        self.instance.send(
            self.id,
            'setCalculateAsPercentage',
            {'calculateAsPercentage': calculate_as_percentage},
        )
        return self

    def set_histogram_color(self, histogram_color: str):
        """Sets the color of the histogram.

        Args:
            histogram_color (str): The color for the histogram.
        """
        self.instance.send(
            self.id,
            'setHistogramColorVolumeOscillator',
            {'histogramColor': histogram_color},
        )
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the oscillator line.

        Args:
            width (int | float): The width of the line.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_moving_average_signal(self, moving_average_type: int):
        """Sets the type of moving average used for the signal line.

        Args:
            moving_average_type (int): The type of the moving average.
        """
        self.instance.send(
            self.id,
            'setMovingAverageSignal',
            {'movingAverageType': moving_average_type},
        )
        return self

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of moving average for the oscillator.

        Args:
            moving_average_type (int): The type of the moving average.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self

    def set_period_counts(self, short_period_count: int, long_period_count: int, signal_period_count: int):
        """Sets the period counts for the oscillator and signal line.

        Args:
            short_period_count (int): The short period count.
            long_period_count (int): The long period count.
            signal_period_count (int): The signal period count.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsVolumeOscillator',
            {
                'shortPeriodCount': short_period_count,
                'longPeriodCount': long_period_count,
                'signalPeriodCount': signal_period_count,
            },
        )
        return self

    def set_signal_line_color(self, color: str):
        """Sets the color of the signal line.

        Args:
            color (str): The color for the signal line.
        """
        self.instance.send(self.id, 'setSignalLineColor', {'color': color})
        return self

    def set_vo_line_color(self, color: str):
        """Sets the color of the oscillator line.

        Args:
            color (str): The color for the oscillator line.
        """
        self.instance.send(self.id, 'setVOLineColor', {'color': color})
        return self
