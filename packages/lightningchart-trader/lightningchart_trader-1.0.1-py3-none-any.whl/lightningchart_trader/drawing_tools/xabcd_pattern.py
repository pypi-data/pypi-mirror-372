from lightningchart_trader.drawing_tools import DrawingToolBase


class XABCDpattern(DrawingToolBase):
    def __init__(
        self,
        trader,
        startX,
        startY,
        positionAX=None,
        positionAY=None,
        positionBX=None,
        positionBY=None,
        positionCX=None,
        positionCY=None,
        positionDX=None,
        positionDY=None,
        lineColor='#000000',
        areaColor=1,
        lineWidth='#FFFFFF',
    ):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addXABCDpattern',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'positionAX': positionAX,
                'positionAY': positionAY,
                'positionBX': positionBX,
                'positionBY': positionBY,
                'positionCX': positionCX,
                'positionCY': positionCY,
                'positionDX': positionDX,
                'positionDY': positionDY,
                'lineColor': lineColor,
                'lineWidth': lineWidth,
                'areaColor': areaColor,
            },
        )

    def set_area_color(self, color: str):
        """Sets the area color of the XABCD Pattern.

        Args:
            color (str): New area color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAreaColor', {'color': color})
        return self

    def set_line_color(self, color: str):
        """Sets the line color of the XABCD Pattern lines.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the XABCD Pattern lines.

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

    def show_ratio_numbers(self, showRatios: bool):
        """When enabled, shows ratio values between various legs.

        Args:
            showRatios (bool): Show ratio numbers.
        """
        self.instance.send(self.id, 'showRatioNumbers', {'showRatios': showRatios})
        return self

    def update_position(
        self,
        positionX=None,
        positionA=None,
        positionB=None,
        positionC=None,
        positionD=None,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            positionX (dict): Location of the X-point.
            positionA (dict): Location of the A-point.
            positionB (dict): Location of the B-point.
            positionC (dict): Location of the C-point.
            positionD (dict): Location of the D-point.
        """
        self.instance.send(
            self.id,
            'updateXABCDPatternPosition',
            {
                'positionX': positionX,
                'positionA': positionA,
                'positionB': positionB,
                'positionC': positionC,
                'positionD': positionD,
            },
        )
        return self
