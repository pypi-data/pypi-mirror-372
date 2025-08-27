from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class SchaffTrendCycleSignal(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addSchaffTrendCycleSignal', {'traderID': trader.id})

    def set_first_stochastic_moving_averages(self, k_moving_average: int, d_moving_average: int):
        """Sets the moving average types for the first stochastic oscillator in the Schaff Trend Cycle.

        Args:
            k_moving_average (int): The moving average type for %K.
            d_moving_average (int): The moving average type for %D.
        """
        self.instance.send(
            self.id,
            'setFirstStochasticMovingAveragesSchaffTrendCycleSignal',
            {'kMovingAverage': k_moving_average, 'dMovingAverage': d_moving_average},
        )
        return self

    def set_first_stochastic_period_counts(
        self,
        stochastic_periods: int,
        smoothing_periods: int,
        moving_average_periods: int,
    ):
        """Sets the period counts for the first stochastic oscillator.

        Args:
            stochastic_periods (int): The number of periods for the stochastic calculation.
            smoothing_periods (int): The number of periods for smoothing the stochastic values.
            moving_average_periods (int): The number of periods for calculating the moving average.
        """
        self.instance.send(
            self.id,
            'setFirstStochasticPeriodCountsSchaffTrendCycleSignal',
            {
                'stochasticPeriods': stochastic_periods,
                'smoothingPeriods': smoothing_periods,
                'movingAveragePeriods': moving_average_periods,
            },
        )
        return self

    def set_macd_moving_averages(
        self,
        short_moving_average: int,
        long_moving_average: int,
        signal_moving_average: int,
    ):
        """Sets the moving average types for the MACD calculation.

        Args:
            short_moving_average (int): The short-period moving average type.
            long_moving_average (int): The long-period moving average type.
            signal_moving_average (int): The signal line moving average type.
        """
        self.instance.send(
            self.id,
            'setMACDMovingAveragesSchaffTrendCycleSignal',
            {
                'shortMovingAverage': short_moving_average,
                'longMovingAverage': long_moving_average,
                'signalMovingAverage': signal_moving_average,
            },
        )
        return self

    def set_macd_period_counts(self, short_period_count: int, long_period_count: int, signal_period_count: int):
        """Sets the period counts for the MACD calculation.

        Args:
            short_period_count (int): The number of periods for the short moving average.
            long_period_count (int): The number of periods for the long moving average.
            signal_period_count (int): The number of periods for the signal line.
        """
        self.instance.send(
            self.id,
            'setMACDPeriodCountsSchaffTrendCycleSignal',
            {
                'shortPeriodCount': short_period_count,
                'longPeriodCount': long_period_count,
                'signalPeriodCount': signal_period_count,
            },
        )
        return self

    def set_second_stochastic_moving_averages(self, k_moving_average: int, d_moving_average: int):
        """Sets the moving average types for the second stochastic oscillator.

        Args:
            k_moving_average (int): The moving average type for %K.
            d_moving_average (int): The moving average type for %D.
        """
        self.instance.send(
            self.id,
            'setSecondStochasticMovingAveragesSchaffTrendCycleSignal',
            {'kMovingAverage': k_moving_average, 'dMovingAverage': d_moving_average},
        )
        return self

    def set_second_stochastic_period_counts(
        self,
        stochastic_periods: int,
        smoothing_periods: int,
        moving_average_periods: int,
    ):
        """Sets the period counts for the second stochastic oscillator.

        Args:
            stochastic_periods (int): The number of periods for the stochastic calculation.
            smoothing_periods (int): The number of periods for smoothing the stochastic values.
            moving_average_periods (int): The number of periods for calculating the moving average.
        """
        self.instance.send(
            self.id,
            'setSecondStochasticPeriodCountsSchaffTrendCycleSignal',
            {
                'stochasticPeriods': stochastic_periods,
                'smoothingPeriods': smoothing_periods,
                'movingAveragePeriods': moving_average_periods,
            },
        )
        return self
