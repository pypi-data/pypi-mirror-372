from lightningchart_trader.indicators import LineIndicator


class ChaikinVolatility(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addChaikinVolatility', {'traderID': trader.id})

    def set_moving_average_type(self, moving_average_type: int):
        """Sets the type of moving average used in the Chaikin Volatility indicator.

        Args:
            moving_average_type (int): The type of moving average to be used (e.g., Simple, Exponential, etc.).
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': moving_average_type})
        return self

    def set_period_counts(self, period_count: int, period_count_ma: int):
        """Sets the period counts for the Chaikin Volatility indicator and its moving average.

        Args:
            period_count (int): The number of periods for the volatility calculation.
            period_count_ma (int): The number of periods for the moving average calculation.

        Raises:
            ValueError: If either `period_count` or `period_count_ma` is not greater than zero.
        """
        period_count = int(period_count)
        period_count_ma = int(period_count_ma)
        if period_count > 0 and period_count_ma > 0:
            self.instance.send(
                self.id,
                'setPeriodCountsChaikinVolatility',
                {'periodCount': period_count, 'periodCountMA': period_count_ma},
            )
        else:
            raise ValueError('Period counts should be integers larger than zero.')
        return self
