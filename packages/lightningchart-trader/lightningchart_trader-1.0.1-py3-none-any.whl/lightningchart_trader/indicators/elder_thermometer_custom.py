from lightningchart_trader.indicators import PeriodIndicator


class ElderThermometerCustom(PeriodIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addElderThermometerCustom', {'traderID': trader.id})

    def set_bar_colors(self, bull_color: str, bear_color: str):
        """Sets the colors for the Bull and Bear bars in the Elder Thermometer.

        Args:
            bull_color (str): The color for the Bull bars (e.g., '#00FF00' for green).
            bear_color (str): The color for the Bear bars (e.g., '#FF0000' for red).
        """
        self.instance.send(
            self.id,
            'setBarColorsElderThermometer',
            {'bullColor': bull_color, 'bearColor': bear_color},
        )
        return self
