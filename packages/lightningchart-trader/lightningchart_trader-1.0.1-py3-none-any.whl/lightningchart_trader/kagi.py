import uuid


class Kagi:
    def __init__(self, instance, chart_id):
        """
        Initialize the Kagi instance.

        Args:
            instance: The charting instance that interacts with the backend.
            chart_id: The ID of the chart associated with this Kagi instance.
        """
        self.instance = instance
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance.send(self.id, 'getKagiInstance', {'chartID': chart_id})

    def set_reversal(self, box_size: float):
        """
        Sets the reversal amount for the Kagi chart. The line will change direction when there is
        a price reversal of at least this amount.

        Args:
            box_size (float): New reversal amount.
        """
        self.instance.send(self.id, 'setReversalKagi', {'boxSize': box_size})
        return self

    def set_atr_period_count(self, new_period_count: int):
        """
        Sets the number of time periods (n) used to calculate the Average True Range (ATR).
        Used when the Kagi chart is based on ATR.

        Args:
            new_period_count (int): New period count for ATR calculation.
        """
        self.instance.send(
            self.id,
            'setATRPeriodCountKagi',
            {'newPeriodCount': new_period_count},
        )
        return self

    def set_kagi_base_type(self, base_type: int):
        """
        Sets which values the Kagi chart is based on.

        Args:
            base_type (int): The integer value of the base type. Valid values are:
                             0 (Close), 1 (HighLowRange), 2 (Percentage), 3 (ATR).
        """
        self.instance.send(self.id, 'setKagiBaseType', {'baseType': base_type})
        return self

    def set_line_width(self, new_width: float):
        """
        Sets the width of the Kagi lines. Thick lines will be slightly thicker than the given value.

        Args:
            new_width (float): New line width.
        """
        self.instance.send(self.id, 'setLineWidthKagi', {'newWidth': new_width})
        return self

    def set_thick_line_color(self, color: str):
        """
        Sets the color of the uptrend (thick) line.

        Args:
            color (str): New line color as a string, should be in HEX format (e.g., #FFFFFF).
        """
        self.instance.send(self.id, 'setThickLineColor', {'newColor': color})
        return self

    def set_thin_line_color(self, color: str):
        """
        Sets the color of the downtrend (thin) line.

        Args:
            color (str): New line color as a string, should be in HEX format (e.g., #FFFFFF).
        """
        self.instance.send(self.id, 'setThinLineColor', {'newColor': color})
        return self
