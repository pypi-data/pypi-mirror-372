from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class PrettyGoodOscillator(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addPrettyGoodOscillator', {'traderID': trader.id})

    def set_moving_average_types(self, moving_average_ma: int, moving_average_atr: int):
        """Sets the types of moving averages for the Pretty Good Oscillator.

        Args:
            moving_average_ma (int): The type of the Moving Average (MA).
            moving_average_atr (int): The type of the Average True Range (ATR).

        Raises:
            ValueError: Raised if the moving average type is not between 0 and 9.
        """
        if moving_average_ma in range(10) and moving_average_atr in range(10):
            self.instance.send(
                self.id,
                'setMovingAverageTypesPrettyGood',
                {
                    'movingAverageMA': moving_average_ma,
                    'movingAverageATR': moving_average_atr,
                },
            )
        else:
            raise ValueError('Invalid moving average type. Must be an integer between 0 and 9.')
        return self

    def set_period_counts(self, period_count_ma: int, period_count_atr: int):
        """Sets the period counts for the MA and ATR in the Pretty Good Oscillator.

        Args:
            period_count_ma (int): The period count for the Moving Average (MA).
            period_count_atr (int): The period count for the Average True Range (ATR).

        Raises:
            ValueError: Raised if the period count is not greater than zero.
        """
        if period_count_ma > 0 and period_count_atr > 0:
            self.instance.send(
                self.id,
                'setPeriodCountsPrettyGood',
                {'periodCountMA': period_count_ma, 'periodCountATR': period_count_atr},
            )
        else:
            raise ValueError('Period count should be an integer larger than zero.')
        return self
