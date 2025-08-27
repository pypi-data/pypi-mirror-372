from lightningchart_trader.indicators import LineIndicator


class CustomStudy(LineIndicator):
    def __init__(self, trader, line_color='#00FF00', line_width=2, row_index=0):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addCustomStudy',
            {
                'traderID': trader.id,
                'lineColor': line_color,
                'lineWidth': line_width,
                'rowIndex': row_index,
            },
        )

    def set_data(self, data_values: list):
        """Sets the data for the custom study.

        Args:
            data_values (list): A list of data values to be used for the custom study.
        """
        self.instance.send(self.id, 'setDataCustomStudy', {'dataValues': data_values})
        return self

    def add_data(self, data_values: list):
        """Adds additional data to the custom study.

        Args:
            data_values (list): A list of data values to be added to the custom study.
        """
        self.instance.send(self.id, 'addDataCustomStudy', {'dataValues': data_values})
        return self
