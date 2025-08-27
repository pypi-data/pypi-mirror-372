from lightningchart_trader.drawing_tools import DrawingToolBase


class Ellipse(DrawingToolBase):
    def __init__(self, trader, startX, startY, radiusX=None, radiusY=None):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addEllipse',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'radiusX': radiusX,
                'radiusY': radiusY,
            },
        )

    def set_area_color(self, color: str):
        """Sets the area color of the Ellipse.

        Args:
            color (str): New area color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAreaColor', {'color': color})
        return self

    def set_line_color(self, color: str):
        """Sets the line color of the Ellipse's border lines.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Ellipse's border lines.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def update_position(
        self,
        point1X: int | float,
        point2X: int | float,
        point1Y: int | float,
        point2Y: int | float,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            point1X (int | float): X-location of the Ellipse's left edge.
            point2X (int | float): X-location of the Ellipse's right edge.
            point1Y (int | float): Y-location of the Ellipse's bottom edge.
            point2Y (int | float): Y-location of the Ellipse's top edge.
        """
        self.instance.send(
            self.id,
            'updateEllipsePosition',
            {
                'point1X': point1X,
                'point2X': point2X,
                'point1Y': point1Y,
                'point2Y': point2Y,
            },
        )
        return self
