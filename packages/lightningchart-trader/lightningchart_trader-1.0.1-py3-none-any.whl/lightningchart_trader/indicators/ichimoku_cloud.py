from lightningchart_trader.indicators import IndicatorBase


class IchimokuCloud(IndicatorBase):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addIchimokuCloud', {'traderID': trader.id})

    def set_chikou_span_color(self, color: str):
        """Sets the color for the Chikou Span line in the Ichimoku Cloud.

        Args:
            color (str): The color for the Chikou Span line (e.g., '#FF0000' for red).
        """
        self.instance.send(self.id, 'setChikouSpanColor', {'color': color})
        return self

    def set_kijun_sen_color(self, color: str):
        """Sets the color for the Kijun Sen line in the Ichimoku Cloud.

        Args:
            color (str): The color for the Kijun Sen line.
        """
        self.instance.send(self.id, 'setKijunSenColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width for the Ichimoku Cloud lines.

        Args:
            width (int | float): The line width for the Ichimoku Cloud.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_period_counts(
        self,
        tenkan_sen_period: int,
        kijun_sen_period: int,
        senkou_span_b_period: int,
        chikou_span_period: int,
    ):
        """Sets the period counts for the various lines in the Ichimoku Cloud.

        Args:
            tenkan_sen_period (int): The period count for the Tenkan Sen line.
            kijun_sen_period (int): The period count for the Kijun Sen line.
            senkou_span_b_period (int): The period count for the Senkou Span B line.
            chikou_span_period (int): The period count for the Chikou Span line.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsIchimokuCloud',
            {
                'tenkanSenPeriodCount': tenkan_sen_period,
                'kijunSenPeriodCount': kijun_sen_period,
                'senkouSpanBPeriodCount': senkou_span_b_period,
                'chikouSpanPeriodCount': chikou_span_period,
            },
        )
        return self

    def set_senkou_span_a_color(self, color: str):
        """Sets the color for the Senkou Span A line in the Ichimoku Cloud.

        Args:
            color (str): The color for the Senkou Span A line.
        """
        self.instance.send(self.id, 'setSenkouSpanAColor', {'color': color})
        return self

    def set_senkou_span_b_color(self, color: str):
        """Sets the color for the Senkou Span B line in the Ichimoku Cloud.

        Args:
            color (str): The color for the Senkou Span B line.
        """
        self.instance.send(self.id, 'setSenkouSpanBColor', {'color': color})
        return self

    def set_tenkan_sen_color(self, color: str):
        """Sets the color for the Tenkan Sen line in the Ichimoku Cloud.

        Args:
            color (str): The color for the Tenkan Sen line.
        """
        self.instance.send(self.id, 'setTenkanSenColor', {'color': color})
        return self
