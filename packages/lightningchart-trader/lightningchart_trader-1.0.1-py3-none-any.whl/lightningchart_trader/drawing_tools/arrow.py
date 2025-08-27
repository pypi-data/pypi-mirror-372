from lightningchart_trader.drawing_tools import DrawingToolBase


class Arrow(DrawingToolBase):
    def __init__(self, trader, x_position, y_position, arrow_type):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addArrow',
            {
                'traderID': trader.id,
                'xPosition': x_position,
                'yPosition': y_position,
                'arrowType': arrow_type,
            },
        )

    def set_arrow_color(self, color: str):
        """Sets the color of the arrow.

        Args:
            color (str): New arrow color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setArrowColor', {'color': color})
        return self

    def set_arrow_size(self, width: int, height: int):
        """Sets the size of the arrow in pixels.

        Args:
            width (int): New arrow width.
            height (int): New arrow height.
        """
        self.instance.send(self.id, 'setArrowSize', {'width': width, 'height': height})
        return self

    def set_arrow_type(self, arrow_type: int):
        """Sets the arrow type (direction).

        Args:
            arrow_type (int): New arrow type.
        """
        self.instance.send(self.id, 'setArrowType', {'arrowType': arrow_type})
        return self

    def update_position(self, x_value: int | float, y_value: int | float):
        """Updates the drawing tool location.

        Args:
            x_value (int | float): X-value for the cross point.
            y_value (int | float): Y-value (price) for the cross point.
        """
        self.instance.send(self.id, 'updateArrowPosition', {'xValue': x_value, 'yValue': y_value})
        return self
