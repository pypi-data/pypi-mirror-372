from lightningchart_trader.indicators import LineIndicator


class CustomOverlay(LineIndicator):
    def __init__(self, trader, line_color='#00FF00', line_width=2):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addCustomOverlay',
            {'traderID': trader.id, 'lineColor': line_color, 'lineWidth': line_width},
        )

    def set_data(self, data_values: list):
        """Sets the data for the custom overlay.

        Args:
            data_values (list): A list of data values to be used for the custom overlay.
        """
        self.instance.send(self.id, 'setDataCustomOverlay', {'dataValues': data_values})
        return self

    def add_data(self, data_values: list):
        """Adds additional data to the custom overlay.

        Args:
            data_values (list): A list of data values to be added to the custom overlay.
        """
        self.instance.send(self.id, 'addDataCustomOverlay', {'dataValues': data_values})
        return self
