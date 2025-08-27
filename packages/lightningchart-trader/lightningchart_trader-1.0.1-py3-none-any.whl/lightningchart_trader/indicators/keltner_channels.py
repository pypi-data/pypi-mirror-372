from lightningchart_trader.indicators import LineIndicator


class KeltnerChannels(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addKeltnerChannels', {'traderID': trader.id})

    def set_fill_color(self, color: str):
        """Sets the fill color of the Keltner Channels.

        Args:
            color (str): The color to set for the filled area of the Keltner Channels (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setFillColor', {'color': color})
        return self

    def set_fill_enabled(self, fill_enabled: bool):
        """Enables or disables the fill color for the Keltner Channels.

        Args:
            fill_enabled (bool): If True, the Keltner Channels will be filled with color.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self

    def set_multiplier(self, multiplier: int | float):
        """Sets the multiplier for the Keltner Channels.

        Args:
            multiplier (int | float): The multiplier used to calculate the channel width.
        """
        self.instance.send(self.id, 'setMultiplierKeltner', {'multiplier': multiplier})
        return self

    def set_period_counts(self, period_count_ema: int, period_count_atr: int):
        """Sets the period counts for EMA and ATR in the Keltner Channels.

        Args:
            period_count_ema (int): The period count for the Exponential Moving Average (EMA).
            period_count_atr (int): The period count for the Average True Range (ATR).
        """
        self.instance.send(
            self.id,
            'setPeriodCountsKeltnerChannels',
            {'periodCountEMA': period_count_ema, 'periodCountATR': period_count_atr},
        )
        return self
