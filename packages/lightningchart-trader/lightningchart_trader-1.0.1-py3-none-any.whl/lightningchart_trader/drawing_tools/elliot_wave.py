from lightningchart_trader.drawing_tools import DrawingToolBase


class ElliotWave(DrawingToolBase):
    def __init__(
        self,
        trader,
        waveType,
        startX,
        startY,
        secondX,
        secondY=None,
        thirdX=None,
        thirdY=None,
        fourthX=None,
        fourthY=None,
        fifthX=None,
        fifthY=None,
        sixthX=None,
        sixthY=None,
        seventhX=None,
        seventhY=None,
        eighthX=None,
        eighthY=None,
        ninthX=None,
        ninthY=None,
    ):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addElliotWave',
            {
                'traderID': trader.id,
                'waveType': waveType,
                'startX': startX,
                'startY': startY,
                'secondX': secondX,
                'secondY': secondY,
                'thirdX': thirdX,
                'thirdY': thirdY,
                'fourthX': fourthX,
                'fourthY': fourthY,
                'fifthX': fifthX,
                'fifthY': fifthY,
                'sixthX': sixthX,
                'sixthY': sixthY,
                'seventhX': seventhX,
                'seventhY': seventhY,
                'eighthX': eighthX,
                'eighthY': eighthY,
                'ninthX': ninthX,
                'ninthY': ninthY,
            },
        )

    def set_line_color(self, color: str):
        """Sets the line color of the wave lines.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the wave lines.

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

    def set_wave_type(self, wave_type: int):
        """Sets the type of the Elliot Wave.

        Args:
            wave_type (int): Elliot Wave type. Possible values:
                0: ElliotWave
                1: ImpulseWave
                2: TriangleWave
                3: TripleComboWave
                4: CorrectionWave
                5: DoubleComboWave
        """
        self.instance.send(self.id, 'setWaveType', {'waveType': wave_type})
        return self

    def update_position(
        self,
        startPosition=None,
        position1=None,
        position2=None,
        position3=None,
        position4=None,
        position5=None,
        positionA=None,
        positionB=None,
        positionC=None,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            startPosition (Point): First control point location.
            position1 (Point): Second control point location (1).
            position2 (Point): Third control point location (2).
            position3 (Point): Fourth control point location (3).
            position4 (Point): Fifth control point location (4).
            position5 (Point): Sixth control point location (5).
            positionA (Point): Seventh control point location (A).
            positionB (Point): Eighth control point location (B).
            positionC (Point): Ninth control point location (C).
        """
        self.instance.send(
            self.id,
            'updateElliotWavePosition',
            {
                'startPosition': startPosition,
                'position1': position1,
                'position2': position2,
                'position3': position3,
                'position4': position4,
                'position5': position5,
                'positionA': positionA,
                'positionB': positionB,
                'positionC': positionC,
            },
        )
        return self
