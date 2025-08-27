import uuid


class DrawingToolBase:
    """Base class for all Drawing Tools."""

    def __init__(self, trader):
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = trader.instance

    def dispose(self):
        """Disposes the drawing tool."""
        self.instance.send(self.id, 'dispose', {})
        return self


# ruff: noqa: E402, F401
from .vertical_line import VerticalLine
from .arrow import Arrow
from .cross_line import CrossLine
from .date_range import DateRange
from .elliot_wave import ElliotWave
from .ellipse import Ellipse
from .extended_line import ExtendedLine
from .fibonacci_arc import FibonacciArc
from .fibonacci_extension import FibonacciExtension
from .fibonacci_fan import FibonacciFan
from .fibonacci_retracements import FibonacciRetracements
from .fibonacci_time_zones import FibonacciTimeZones
from .flat_top_bottom import FlatTopBottom
from .head_and_shoulders import HeadAndShoulders
from .horizontal_line import HorizontalLine
from .horizontal_ray import HorizontalRay
from .linear_regression_channel import LinearRegressionChannel
from .parallel_channel import ParallelChannel
from .pitchfork import Pitchfork
from .price_range import PriceRange
from .rectangle import Rectangle
from .text_box import TextBox
from .plain_text import PlainText
from .trend_line import TrendLine
from .triangle import Triangle
from .xabcd_pattern import XABCDpattern
from .cycle_lines import CycleLines
from .sine_wave import SineWave
from .gannbox import GannBox
from .gannfan import GannFan
