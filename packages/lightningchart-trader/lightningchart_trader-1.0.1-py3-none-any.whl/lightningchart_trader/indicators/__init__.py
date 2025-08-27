import uuid


class IndicatorBase:
    """Base class for all technical indicators."""

    def __init__(self, trader):
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = trader.instance

    def dispose(self):
        """Disposes the indicator."""
        self.instance.send(self.id, 'dispose', {})
        return self

    def set_name(self, name: str):
        """Sets the name of the indicator.

        Args:
            name (str): New indicator name.
        """
        self.name = name
        self.instance.send(self.id, 'setName', {'name': name})
        return self

    def get_name(self):
        """Gets the indicator name."""
        return self.name if self.name else None

    def set_offset(self, offset: int | float):
        """Moves the indicator from its calculated position forward or backward.

        Args:
            offset (int | float): New offset value.
        """
        self.instance.send(self.id, 'setOffset', {'offset': offset})
        return self

    def set_visible(self, visible: bool):
        """Sets the visibility of the indicator.
        Hiding the indicator via setVisible(false) does not remove it.
        Use dispose() to delete any indicator.

        Args:
            visible (bool): Visibility of the indicator.
        """
        self.instance.send(self.id, 'setVisible', {'visible': visible})
        return self


class LineIndicator(IndicatorBase):
    def set_line_color(self, color: str):
        """Sets the line color of the indicator.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the line width of the indicator.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self


class PeriodIndicator(IndicatorBase):
    def set_period_count(self, count: int):
        """Sets the number of time periods (n) used to calculate the indicator.

        Args:
            count (int): New period count.
        """
        self.instance.send(self.id, 'setPeriodCount', {'count': count})
        return self


class SourceIndicator(IndicatorBase):
    def set_source(self, source: str):
        """Sets which values the indicator calculations are based on.

        Args:
            source (str):  "Close" | "High" | "Hl2" | "Hlc3" | "Hlcc4" | "Indicator" | "Low" | "Oc2" | "Olhc4" | "Open"
        """
        self.instance.send(self.id, 'setSource', {'source': source})
        return self


# ruff: noqa: E402, F401
from .accumulation_distribution import AccumulationDistribution
from .accumulative_swing_index import AccumulativeSwingIndex
from .aroon import Aroon
from .aroon_oscillator import AroonOscillator
from .average_directional_index import AverageDirectionalIndex
from .average_true_range import AverageTrueRange
from .awesome_oscillator import AwesomeOscillator
from .balance_of_power import BalanceOfPower
from .bollinger_band import BollingerBand
from .center_of_gravity import CenterOfGravity
from .chaikin_money_flow import ChaikinMoneyFlow
from .chaikin_oscillator import ChaikinOscillator
from .chaikin_volatility import ChaikinVolatility
from .chande_forecast_oscillator import ChandeForecastOscillator
from .chande_momentum_oscillator import ChandeMomentumOscillator
from .commodity_channel_index import CommodityChannelIndex
from .coppock_curve import CoppockCurve
from .correlation_coefficient import CorrelationCoefficient
from .custom_overlay import CustomOverlay
from .custom_study import CustomStudy
from .detrended_price_oscillator import DetrendedPriceOscillator
from .donchian_channels import DonchianChannels
from .ease_of_movement import EaseOfMovement
from .ehler_fisher_transform import EhlerFisherTransform
from .elder_ray_index import ElderRayIndex
from .elder_thermometer_custom import ElderThermometerCustom
from .elders_force_index import EldersForceIndex
from .exponential_moving_average import ExponentialMovingAverage
from .fractal_chaos_bands import FractalChaosBands
from .fractal_chaos_oscillator import FractalChaosOscillator
from .gopalakrishnan_range_index import GopalakrishnanRangeIndex
from .high_low_bands import HighLowBands
from .high_minus_low import HighMinusLow
from .historical_volatility_index import HistoricalVolatilityIndex
from .ichimoku_cloud import IchimokuCloud
from .intraday_momentum_index import IntradayMomentumIndex
from .keltner_channels import KeltnerChannels
from .klinger_volume_oscillator import KlingerVolumeOscillator
from .kurtosis import Kurtosis
from .linear_regression import LinearRegression
from .market_facilitation_index import MarketFacilitationIndex
from .mass_index import MassIndex
from .median_price import MedianPrice
from .momentum_oscillator import MomentumOscillator
from .money_flow_index import MoneyFlowIndex
from .moving_average_convergence_divergence import MovingAverageConvergenceDivergence
from .moving_average_convergence_divergence_custom import MovingAverageConvergenceDivergenceCustom
from .moving_average_envelopes import MovingAverageEnvelopes
from .negative_volume_index import NegativeVolumeIndex
from .on_balance_volume import OnBalanceVolume
from .open_interest import OpenInterest
from .parabolic_sar import ParabolicSAR
from .percentage_price_oscillator import PercentagePriceOscillator
from .performance_index import PerformanceIndex
from .positive_volume_index import PositiveVolumeIndex
from .pretty_good_oscillator import PrettyGoodOscillator
from .price_volume_trend import PriceVolumeTrend
from .prime_number_bands import PrimeNumberBands
from .prime_number_oscillator import PrimeNumberOscillator
from .qstick import QStick
from .rainbow_oscillator import RainbowOscillator
from .random_walk_index import RandomWalkIndex
from .range_action_verification_index import RangeActionVerificationIndex
from .rate_of_change import RateOfChange
from .relative_strength_index import RelativeStrengthIndex
from .sqn_trend import SQNTrend
from .schaff_trend_cycle import SchaffTrendCycle
from .schaff_trend_cycle_signal import SchaffTrendCycleSignal
from .simple_moving_average import SimpleMovingAverage
from .skewness import Skewness
from .standard_deviation import StandardDeviation
from .standard_error import StandardError
from .standard_error_bands import StandardErrorBands
from .stochastic_momentum_index import StochasticMomentumIndex
from .stochastic_oscillator import StochasticOscillator
from .stochastic_oscillator_smoothed import StochasticOscillatorSmoothed
from .stoller_average_range_channel import StollerAverageRangeChannel
from .super_trend import SuperTrend
from .swing_index import SwingIndex
from .time_series_moving_average import TimeSeriesMovingAverage
from .trade_volume_index import TradeVolumeIndex
from .triangular_moving_average import TriangularMovingAverage
from .triple_exponential_average import TripleExponentialAverage
from .true_strength_index import TrueStrengthIndex
from .twiggs_money_flow import TwiggsMoneyFlow
from .typical_price import TypicalPrice
from .ultimate_oscillator import UltimateOscillator
from .ultimate_oscillator_smoothed import UltimateOscillatorSmoothed
from .vidya import VIDYA
from .variable_moving_average import VariableMovingAverage
from .vertical_horizontal_filter import VerticalHorizontalFilter
from .volume import Volume
from .volume_oscillator import VolumeOscillator
from .volume_rate_of_change import VolumeRateOfChange
from .volume_weighted_moving_average import VolumeWeightedMovingAverage
from .weighted_close import WeightedClose
from .weighted_moving_average import WeightedMovingAverage
from .welles_wilder_smoothing_average import WellesWilderSmoothingAverage
from .williams_accumulation_distribution import WilliamsAccumulationDistribution
from .williams_percent_range import WilliamsPercentRange
from .williams_variable_accumulation_distribution import WilliamsVariableAccumulationDistribution
from .z_value import ZValue
