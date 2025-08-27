import uuid


class Renko:
    def __init__(self, instance, chart_id):
        """
        Initialize the Renko instance.

        Args:
            instance: The charting instance that interacts with the backend.
            chart_id: The ID of the chart associated with this Renko instance.
        """
        self.instance = instance
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance.send(self.id, 'getRenkoInstance', {'chartID': chart_id})

    def set_box_size(self, box_size: int):
        """Set the box size for the Renko chart.

        Args:
            box_size (int): Sets box size value for the Renko chart. A new brick will be drawn when the price moves above or below the previous brick by this amount.
        """

        if box_size > 0:
            self.instance.send(self.id, 'setBoxSizeRenko', {'boxSize': box_size})
        else:
            raise ValueError('Box size must be greater than 0.')
        return self

    def set_renko_base_type(self, base_type: int):
        """Set the base type for the Renko chart.

        Args:
            base_type (int): The integer value of the base type. Valid values are:
                            0 (Close), 1 (HighLowRange), 2 (Percentage), 3 (ATR).
        """
        self.instance.send(self.id, 'setRenkoBaseType', {'baseType': base_type})
        return self

    def set_atr_period_count(self, period_count: int):
        """Set the ATR period count for the Renko chart.

        Args:
            period_count (int): Sets the number of time periods (n) used to calculate the Average True Range (ATR). Used when Renko chart is based on ATR.
        """

        if period_count > 0:
            self.instance.send(
                self.id,
                'setATRPeriodCountRenko',
                {'newPeriodCount': period_count},
            )
        else:
            raise ValueError('ATR period count must be greater than 0.')
        return self
