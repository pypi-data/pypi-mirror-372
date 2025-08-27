from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class TrueStrengthIndex(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addTrueStrengthIndex', {'traderID': trader.id})

    def set_moving_average_types(self, first_smooth_ma: int, double_smooth_ma: int, signal_ma: int):
        """Sets the types of moving averages for different smoothing stages.

        Args:
            first_smooth_ma (int): The moving average type for the first smoothing.
            double_smooth_ma (int): The moving average type for the double smoothing.
            signal_ma (int): The moving average type for the signal line.
        """
        self.instance.send(
            self.id,
            'setMovingAverageTypesTrueStrength',
            {
                'firstSmoothMovingAverage': first_smooth_ma,
                'doubleSmoothMovingAverage': double_smooth_ma,
                'signalMovingAverage': signal_ma,
            },
        )
        return self

    def set_period_counts(
        self,
        price_period_count: int,
        first_smooth_periods: int,
        double_smooth_periods: int,
        signal_periods: int,
    ):
        """Sets the period counts for the different stages of the True Strength Index.

        Args:
            price_period_count (int): The period count for the price.
            first_smooth_periods (int): The period count for the first smoothing.
            double_smooth_periods (int): The period count for the double smoothing.
            signal_periods (int): The period count for the signal line.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsTrueStrength',
            {
                'pricePeriodCount': price_period_count,
                'firstSmoothPeriods': first_smooth_periods,
                'doubleSmoothPeriods': double_smooth_periods,
                'signalPeriods': signal_periods,
            },
        )
        return self

    def set_signal_color(self, color: str):
        """Sets the color of the signal line for the True Strength Index.

        Args:
            color (str): The color to set for the signal line.
        """
        self.instance.send(self.id, 'setSignalColor', {'color': color})
        return self
