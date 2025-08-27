from lightningchart_trader.indicators import IndicatorBase


class StochasticMomentumIndex(IndicatorBase):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addStochasticMomentumIndex', {'traderID': trader.id})

    def set_line_width(self, width: int | float):
        """Sets the width of the line in the Stochastic Momentum Index.

        Args:
            width (int | float): The width of the line.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_moving_average_line_color(self, color: str):
        """Sets the color of the moving average line.

        Args:
            color (str): The color of the moving average line.
        """
        self.instance.send(self.id, 'setMovingAverageLineColor', {'color': color})
        return self

    def set_moving_average_types(self, oscillator_smoothing_average: int, ma_moving_average: int):
        """Sets the types of moving averages used in the Stochastic Momentum Index.

        Args:
            oscillator_smoothing_average (int): Type of smoothing moving average.
            ma_moving_average (int): Type of moving average for the MA line.
        """
        self.instance.send(
            self.id,
            'setMovingAverageTypesStochasticMomentum',
            {
                'oscillatorSmoothingAverage': oscillator_smoothing_average,
                'maMovingAverage': ma_moving_average,
            },
        )
        return self

    def set_overbought_color(self, color: str):
        """Sets the color for the overbought threshold.

        Args:
            color (str): The color representing the overbought threshold.
        """
        self.instance.send(self.id, 'setOverboughtColor', {'color': color})
        return self

    def set_oversold_and_overbought_ranges(self, oversold_range: int | float, overbought_range: int | float):
        """Sets the ranges for oversold and overbought levels.

        Args:
            oversold_range (int | float): The value of the oversold threshold.
            overbought_range (int | float): The value of the overbought threshold.
        """
        self.instance.send(
            self.id,
            'setOversoldAndOverboughtRanges',
            {'oversoldRange': oversold_range, 'overboughtRange': overbought_range},
        )
        return self

    def set_oversold_color(self, color: str):
        """Sets the color for the oversold threshold.

        Args:
            color (str): The color representing the oversold threshold.
        """
        self.instance.send(self.id, 'setOversoldColor', {'color': color})
        return self

    def set_period_counts(
        self,
        oscillator_period_count: int,
        first_smooth_periods: int,
        double_smooth_periods: int,
        moving_average_period_count: int,
    ):
        """Sets the period counts for various components of the Stochastic Momentum Index.

        Args:
            oscillator_period_count (int): Number of periods for the oscillator.
            first_smooth_periods (int): Number of periods for the first smoothing.
            double_smooth_periods (int): Number of periods for double smoothing.
            moving_average_period_count (int): Number of periods for the moving average.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsStochasticMomentum',
            {
                'oscillatorPeriodCount': oscillator_period_count,
                'firstSmoothPeriods': first_smooth_periods,
                'doubleSmoothPeriods': double_smooth_periods,
                'movingAveragePeriodCount': moving_average_period_count,
            },
        )
        return self

    def set_stochastic_line_color(self, color: str):
        """Sets the color of the stochastic line.

        Args:
            color (str): The color of the stochastic line.
        """
        self.instance.send(self.id, 'setStochasticLineColor', {'color': color})
        return self
