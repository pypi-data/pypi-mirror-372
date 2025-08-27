from lightningchart_trader.drawing_tools import DrawingToolBase


class HorizontalRay(DrawingToolBase):
    def __init__(self, trader, xPosition, yPosition, lineColor='#000000', lineWidth=1):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addHorizontalRay',
            {
                'traderID': trader.id,
                'xPosition': xPosition,
                'yPosition': yPosition,
                'lineColor': lineColor,
                'lineWidth': lineWidth,
            },
        )

    def set_line_color(self, color: str):
        """Sets the color of the Horizontal Ray.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Horizontal Ray.

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

    def update_position(self, xValue: int | float, yValue: int | float):
        """Updates the drawing tool location.

        Args:
            xValue (int | float): Starting point X-value for the ray.
            yValue (int | float): Y-value (price) for the ray.
        """
        self.instance.send(self.id, 'updateHorizontalRayPosition', {'xValue': xValue, 'yValue': yValue})
        return self
