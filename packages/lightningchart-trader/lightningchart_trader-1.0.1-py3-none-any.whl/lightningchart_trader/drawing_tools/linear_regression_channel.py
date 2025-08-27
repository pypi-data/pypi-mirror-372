from lightningchart_trader.drawing_tools import DrawingToolBase


class LinearRegressionChannel(DrawingToolBase):
    def __init__(self, trader, startX, startY, endX=None, endY=None):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addLinearRegressionChannel',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'endX': endX,
                'endY': endY,
            },
        )

    def set_channel_type(self, channelType: int):
        """Sets the type of the Linear regression Channel.

        Args:
            channelType (int): Channel type. Possible values:
                0: Line
                1: RaffChannel
                2: StandardDeviations
        """
        self.instance.send(self.id, 'setChannelType', {'channelType': channelType})
        return self

    def set_fill_enabled(self, fillEnabled: bool):
        """Set whether areas between the channel lines are colored or not.

        Args:
            fillEnabled (bool): Set true to enable fill.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fillEnabled})
        return self

    def set_line_color(self, color: str):
        """Sets the color of the channel lines.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the channel lines.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_number_of_standard_deviations(self, standardDeviationNumber: int):
        """Sets the number of standard deviations between the linear regression line and the upper and the lower lines.

        Args:
            standardDeviationNumber (int): New number of standard deviations.
        """
        self.instance.send(
            self.id,
            'setNumberOfStandardDeviations',
            {'standardDeviationNumber': standardDeviationNumber},
        )
        return self

    def update_position(self, startX: int | float, endX: int | float):
        """Updates the drawing tool based on the control points' locations.

        Args:
            startX (int | float): Starting point X location.
            endX (int | float): End point X location.
        """
        self.instance.send(
            self.id,
            'updateLinearRegressionChannelPosition',
            {'startX': startX, 'endX': endX},
        )
        return self
