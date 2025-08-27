from lightningchart_trader.indicators import LineIndicator


class ChaikinOscillator(LineIndicator):
    def __init__(self, trader, fast_period_count=3, slow_period_count=10):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addChaikinOscillator',
            {
                'traderID': trader.id,
                'fastPeriodCount': fast_period_count,
                'slowPeriodCount': slow_period_count,
            },
        )

    def set_period_counts(self, fast_period_count: int, slow_period_count: int):
        """Sets the period counts for the fast and slow moving averages used in the Chaikin Oscillator.

        Args:
            fast_period_count (int): The number of periods for the fast moving average.
            slow_period_count (int): The number of periods for the slow moving average.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsChaikinOscillator',
            {
                'fastPeriodCount': fast_period_count,
                'slowPeriodCount': slow_period_count,
            },
        )
        return self
