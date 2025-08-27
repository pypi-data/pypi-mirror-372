from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class Aroon(LineIndicator, PeriodIndicator):
    def __init__(self, trader, period_count=25):
        super().__init__(trader)
        self.instance.send(self.id, 'addAroon', {'traderID': trader.id, 'periodCount': period_count})

    def set_aroon_down_line_color(self, color: str):
        """Sets the color of the Aroon Down line.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAroonDownLineColor', {'color': color})
        return self

    def set_aroon_up_line_color(self, color: str):
        """Sets the color of the Aroon Up line.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAroonUpLineColor', {'color': color})
        return self
