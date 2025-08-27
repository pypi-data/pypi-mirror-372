from lightningchart_trader.indicators import LineIndicator, PeriodIndicator


class AverageDirectionalIndex(LineIndicator, PeriodIndicator):
    def __init__(self, trader, period_count=14):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addAverageDirectionalIndex',
            {'traderID': trader.id, 'periodCount': period_count},
        )

    def set_di_minus_color(self, color: str):
        """Sets the line color of the -DI line.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setDiMinusColor', {'color': color})
        return self

    def set_di_plus_color(self, color: str):
        """Sets the line color of the +DI line.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setDiPlusColor', {'color': color})
        return self

    def show_di_lines(self, show: bool):
        """Control whether -DI and +DI lines should be displayed.

        Args:
            show (bool): Set true to show DI lines.
        """
        self.instance.send(self.id, 'showDiLines', {'showDiLines': show})
        return self
