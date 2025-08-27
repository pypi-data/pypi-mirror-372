from lightningchart_trader.indicators import LineIndicator


class UltimateOscillator(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addUltimateOscillator', {'traderID': trader.id})

    def set_period_counts(self, period_count_short: int, period_count_mid: int, period_count_long: int):
        """Sets the period counts for the Ultimate Oscillator.

        Args:
            period_count_short (int): The period count for short-term oscillation.
            period_count_mid (int): The period count for mid-term oscillation.
            period_count_long (int): The period count for long-term oscillation.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsUltimateOscillator',
            {
                'periodCountShort': period_count_short,
                'periodCountMid': period_count_mid,
                'periodCountLong': period_count_long,
            },
        )
        return self
