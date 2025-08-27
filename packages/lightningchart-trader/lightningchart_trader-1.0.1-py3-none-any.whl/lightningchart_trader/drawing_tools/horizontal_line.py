from lightningchart_trader.drawing_tools import DrawingToolBase


class HorizontalLine(DrawingToolBase):
    def __init__(self, trader, yPosition, lineColor='#000000', lineWidth=1):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addHorizontalLine',
            {
                'traderID': trader.id,
                'yPosition': yPosition,
                'lineColor': lineColor,
                'lineWidth': lineWidth,
            },
        )

    def set_line_color(self, color: str):
        """Sets the color of the Horizontal Line.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Horizontal Line.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def update_position(self, yValue: int | float):
        """Updates the drawing tool location.

        Args:
            yValue (int | float): Y-value for the line.
        """
        self.instance.send(self.id, 'updateHorizontalLinePosition', {'yValue': yValue})
        return self
