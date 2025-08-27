from lightningchart_trader.drawing_tools import DrawingToolBase


class PlainText(DrawingToolBase):
    def __init__(self, trader, positionX, positionY, text='Text', textColor='#000000'):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addPlainText',
            {
                'traderID': trader.id,
                'positionX': positionX,
                'positionY': positionY,
                'text': text,
                'textColor': textColor,
            },
        )

    def set_font_size(self, fontSize: int | float):
        """Sets the font size of the text.

        Args:
            fontSize (int | float): New font size for the text.
        """
        self.instance.send(self.id, 'setFontSize', {'fontSize': fontSize})
        return self

    def set_text(self, text: str):
        """Sets the text.

        Args:
            text (str): New text.
        """
        self.instance.send(self.id, 'setText', {'text': text})
        return self

    def set_text_color(self, color: str):
        """Sets the color of the text.

        Args:
            color (str): New text color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setTextColor', {'color': color})
        return self

    def update_position(self, positionX: int | float, positionY: int | float):
        """Updates the position of the text.

        Args:
            positionX (int | float): Text X-position.
            positionY (int | float): Text Y-position.
        """
        self.instance.send(
            self.id,
            'updatePlainTextPosition',
            {'positionX': positionX, 'positionY': positionY},
        )
        return self
