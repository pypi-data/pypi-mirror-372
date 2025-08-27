from lightningchart_trader.indicators import LineIndicator, SourceIndicator


class StollerAverageRangeChannel(LineIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addStollerAverageRangeChannel', {'traderID': trader.id})

    def set_fill_color(self, color: str):
        """Sets the fill color for the Stoller Average Range Channel.

        Args:
            color (str): The color to set for the fill area.
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_fill_enabled(self, enabled: bool):
        """Enables or disables the fill for the Stoller Average Range Channel.

        Args:
            enabled (bool): True to enable the fill, False to disable it.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': enabled})
        return self

    def set_moving_average_type(self, ma_type: int):
        """Sets the type of moving average used in the channel.

        Args:
            ma_type (int): The moving average type.
        """
        self.instance.send(self.id, 'setMovingAverageType', {'movingAverageType': ma_type})
        return self

    def set_multiplier(self, multiplier: float):
        """Sets the multiplier for the Stoller Average Range Channel.

        Args:
            multiplier (float): The multiplier value to adjust the channel width.
        """
        self.instance.send(self.id, 'setMultiplierStollerAverage', {'Multiplier': multiplier})
        return self

    def set_period_counts(self, period_count_ma: int, period_count_atr: int):
        """Sets the period counts for the moving average and ATR.

        Args:
            period_count_ma (int): The number of periods for the moving average.
            period_count_atr (int): The number of periods for the ATR (Average True Range).
        """
        self.instance.send(
            self.id,
            'setPeriodCountsStollerAverage',
            {'periodCountMA': period_count_ma, 'periodCountATR': period_count_atr},
        )
        return self
