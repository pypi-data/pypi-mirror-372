from lightningchart_trader.drawing_tools import DrawingToolBase


class FlatTopBottom(DrawingToolBase):
    def __init__(self, trader, startX, startY, endX=None, endY=None, flatYValue=None):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addFlatTopBottom',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'endX': endX,
                'endY': endY,
                'flatYValue': flatYValue,
            },
        )

    def set_area_color(self, color: str):
        """Sets the color of the area between the lines.

        Args:
            color (str): New area color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAreaColor', {'color': color})
        return self

    def set_extend_lines(self, enabled: bool):
        """Sets whether the two lines extend to the edge of the chart.

        Args:
            enabled (bool): Set true to extend the lines.
        """
        self.instance.send(self.id, 'setExtendLines', {'extendLines': enabled})
        return self

    def set_fill_enabled(self, fillEnabled: bool):
        """Sets whether the area between the two lines is colored or not.

        Args:
            fillEnabled (bool): Set true to enable colored fill.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fillEnabled})
        return self

    def set_line_color(self, color: str):
        """Sets the color of the lines.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the lines.

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

    def update_position(
        self,
        startX: int | float,
        endX: int | float,
        trendStartY: int | float,
        trendEndY: int | float,
        flatY: int | float,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            startX (int | float): Trend line first point X-location.
            endX (int | float): Trend line second point X-location.
            trendStartY (int | float): Trend line first point Y-location.
            trendEndY (int | float): Trend line second point Y-location.
            flatY (int | float): Flat line Y-location.
        """
        self.instance.send(
            self.id,
            'updateFlatTopBottomPosition',
            {
                'startX': startX,
                'endX': endX,
                'trendStartY': trendStartY,
                'trendEndY': trendEndY,
                'flatY': flatY,
            },
        )
        return self
