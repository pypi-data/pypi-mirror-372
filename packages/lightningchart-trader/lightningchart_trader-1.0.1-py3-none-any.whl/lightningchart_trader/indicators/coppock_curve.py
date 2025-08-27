from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class CoppockCurve(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addCoppockCurve', {'traderID': trader.id})

    def set_period_counts(
        self,
        period_count_long_roc: int,
        period_count_short_roc: int,
        period_count_wma: int,
    ):
        """Sets the period counts for the Coppock Curve indicator.

        Args:
            period_count_long_roc (int): The period count for the long rate of change (ROC).
            period_count_short_roc (int): The period count for the short rate of change (ROC).
            period_count_wma (int): The period count for the weighted moving average (WMA).
        """
        self.instance.send(
            self.id,
            'setPeriodCountsCoppockCurve',
            {
                'periodCountLongROC': period_count_long_roc,
                'periodCountShortROC': period_count_short_roc,
                'periodCountWMA': period_count_wma,
            },
        )
        return self
