from lightningchart_trader.drawing_tools import DrawingToolBase


class HeadAndShoulders(DrawingToolBase):
    def __init__(
        self,
        trader,
        startX,
        startY,
        leftShoulderX=None,
        leftShoulderY=None,
        firstTroughX=None,
        firstTroughY=None,
        headX=None,
        headY=None,
        secondTroughX=None,
        secondTroughY=None,
        rightShoulderX=None,
        rightShoulderY=None,
        endX=None,
        endY=None,
    ):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addHeadAndShoulders',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'leftShoulderX': leftShoulderX,
                'leftShoulderY': leftShoulderY,
                'firstTroughX': firstTroughX,
                'firstTroughY': firstTroughY,
                'headX': headX,
                'headY': headY,
                'secondTroughX': secondTroughX,
                'secondTroughY': secondTroughY,
                'rightShoulderX': rightShoulderX,
                'rightShoulderY': rightShoulderY,
                'endX': endX,
                'endY': endY,
            },
        )

    def set_area_color(self, color: str):
        """Sets the area color of the Head and Shoulders.

        Args:
            color (str): New area color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAreaColor', {'color': color})
        return self

    def set_line_color(self, color: str):
        """Sets the line color of the Head and Shoulders lines.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Head and Shoulders lines.

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
        startPosition=None,
        positionLS=None,
        position1stTrough=None,
        positionHead=None,
        position2ndTrough=None,
        positionRS=None,
        positionEnd=None,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            startPosition (dict, optional): Starting control point location.
            positionLS (dict, optional): Left shoulder control point location.
            position1stTrough (dict, optional): First trough control point location.
            positionHead (dict, optional): Head control point location.
            position2ndTrough (dict, optional): Second trough control point location.
            positionRS (dict, optional): Right shoulder control point location.
            positionEnd (dict, optional): Last control point location.
        """
        self.instance.send(
            self.id,
            'updateHeadAndShouldersPosition',
            {
                'startPosition': startPosition,
                'positionLS': positionLS,
                'position1stTrough': position1stTrough,
                'positionHead': positionHead,
                'position2ndTrough': position2ndTrough,
                'positionRS': positionRS,
                'positionEnd': positionEnd,
            },
        )
        return self
