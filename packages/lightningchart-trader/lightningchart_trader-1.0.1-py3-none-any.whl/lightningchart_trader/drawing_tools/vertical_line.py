from lightningchart_trader.drawing_tools import DrawingToolBase


class VerticalLine(DrawingToolBase):
    def __init__(self, trader, x_position):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addVerticalLine',
            {
                'traderID': trader.id,
                'xPosition': x_position,
            },
        )

    def set_line_color(self, color: str):
        """Sets the color of the Vertical Line.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Vertical Line.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def update_position(self, x_value: int | float):
        """Updates the drawing tool location.

        Args:
            x_value (int | float): X-value for the line. Given as a number.
        """
        self.instance.send(self.id, 'updateVerticalLinePosition', {'xValue': x_value})
        return self
