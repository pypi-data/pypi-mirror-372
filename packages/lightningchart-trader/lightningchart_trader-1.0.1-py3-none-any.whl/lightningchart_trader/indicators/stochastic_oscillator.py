from lightningchart_trader.indicators import IndicatorBase


class StochasticOscillator(IndicatorBase):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addStochasticOscillator', {'traderID': trader.id})

    def set_line_width(self, width: int | float):
        """Sets the width of the stochastic oscillator line.

        Args:
            width (int | float): Width of the line.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_moving_average_line_color(self, color: str):
        """Sets the color of the moving average line.

        Args:
            color (str): The color to set for the moving average line.
        """
        self.instance.send(self.id, 'setMovingAverageLineColor', {'color': color})
        return self

    def set_overbought_color(self, color: str):
        """Sets the color representing the overbought threshold.

        Args:
            color (str): The color to represent the overbought range.
        """
        self.instance.send(self.id, 'setOverboughtColor', {'color': color})
        return self

    def set_oversold_and_overbought_ranges(self, oversold_range: float, overbought_range: float):
        """Sets the oversold and overbought threshold ranges.

        Args:
            oversold_range (float): The oversold range value.
            overbought_range (float): The overbought range value.
        """
        self.instance.send(
            self.id,
            'setOversoldAndOverboughtRanges',
            {'oversoldRange': oversold_range, 'overboughtRange': overbought_range},
        )
        return self

    def set_oversold_color(self, color: str):
        """Sets the color representing the oversold threshold.

        Args:
            color (str): The color to represent the oversold range.
        """
        self.instance.send(self.id, 'setOversoldColor', {'color': color})
        return self

    def set_period_counts(self, so_period_count: int, ma_period_count: int):
        """Sets the period counts for the stochastic oscillator and moving average.

        Args:
            so_period_count (int): Number of periods for the stochastic oscillator.
            ma_period_count (int): Number of periods for the moving average.
        """
        self.instance.send(
            self.id,
            'setPeriodCountsStochasticOscillator',
            {'soPeriodCount': so_period_count, 'maPeriodCount': ma_period_count},
        )
        return self

    def set_stochastic_line_color(self, color: str):
        """Sets the color of the stochastic line.

        Args:
            color (str): The color to set for the stochastic line.
        """
        self.instance.send(self.id, 'setStochasticLineColor', {'color': color})
        return self
