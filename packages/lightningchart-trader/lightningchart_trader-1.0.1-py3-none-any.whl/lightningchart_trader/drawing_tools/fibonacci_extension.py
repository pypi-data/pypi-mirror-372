from lightningchart_trader.drawing_tools import DrawingToolBase


class FibonacciExtension(DrawingToolBase):
    def __init__(
        self,
        trader,
        firstX,
        firstY,
        secondX=None,
        secondY=None,
        thirdX=None,
        thirdY=None,
    ):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addFibonacciExtension',
            {
                'traderID': trader.id,
                'firstX': firstX,
                'firstY': firstY,
                'secondX': secondX,
                'secondY': secondY,
                'thirdX': thirdX,
                'thirdY': thirdY,
            },
        )

    def set_extend_lines(self, enabled: bool):
        """Sets whether the two lines extend to the edge of the chart.

        Args:
            enabled (bool): Set true to extend the lines.
        """
        self.instance.send(self.id, 'setExtendLines', {'extendLines': enabled})
        return self

    def set_fill_enabled(self, fillEnabled: bool):
        """Sets whether areas between the Fibonacci levels are colored or not.

        Args:
            fillEnabled (bool): Set true to enable the fill.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fillEnabled})
        return self

    def set_line_color(self, color: str):
        """Sets the color of the Fibonacci Extension lines.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Fibonacci Extension lines.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_magnetic(self, is_magnetic: bool):
        """Sets whether the drawing tool should automatically snap to OHLC data points.

        Args:
            is_magnetic (bool): Set true to enable snapping to data points.
        """
        self.instance.send(self.id, 'setMagnetic', {'isMagnetic': is_magnetic})
        return self

    def set_show_prices(self, showPrices: bool):
        """Shows the price values of each Fibonacci level label.

        Args:
            showPrices (bool): Set true to show the price values.
        """
        self.instance.send(self.id, 'setShowPrices', {'showPrices': showPrices})
        return self

    def update_position(
        self,
        startX: int | float,
        startY: int | float,
        midX: int | float,
        midY: int | float,
        endX: int | float,
        endY: int | float,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            startX (int | float): Starting point X location.
            startY (int | float): Starting point Y location.
            midX (int | float): Middle point X location.
            midY (int | float): Middle point Y location.
            endX (int | float): End point X location.
            endY (int | float): End point Y location.
        """
        self.instance.send(
            self.id,
            'updateFibonacciExtensionPosition',
            {
                'startX': startX,
                'startY': startY,
                'midX': midX,
                'midY': midY,
                'endX': endX,
                'endY': endY,
            },
        )
        return self
