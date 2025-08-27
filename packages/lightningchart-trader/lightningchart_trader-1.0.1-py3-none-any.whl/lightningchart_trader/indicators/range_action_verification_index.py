from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class RangeActionVerificationIndex(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addRangeActionVerificationIndex', {'traderID': trader.id})

    def set_moving_average_types(self, moving_average_short: int, moving_average_long: int):
        """Sets the moving average types for the Range Action Verification Index.

        Args:
            moving_average_short (int): The type of the short moving average (valid values between 0 and 9).
            moving_average_long (int): The type of the long moving average (valid values between 0 and 9).

        Raises:
            ValueError: If either moving average type is not between 0 and 9.
        """
        if not (0 <= moving_average_short <= 9) or not (0 <= moving_average_long <= 9):
            raise ValueError('Invalid moving average type. Must be an integer between 0 and 9.')
        self.instance.send(
            self.id,
            'setMovingAverageTypesRangeActionVerification',
            {
                'movingAverageShort': moving_average_short,
                'movingAverageLong': moving_average_long,
            },
        )
        return self

    def set_period_counts(self, short_period_count: int, long_period_count: int):
        """Sets the period counts for the Range Action Verification Index.

        Args:
            short_period_count (int): The number of periods for the short-term range action.
            long_period_count (int): The number of periods for the long-term range action.

        Raises:
            ValueError: If either period count is less than or equal to zero.
        """
        if short_period_count <= 0 or long_period_count <= 0:
            raise ValueError('Period count should be an integer larger than zero.')
        self.instance.send(
            self.id,
            'setPeriodCountsRangeActionVerification',
            {
                'shortPeriodCount': short_period_count,
                'longPeriodCount': long_period_count,
            },
        )
        return self
