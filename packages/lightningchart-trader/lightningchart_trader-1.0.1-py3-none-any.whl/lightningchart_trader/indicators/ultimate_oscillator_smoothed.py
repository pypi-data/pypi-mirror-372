from lightningchart_trader.indicators import LineIndicator


class UltimateOscillatorSmoothed(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addUltimateOscillatorSmoothed', {'traderID': trader.id})

    def set_moving_average_type(self, ma_type: int):
        """Sets the moving average type for the smoothed Ultimate Oscillator.

        Args:
            ma_type (int): The moving average type to be applied.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': ma_type})
        return self

    def set_period_counts(self, period_count_short: int, period_count_mid: int, period_count_long: int):
        """Sets the period counts for short, mid, and long-term oscillations.

        Args:
            period_count_short (int): The period count for the short-term oscillator.
            period_count_mid (int): The period count for the mid-term oscillator.
            period_count_long (int): The period count for the long-term oscillator.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsUltimateOscillatorSmoothed',
            {
                'periodCountShort': period_count_short,
                'periodCountMid': period_count_mid,
                'periodCountLong': period_count_long,
            },
        )
        return self
