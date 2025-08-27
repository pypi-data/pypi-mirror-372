from lightningchart_trader.indicators import IndicatorBase


class StochasticOscillatorSmoothed(IndicatorBase):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addStochasticOscillatorSmoothed', {'traderID': trader.id})

    def set_line_width(self, width: int | float):
        """Sets the width of the stochastic oscillator line.

        Args:
            width (int | float): Width of the line.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_moving_average_line_color(self, color: str):
        """Sets the color of the moving average line.

        Args:
            color (str): Color of the moving average line.
        """
        self.instance.send(self.id, 'setMovingAverageLineColor', {'color': color})
        return self

    def set_moving_average_types(self, oscillator_smoothing_average: int, ma_moving_average: int):
        """Sets the types of moving averages for smoothing and the MA line.

        Args:
            oscillator_smoothing_average (int): The smoothing moving average type.
            ma_moving_average (int): The moving average type for the MA line.
        """
        self.instance.send(
            self.id,
            'setMovingAverageTypesStochasticOscillatorSmoothed',
            {
                'oscillatorSmoothingAverage': oscillator_smoothing_average,
                'maMovingAverage': ma_moving_average,
            },
        )
        return self

    def set_overbought_color(self, color: str):
        """Sets the color representing the overbought threshold.

        Args:
            color (str): The overbought color.
        """
        self.instance.send(self.id, 'setOverboughtColor', {'color': color})
        return self

    def set_oversold_and_overbought_ranges(self, oversold_range: float, overbought_range: float):
        """Sets the oversold and overbought threshold ranges.

        Args:
            oversold_range (float): The oversold range value.
            overbought_range (float): The overbought range value.
        """
        self.instance.send(
            self.id,
            'setOversoldAndOverboughtRanges',
            {'oversoldRange': oversold_range, 'overboughtRange': overbought_range},
        )
        return self

    def set_oversold_color(self, color: str):
        """Sets the color representing the oversold threshold.

        Args:
            color (str): The oversold color.
        """
        self.instance.send(self.id, 'setOversoldColor', {'color': color})
        return self

    def set_period_counts(
        self,
        oscillator_period_count: int,
        oscillator_smoothing_periods: int,
        moving_average_period_count: int,
    ):
        """Sets the period counts for different components of the oscillator.

        Args:
            oscillator_period_count (int): The number of periods for the oscillator.
            oscillator_smoothing_periods (int): The number of periods for smoothing the oscillator.
            moving_average_period_count (int): The number of periods for the moving average.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsStochasticOscillatorSmoothed',
            {
                'oscillatorPeriodCount': oscillator_period_count,
                'oscillatorSmoothingPeriods': oscillator_smoothing_periods,
                'movingAveragePeriodCount': moving_average_period_count,
            },
        )
        return self

    def set_stochastic_line_color(self, color: str):
        """Sets the color of the stochastic line.

        Args:
            color (str): Color of the stochastic line.
        """
        self.instance.send(self.id, 'setStochasticLineColor', {'color': color})
        return self
