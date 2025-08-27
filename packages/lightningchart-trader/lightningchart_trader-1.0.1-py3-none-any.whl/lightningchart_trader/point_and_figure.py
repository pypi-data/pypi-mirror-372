import uuid


class PointAndFigure:
    def __init__(self, instance, chart_id):
        """
        Initialize the PointAndFigure instance.

        Args:
            instance: The charting instance that interacts with the backend.
            chart_id: The ID of the chart associated with this PointAndFigure instance.
        """
        self.instance = instance
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance.send(self.id, 'getPointAndFigureInstance', {'chartID': chart_id})

    def set_box_size(self, boxSize):
        """
        Sets the box size amount for the Point-and-Figure chart. The price needs to move at least
        this amount for a new X or O to be created.

        Args:
            boxSize (number): New box size amount.
        """
        self.instance.send(self.id, 'setBoxSizePointAndFigure', {'boxSize': boxSize})
        return self

    def set_reversal_amount(self, reversal: int):
        """
        Sets the reversal amount for the Point-and-Figure chart. A new X- or O-column will be created
        when there is a price reversal of at least this amount.

        Args:
            reversal (int): New reversal amount.
        """
        self.instance.send(self.id, 'setReversalAmount', {'reversal': reversal})
        return self

    def set_atr_period_count(self, newPeriodCount):
        """
        Sets the number of time periods (n) used to calculate the Average True Range (ATR).
        Used when the Point-and-Figure chart is based on ATR.

        Args:
            newPeriodCount (number): New period count for ATR calculation.
        """
        self.instance.send(
            self.id,
            'setATRPeriodCountPointAndFigure',
            {'newPeriodCount': newPeriodCount},
        )
        return self

    def set_x_color(self, color: str):
        """
        Sets the color of the X-figures/columns.

        Args:
            color (str): New line color as a string, should be in HEX format (e.g., #FFFFFF).
        """
        self.instance.send(self.id, 'setXColor', {'newColor': color})
        return self

    def set_o_color(self, color: str):
        """
        Sets the color of the O-figures/columns.

        Args:
            color (str): New line color as a string, should be in HEX format (e.g., #FFFFFF).
        """
        self.instance.send(self.id, 'setOColor', {'newColor': color})
        return self

    def set_point_and_figure_base_type(self, base_type: int):
        """
        Sets which values the Point-and-Figure chart is based on.

        Args:
            base_type (int): The integer value of the base type. Valid values are:
                             0 (Close), 1 (HighLowRange), 2 (Percentage), 3 (ATR).
        """
        self.instance.send(self.id, 'setPointAndFigureBaseType', {'baseType': base_type})
        return self
