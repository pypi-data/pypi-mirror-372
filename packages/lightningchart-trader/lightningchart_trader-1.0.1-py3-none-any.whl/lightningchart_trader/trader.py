from io import StringIO
import csv as csv_module
import os
import uuid
from datetime import datetime
from IPython import get_ipython
from typing import Union, TYPE_CHECKING
import base64
import requests

from .renko import Renko
from .point_and_figure import PointAndFigure
from .kagi import Kagi

try:
    import pandas as pd
except ImportError:
    pd = None

if TYPE_CHECKING:
    try:
        from pandas import DataFrame
    except ImportError:
        DataFrame = None

from .technical_analysis_methods import TechnicalAnalysisMethods
from .heatmap import Heatmap
from .instance import Instance
from .menu_options import MenuOptions
from .utils.utils import (
    normalize_data,
    preprocess_data_point,
    is_data_sorted_chronologically,
)

from .drawing_tools import (
    VerticalLine,
    Arrow,
    CrossLine,
    DateRange,
    ElliotWave,
    Ellipse,
    ExtendedLine,
    FibonacciArc,
    FibonacciExtension,
    FibonacciFan,
    FibonacciRetracements,
    FibonacciTimeZones,
    FlatTopBottom,
    HeadAndShoulders,
    HorizontalLine,
    HorizontalRay,
    LinearRegressionChannel,
    ParallelChannel,
    Pitchfork,
    PriceRange,
    Rectangle,
    TextBox,
    PlainText,
    TrendLine,
    Triangle,
    XABCDpattern,
    CycleLines,
    SineWave,
    GannBox,
    GannFan,
)

from .indicators import (
    AccumulationDistribution,
    AccumulativeSwingIndex,
    Aroon,
    AroonOscillator,
    AverageDirectionalIndex,
    AverageTrueRange,
    AwesomeOscillator,
    BalanceOfPower,
    BollingerBand,
    CenterOfGravity,
    ChaikinMoneyFlow,
    ChaikinOscillator,
    ChaikinVolatility,
    ChandeForecastOscillator,
    ChandeMomentumOscillator,
    CommodityChannelIndex,
    CoppockCurve,
    CorrelationCoefficient,
    CustomOverlay,
    CustomStudy,
    DetrendedPriceOscillator,
    DonchianChannels,
    EaseOfMovement,
    EhlerFisherTransform,
    ElderRayIndex,
    ElderThermometerCustom,
    EldersForceIndex,
    ExponentialMovingAverage,
    FractalChaosBands,
    FractalChaosOscillator,
    GopalakrishnanRangeIndex,
    HighLowBands,
    HighMinusLow,
    HistoricalVolatilityIndex,
    IchimokuCloud,
    IntradayMomentumIndex,
    KeltnerChannels,
    KlingerVolumeOscillator,
    Kurtosis,
    LinearRegression,
    MarketFacilitationIndex,
    MassIndex,
    MedianPrice,
    MomentumOscillator,
    MoneyFlowIndex,
    MovingAverageConvergenceDivergence,
    MovingAverageConvergenceDivergenceCustom,
    MovingAverageEnvelopes,
    NegativeVolumeIndex,
    OnBalanceVolume,
    OpenInterest,
    ParabolicSAR,
    PercentagePriceOscillator,
    PerformanceIndex,
    PositiveVolumeIndex,
    PrettyGoodOscillator,
    PriceVolumeTrend,
    PrimeNumberBands,
    PrimeNumberOscillator,
    QStick,
    RainbowOscillator,
    RandomWalkIndex,
    RangeActionVerificationIndex,
    RateOfChange,
    RelativeStrengthIndex,
    SQNTrend,
    SchaffTrendCycle,
    SchaffTrendCycleSignal,
    SimpleMovingAverage,
    Skewness,
    StandardDeviation,
    StandardError,
    StandardErrorBands,
    StochasticMomentumIndex,
    StochasticOscillator,
    StochasticOscillatorSmoothed,
    StollerAverageRangeChannel,
    SuperTrend,
    SwingIndex,
    TimeSeriesMovingAverage,
    TradeVolumeIndex,
    TriangularMovingAverage,
    TripleExponentialAverage,
    TrueStrengthIndex,
    TwiggsMoneyFlow,
    TypicalPrice,
    UltimateOscillator,
    UltimateOscillatorSmoothed,
    VIDYA,
    VariableMovingAverage,
    VerticalHorizontalFilter,
    Volume,
    VolumeOscillator,
    VolumeRateOfChange,
    VolumeWeightedMovingAverage,
    WeightedClose,
    WeightedMovingAverage,
    WellesWilderSmoothingAverage,
    WilliamsAccumulationDistribution,
    WilliamsPercentRange,
    WilliamsVariableAccumulationDistribution,
    ZValue,
)


class TAChart:
    def __init__(
        self, license_key: str, html_text_rendering: bool = True, load_from_storage: bool = True, axis_on_right: bool = None, theme: str = None
    ):
        """
        Args:
            license_key (str): "Your license key"
            html_text_rendering (bool): Switch between Html texts and WebGl texts.
            load_from_storage (bool): Sets whether chart settings should be saved to and loaded from the local storage.
            axis_on_right (bool): Set True to place the price axes on the right side of the chart, False to place them on the left.
                NOTE: This only works if load_from_storage is False.
            theme (str): The new color theme. Example values: 'cyberSpace', 'darkGold', 'light', 'lightNature', 'turquoiseHexagon'.
                NOTE: This only works if load_from_storage is False.
        """

        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = Instance(license_key)

        chart_args = {
            'licenseKey': license_key,
            'htmlTextRendering': html_text_rendering,
            'loadFromStorage': load_from_storage,
        }

        if not load_from_storage:
            if axis_on_right is not None:
                chart_args['axisOnRight'] = axis_on_right
            if theme is not None:
                chart_args['colorTheme'] = theme

        self.instance.send(self.id, 'createTradingChart', chart_args)

        self.point_count = 0
        self.settings = {}

    def open(self, method: str = None, width: int | str = '100%', height: int | str = 600):
        """Open the technical analysis chart.

        Method "browser" will open the chart in your browser.
        Method "notebook" will display the chart in a notebook environment with an IFrame component.
        Method "link" will return a URL of the chart that can be used to embed it in external applications.

        Args:
            method (str): "browser" | "notebook" | "link"
            width (int): The CSS width value of the IFrame component.
            height (int): The CSS height value of the IFrame component.

        Returns:
            self | str: Returns a URL string if method is "link", otherwise returns the class instance.
        """
        result = self.instance.open(method=method, width=width, height=height)
        return result if method == 'link' else self

    def close(self):
        """
        Closes the current technical analysis chart instance and releases resources.

        This method ensures that the chart and all related resources are properly closed
        when they are no longer needed. It calls the `close()` method of the underlying
        `TAChart` instance to perform the cleanup.
        """
        self.instance.close()
        return self

    def add_data_point(self, *args, **kwargs):
        """
        Adds a single data point to the end of the existing data or to an empty chart.

        Args:
            *args: Accepts positional arguments like tuples or lists representing the data point.
            **kwargs: Additional keyword arguments for data point fields (e.g., open, high, low, close, dateTime, volume, openInterest).

        Examples:
            >>> ### Using keyword arguments
            >>> trader.add_data_point(open=1.6, high=1.7, low=1.5, close=1.65, date_time='2020-08-22')
            >>> trader.add_data_point(open=1.6, high=1.7, low=1.5, close=1.65)

            >>> ### Using a dictionary
            >>> data_point = {'open': 1.6, 'high': 1.7, 'low': 1.5, 'close': 1.65, 'dateTime': "2022/10/25"}
            >>> trader.add_data_point(data_point=data_point)

            >>> ### Using a list: Ensure OHLC values come first, followed by optional fields and dateTime.
            >>> trader.add_data_point([1.6, 1.7, 1.5, 1.65, "2022/12/25"])
            >>> trader.add_data_point([1.6, 1.7, 1.5, 1.65, 1000, 200, "2023/10/25"])

            >>> ### Using a tuple: Ensure OHLC values come first, followed by optional fields and dateTime.
            >>> trader.add_data_point((1.6, 1.7, 1.5, 1.65, 1000, 200, "2023/11/25"))
            >>> trader.add_data_point((1.6, 1.7, 1.5, 1.65, "2023/12/25"))

            >>> ### Using positional arguments: Ensure OHLC values come first, followed by optional fields and dateTime.
            >>> trader.add_data_point(1.6, 1.7, 1.5, 1.65, "1/4/2024")
            >>> trader.add_data_point(1.6, 1.7, 1.5, 1.65, 1000, 200, "2/4/2024")
        """
        data_point = preprocess_data_point(False, *args, **kwargs)

        scroll = False
        if kwargs and kwargs.get('scroll'):
            scroll = kwargs['scroll']

        self.instance.send(
            self.id,
            'addDataPoint',
            {'dataPoint': data_point, 'scroll': scroll},
        )
        return self

    def update_last_data_point(self, *args, **kwargs):
        """
        Updates the last data point on the chart with new OHLC values, and optionally volume and open interest.

        Args:
            *args: Positional arguments for open, high, low, close, volume, and openInterest in order.
            data_point (Union[dict, list, None]): A dictionary or list representing the data point.
            **kwargs: Additional keyword arguments for data point fields (e.g., open, high, low, close, etc.).

        Examples:
            >>> ### Using positional arguments: Ensure OHLC values come first, followed by dateTime, then optional fields.
            >>> trader.update_last_data_point(101.5, 102.0, 100.0, 101.8, "2024-11-25", 15000, 5000)
            >>> trader.update_last_data_point(101.5, 102.0, 100.0, 101.8, "2024-11-25")

            >>> ### Using a dictionary
            >>> trader.update_last_data_point({
            >>>     "open": 101.5, "high": 102.0, "low": 100.0, "close": 101.8,
            >>>     "dateTime": "2024-11-25", "volume": 15000, "openInterest": 5000
            >>> })

            >>> ### Using a list: Ensure OHLC values come first, followed by dateTime, then optional fields.
            >>> trader.update_last_data_point([101.5, 102.0, 100.0, 101.8, "2024-11-25", 15000, 5000])
            >>> trader.update_last_data_point([101.5, 102.0, 100.0, 101.8, "2024-11-25"])

            >>> ### Using keyword arguments
            >>> trader.update_last_data_point(open=101.5, high=102.0, low=100.0, close=101.8, dateTime="2024-11-25", volume=15000, openInterest=5000)
            >>> trader.update_last_data_point(open=101.5, high=102.0, low=100.0, close=101.8)
        """
        data_point = preprocess_data_point(True, *args, **kwargs)

        self.instance.send(self.id, 'updateLastDataPoint', data_point)
        return self

    def add_data_array(self, data: Union[dict, list, 'DataFrame'], scroll=False):
        """
        Add an array of data points to the existing chart data.

        Args:
            data: The dataset to be added. Can be a list of dictionaries, raw lists of OHLC data, or a single dictionary.
            scroll (bool): Whether to scroll data, dropping the oldest data points.

        Examples:
            >>> ### Using a list of lists: Ensure OHLC values come first, followed by dateTime, then optional fields.
            >>> data = [
            >>>     [1.9, 1.9, 1.7, 1.85, "Thu, 01 Jan 1970 00:00:00 GMT+0000"],
            >>>     [2.0, 2.0, 1.8, 1.95, "04 Dec 1995", 1200, 300]
            >>> ]
            >>> trader.add_data_array(data)

            >>> ### Using mixed list: Ensure OHLC values come first, followed by dateTime, then optional fields.
            >>> data = [
            >>>     {'open': 1.1, 'high': 1.2, 'low': 1.0, 'close': 1.15, 'dateTime': "Jan 1, 1970", 'volume': 350},
            >>>     [1.9, 1.9, 1.7, 1.85, "Thu, 01 Jan 1970 00:00:00 GMT+0000"],
            >>>     {'open': 2.0, 'high': 2.0, 'low': 1.8, 'close': 1.95, 'dateTime': "04 Dec 1995", 'volume': 1200, 'openInterest': 300}
            >>> ]
            >>> trader.add_data_array(data)

            >>> ### Using a single dictionary
            >>> data = {'open': 1.6, 'high': 1.7, 'low': 1.5, 'close': 1.65, 'dateTime': "2022-12-31"}
            >>> trader.add_data_array(data)

            >>> ### Using a DataFrame
            >>> df = pd.read_csv('data/Tesla.csv')
            >>> trader.add_data_array(df)
        """
        normalized_data = normalize_data(data)
        valid_data = [
            item
            for item in normalized_data
            if all(key in item for key in ['open', 'high', 'low', 'close', 'dateTime']) and item['dateTime'] is not None
        ]
        if is_data_sorted_chronologically(valid_data):
            final_data = valid_data
        else:
            try:
                final_data = sorted(valid_data, key=lambda x: x['dateTime'])
            except (TypeError, KeyError) as e:
                raise ValueError(f'Error sorting data by dateTime: {e}. Ensure all dateTime values are valid.')
        self.instance.send(self.id, 'addDataArray', {'data': final_data, 'scroll': scroll})
        return self

    def set_data(self, data: Union[dict, list, 'DataFrame']):
        """
        Sets the dataset for the chart after converting dateTime values to ISO format.

        Args:
            data: The dataset to be set. Can be a single dictionary, a single list of OHLC data,
                multiple lists of OHLC data or Pandas DataFrame.

        Examples:
            >>> ### Using a list of dictionaries: OHLC values come first, then dateTime, and optional fields last.
            >>> data = [
            >>>     {'open': 1.1, 'high': 1.2, 'low': 1.0, 'close': 1.15, 'dateTime': "Jan 1, 1970"},
            >>>     {'open': 1.9, 'high': 1.9, 'low': 1.7, 'close': 1.85, 'dateTime': "Thu, 01 Jan 1970 00:00:00 GMT+0000"}
            >>> ]
            >>> trader.set_data(data)

            >>> ### Using a single dictionary
            >>> data = {'open': 1.1, 'high': 1.2, 'low': 1.0, 'close': 1.15, 'dateTime': "Jan 1, 1970"}
            >>> trader.set_data(data)

            >>> ### Using a list of lists: Ensure OHLC values come first, followed by dateTime, then optional fields.
            >>> data = [
            >>>     [1.1, 1.2, 1.0, 1.15, "Jan 1, 1970"],
            >>>     [1.2, 1.3, 1.1, 1.25, "Feb 1, 1970"]
            >>> ]
            >>> trader.set_data(data)

            >>> ### Using a DataFrame
            >>> df = pd.read_csv('data/Tesla.csv')
            >>> trader.set_data(df)

            >>> ### Mixed formats with different dateTime formats
            >>> data = [
            >>>     {'open': 1.6, 'high': 1.7, 'low': 1.5, 'close': 1.65, 'dateTime': '2024-10-22'},
            >>>     {'open': 1.7, 'high': 1.8, 'low': 1.6, 'close': 1.75, 'dateTime': '2024-10-23'}
            >>> ]
            >>> trader.set_data(data)
        """
        normalized_data = normalize_data(data)
        valid_data = [
            item
            for item in normalized_data
            if all(key in item for key in ['open', 'high', 'low', 'close', 'dateTime']) and item['dateTime'] is not None
        ]
        if is_data_sorted_chronologically(valid_data):
            final_data = valid_data
        else:
            try:
                final_data = sorted(valid_data, key=lambda x: x['dateTime'])
            except (TypeError, KeyError) as e:
                raise ValueError(f'Error sorting data by dateTime: {e}. Ensure all dateTime values are valid.')
        self.instance.send(self.id, 'setData', {'data': final_data})
        return self

    def load_csv(self, csv: str, dataset_name='', delimiter=','):
        """Reads the given csv string/file and converts it into a data array, which is then added to the chart.
        Replaces existing data.

        Args:
            csv (str): Path to the CSV file or CSV file content as string.
            dataset_name (str, optional): Name of the dataset, shown as the chart title. Defaults to ''.
            delimiter (str, optional): Delimiter used in the CSV file. Defaults to ','.

        Examples:
            Read from file:
            >>> trader.load_csv('data/file.csv', delimiter=',')

            Raw CSV string:
            >>> csv_content = '''Date,Open,Close,High,Low,Volume
            >>> 1/4/2010,28.29999924,28.68400002,28.71333313,28.11400032,142981500
            >>> 1/5/2010,29.36666679,29.5340004,30.26666641,29.12800026,266677500
            >>> 1/6/2010,29.36466789,30.10266685,30.10400009,29.33333206,151995000
            >>> '''
            >>> trader.load_csv(csv_content, delimiter=',')
        """
        csv_string = ''

        if os.path.exists(csv):
            with open(csv, 'r') as file:
                csv_string = file.read()
        else:
            csv_string = csv

        try:
            csv_file = StringIO(csv_string)
            csv_reader = csv_module.DictReader(csv_file, delimiter=delimiter)
            csv_data = [row for row in csv_reader]
            if csv_data:
                normalized_csv_data = normalize_data(csv_data)

                valid_csv_data = [
                    item
                    for item in normalized_csv_data
                    if all(key in item for key in ['open', 'high', 'low', 'close', 'dateTime']) and item['dateTime'] is not None
                ]
                numeric_csv_data = []
                for item in valid_csv_data:
                    try:
                        converted_item = {
                            'dateTime': item['dateTime'],
                            'open': float(item['open']) if item['open'] is not None else None,
                            'high': float(item['high']) if item['high'] is not None else None,
                            'low': float(item['low']) if item['low'] is not None else None,
                            'close': float(item['close']) if item['close'] is not None else None,
                        }

                        if 'volume' in item and item['volume'] is not None:
                            converted_item['volume'] = float(item['volume'])
                        if 'openInterest' in item and item['openInterest'] is not None:
                            converted_item['openInterest'] = float(item['openInterest'])

                        if all(converted_item[key] is not None for key in ['open', 'high', 'low', 'close']):
                            numeric_csv_data.append(converted_item)

                    except (ValueError, TypeError):
                        continue
                if is_data_sorted_chronologically(numeric_csv_data):
                    sorted_data = numeric_csv_data
                else:
                    try:
                        sorted_data = sorted(numeric_csv_data, key=lambda x: x['dateTime'])
                    except (TypeError, KeyError) as e:
                        raise ValueError(f'Error sorting CSV data by dateTime: {e}. Ensure all dateTime values are valid.')

                if dataset_name:
                    self.set_chart_title(dataset_name)

                self.instance.send(self.id, 'setData', {'data': sorted_data})
                return self
            else:
                args = {
                    'csvString': csv_string,
                    'datasetName': dataset_name,
                    'delimiter': delimiter,
                }
                self.instance.send(self.id, 'loadCsvString', args)
                return self

        except Exception:
            args = {
                'csvString': csv_string,
                'datasetName': dataset_name,
                'delimiter': delimiter,
            }
            self.instance.send(self.id, 'loadCsvString', args)
            return self

    def clear_data(self):
        """
        Clears all data from the current chart.

        This method sends a command to the technical analysis chart instance to remove all data
        points from the chart. It can be useful when you want to reset or refresh the chart
        without closing it.
        """
        self.instance.send(self.id, 'clearData', {})
        return self

    def set_chart_title(self, title: str):
        """
        Sets the title of the current trading chart.

        This method allows you to specify a title that will be displayed on the chart.

        Args:
            title (str): The title text to be displayed on the chart.
        """
        self.instance.send(self.id, 'setChartTitle', {'title': title})
        return self

    def add_accumulation_distribution(self):
        """
        Adds the Accumulation/Distribution indicator to the chart.

        The Accumulation/Distribution indicator is a volume-based indicator designed to measure the cumulative flow of money into and out of a security.
        """
        return AccumulationDistribution(self)

    def add_accumulative_swing_index(self):
        """
        Adds the Accumulative Swing Index (ASI) indicator to the chart.

        The Accumulative Swing Index (ASI) is a trend-following indicator that quantifies price swings and helps identify trends in the market.
        """
        return AccumulativeSwingIndex(self)

    def add_aroon(self, period_count: int = 25):
        """
        Adds the Aroon indicator to the chart.

        The Aroon indicator is used to identify trend changes in the price of an asset, as well as the strength of that trend.
        It consists of the Aroon-Up and Aroon-Down lines, which show how many periods have passed since the highest high and lowest low, respectively.

        Args:
            period_count (int): The number of periods used to calculate the Aroon indicator.
        """
        return Aroon(self, period_count)

    def add_aroon_oscillator(self, period_count: int = 25):
        """
        Adds the Aroon Oscillator to the chart.

        The Aroon Oscillator is used to determine the strength of a trend and the likelihood of its continuation.
        It is derived from the difference between the Aroon-Up and Aroon-Down indicators.

        Args:
            period_count (int): The number of periods used to calculate the Aroon Oscillator.
        """
        return AroonOscillator(self, period_count)

    def add_average_directional_index(self, period_count: int = 14):
        """
        Adds the Average Directional Index (ADX) to the chart.

        The ADX is used to measure the strength of a trend, whether it's upward or downward.
        It does not indicate the direction of the trend, only the strength of it.
        A higher ADX value means a stronger trend.

        Args:
            period_count (int): The number of periods used to calculate the ADX.
        """
        return AverageDirectionalIndex(self, period_count)

    def add_average_true_range(self, period_count: int = 14):
        """
        Adds the Average True Range (ATR) indicator to the chart.

        The ATR is a volatility indicator that measures the degree of price fluctuation.
        It does not indicate the direction of the price movement, but rather the magnitude of recent volatility.

        Args:
            period_count (int): The number of periods used to calculate the ATR.
        """
        return AverageTrueRange(self, period_count)

    def add_awesome_oscillator(self):
        """
        Adds the Awesome Oscillator (AO) to the chart.

        The Awesome Oscillator is a momentum indicator used to measure market momentum by comparing the most recent 5-period moving average
        with the 34-period moving average of the price. It is primarily used to confirm trends or anticipate potential reversals.
        """
        return AwesomeOscillator(self)

    def add_balance_of_power(self):
        """
        Adds the Balance of Power (BOP) indicator to the chart.

        The Balance of Power is an indicator that measures the strength of buying and selling pressure. It helps to identify potential reversals or continuation of trends based on the balance between buyers and sellers.

        Args:
            period_count (int): The number of periods over which the Balance of Power will be calculated.
        """
        return BalanceOfPower(self)

    def add_bollinger_band(self, period_count: int = 14):
        """
        Adds the Bollinger Bands indicator to the chart.

        Bollinger Bands are a volatility indicator that plots an upper and lower band based on standard deviations
        from a moving average, helping to identify overbought or oversold conditions.

        Args:
            period_count (int): The number of periods to use for the moving average.
        """
        return BollingerBand(self, period_count)

    def add_center_of_gravity(self):
        """
        Adds the Center of Gravity indicator to the chart.

        The Center of Gravity indicator is a leading indicator that identifies turning points in the market.
        """
        return CenterOfGravity(self)

    def add_chaikin_money_flow(self, period_count: int = 21):
        """
        Adds the Chaikin Money Flow indicator to the chart.

        The Chaikin Money Flow measures the accumulation/distribution over a period of time, indicating buying or selling pressure.

        Args:
            period_count (int): The number of periods to calculate the money flow.
        """
        return ChaikinMoneyFlow(self, period_count)

    def add_chaikin_oscillator(self, fast_period_count: int = 3, slow_period_count: int = 10):
        """
        Adds the Chaikin Oscillator to the chart.

        The Chaikin Oscillator is a momentum indicator derived from the accumulation/distribution line of the market.

        Args:
            fast_period_count (int): The fast period for the calculation.
            slow_period_count (int): The slow period for the calculation.
        """
        return ChaikinOscillator(self, fast_period_count, slow_period_count)

    def add_chaikin_volatility(self):
        """
        Adds the Chaikin Volatility indicator to the chart.

        This indicator measures the volatility by comparing the spread between a security's high and low prices.
        """
        return ChaikinVolatility(self)

    def add_chande_forecast_oscillator(self, period_count: int = 14):
        """
        Adds the Chande Forecast Oscillator to the chart.

        This oscillator measures the difference between the price and a linear regression forecast over a period.

        Args:
            period_count (int): The number of periods to calculate the oscillator.
        """
        return ChandeForecastOscillator(self, period_count)

    def add_chande_momentum_oscillator(self, period_count: int = 9):
        """
        Adds the Chande Momentum Oscillator to the chart.

        This oscillator is used to measure momentum over a specified period of time.

        Args:
            period_count (int): The number of periods for calculating momentum.
        """
        return ChandeMomentumOscillator(self, period_count)

    def add_commodity_channel_index(self, period_count: int = 20):
        """
        Adds the Commodity Channel Index (CCI) to the chart.

        The CCI is an oscillator that helps to identify cyclical trends in commodities or other securities.

        Args:
            period_count (int): The number of periods for the CCI calculation.
        """
        return CommodityChannelIndex(self, period_count)

    def add_coppock_curve(self):
        """
        Adds the Coppock Curve to the chart.

        The Coppock Curve is a long-term momentum indicator used to identify major bottoms in the stock market.
        """
        return CoppockCurve(self)

    def add_correlation_coefficient(self):
        """
        Adds the Correlation Coefficient indicator to the chart.

        The Correlation Coefficient measures the strength of the relationship between two variables.
        """
        return CorrelationCoefficient(self)

    def add_custom_overlay(self):
        """
        Adds a Custom Overlay indicator to the chart.

        Custom overlays allow you to create and apply custom formulas or calculations.
        """
        return CustomOverlay(self)

    def add_custom_study(self):
        """
        Adds a Custom Study to the chart.

        Custom studies allow for the creation and application of unique trading strategies and calculations.
        """
        return CustomStudy(self)

    def add_detrended_price_oscillator(self):
        """
        Adds the Detrended Price Oscillator (DPO) to the chart.

        The DPO is used to identify cycles in the market by removing the long-term trend.

        Args:
            period_count (int): The number of periods for the DPO calculation.
        """
        return DetrendedPriceOscillator(self)

    def add_donchian_channels(self, period_count: int = 20):
        """
        Adds Donchian Channels to the chart.

        Donchian Channels plot the highest and lowest price over a period, used to identify breakouts.

        Args:
            period_count (int): The number of periods to calculate the channels.
        """
        return DonchianChannels(self, period_count)

    def add_ease_of_movement(self):
        """
        Adds the Ease of Movement (EOM) indicator to the chart.

        EOM is an indicator that measures the relationship between price changes and volume. It shows how easily a price is moving up or down.
        """
        return EaseOfMovement(self)

    def add_ehler_fisher_transform(self):
        """
        Adds the Ehler Fisher Transform indicator to the chart.

        The Ehler Fisher Transform is a technical indicator used to determine trend reversals based on price data transformation.
        """
        return EhlerFisherTransform(self)

    def add_elder_ray_index(self, period_count: int = 13):
        """
        Adds the Elder Ray Index indicator to the chart.

        The Elder Ray Index helps identify buying and selling pressure in the market.

        Args:
            period_count (int): The number of periods over which the Elder Ray Index will be calculated.
        """
        return ElderRayIndex(self, period_count)

    def add_elder_thermometer_custom(self):
        """
        Adds a custom Elder Thermometer indicator to the chart.

        This indicator helps measure market volatility by comparing price range changes.
        """
        return ElderThermometerCustom(self)

    def add_elders_force_index(self, period_count: int = 13):
        """
        Adds the Elder's Force Index to the chart.

        Elder's Force Index measures the strength of bulls or bears in the market by combining price direction, extent of price movement, and volume.

        Args:
            period_count (int): The number of periods over which the Force Index will be calculated.
        """
        return EldersForceIndex(self, period_count)

    def add_exponential_moving_average(self, period_count: int = 14):
        """
        Adds the Exponential Moving Average (EMA) to the chart.

        The EMA gives more weight to recent prices to make it more responsive to new information.

        Args:
            period_count (int): The number of periods over which the EMA will be calculated.
        """
        return ExponentialMovingAverage(self, period_count)

    def add_fractal_chaos_bands(self):
        """
        Adds the Fractal Chaos Bands indicator to the chart.

        This indicator helps identify the market's fractal patterns and potential turning points.
        """
        return FractalChaosBands(self)

    def add_fractal_chaos_oscillator(self):
        """
        Adds the Fractal Chaos Oscillator to the chart.

        This indicator helps identify fractal patterns in the market for trend analysis.

        Args:
            period_count (int): The number of periods over which the oscillator will be calculated.
        """
        return FractalChaosOscillator(self)

    def add_gopalakrishnan_range_index(self, period_count: int = 14):
        """
        Adds the Gopalakrishnan Range Index (GAPO) to the chart.

        GAPO is used to measure the volatility of an asset over a specified period.

        Args:
            period_count (int): The number of periods over which the range index will be calculated.
        """
        return GopalakrishnanRangeIndex(self, period_count)

    def add_high_low_bands(self):
        """
        Adds the High-Low Bands indicator to the chart.

        The High-Low Bands indicator shows two lines representing the highest and lowest prices over a specific period.

        Args:
            period_count (int): The number of periods to calculate the high and low bands.
        """
        return HighLowBands(self)

    def add_high_minus_low(self):
        """
        Adds the High Minus Low indicator to the chart.

        The High Minus Low indicator calculates the difference between the high and low prices.
        """
        return HighMinusLow(self)

    def add_historical_volatility_index(self):
        """
        Adds the Historical Volatility Index to the chart.

        This indicator measures the volatility of a stock by calculating the standard deviation of its price changes over a specified period.
        """
        return HistoricalVolatilityIndex(self)

    def add_ichimoku_cloud(self):
        """
        Adds the Ichimoku Cloud indicator to the chart.

        Ichimoku Cloud is a technical analysis tool that defines support and resistance, identifies trend direction, and provides trade signals.
        """
        return IchimokuCloud(self)

    def add_intraday_momentum_index(self):
        """
        Adds the Intraday Momentum Index to the chart.

        This indicator combines elements of both candlestick analysis and RSI to show intraday price momentum.
        """
        return IntradayMomentumIndex(self)

    def add_keltner_channels(self):
        """
        Adds the Keltner Channels to the chart.

        Keltner Channels are volatility-based envelopes set above and below an exponential moving average.
        """
        return KeltnerChannels(self)

    def add_klinger_volume_oscillator(self):
        """
        Adds the Klinger Volume Oscillator to the chart.

        The Klinger Oscillator uses volume and price to predict price reversals.
        """
        return KlingerVolumeOscillator(self)

    def add_kurtosis(self):
        """
        Adds the Kurtosis indicator to the chart.

        Kurtosis measures the "tailedness" of the distribution of returns.
        """
        return Kurtosis(self)

    def add_linear_regression(self):
        """
        Adds the Linear Regression indicator to the chart.

        This indicator shows the best-fit line of a stock's price movement over a specified time period.
        """
        return LinearRegression(self)

    def add_market_facilitation_index(self):
        """
        Adds the Market Facilitation Index (MFI) to the chart.

        MFI evaluates the efficiency of price movements by comparing price changes with volume.
        """
        return MarketFacilitationIndex(self)

    def add_mass_index(self, period_count: int = 25):
        """
        Adds the Mass Index to the chart.

        The Mass Index identifies potential reversals by analyzing price ranges.

        Args:
            period_count (int): The number of periods to calculate the Mass Index.
        """
        return MassIndex(self, period_count)

    def add_median_price(self):
        """
        Adds the Median Price indicator to the chart.

        The Median Price indicator is a simple average of the high and low prices for each period.
        """
        return MedianPrice(self)

    def add_momentum_oscillator(self, period_count: int = 10):
        """
        Adds the Momentum Oscillator to the chart.

        The Momentum Oscillator measures the rate of change in a stock’s price.

        Args:
            period_count (int): The number of periods over which to calculate momentum.
        """
        return MomentumOscillator(self, period_count)

    def add_money_flow_index(self, period_count: int = 14):
        """
        Adds the Money Flow Index (MFI) to the chart.

        MFI measures the strength of money flowing into and out of a security over a specific period.

        Args:
            period_count (int): The number of periods to calculate MFI.
        """
        return MoneyFlowIndex(self, period_count)

    def add_moving_average_convergence_divergence(self):
        """
        Adds the Moving Average Convergence Divergence (MACD) indicator to the chart.

        MACD shows the relationship between two moving averages of a security’s price.
        """
        return MovingAverageConvergenceDivergence(self)

    def add_moving_average_convergence_divergence_custom(self):
        """
        Adds a custom MACD indicator to the chart, allowing for custom settings.
        """
        return MovingAverageConvergenceDivergenceCustom(self)

    def add_moving_average_envelopes(self, period_count: int):
        """
        Adds the Moving Average Envelopes to the chart.

        Moving Average Envelopes are percentages-based lines set above and below a moving average.

        Args:
            period_count (int): The number of periods over which the moving average is calculated.
        """
        return MovingAverageEnvelopes(self, period_count)

    def add_negative_volume_index(self):
        """
        Adds the Negative Volume Index (NVI) indicator to the chart.

        The Negative Volume Index is used to identify trends in a market based on the concept that "smart money" takes advantage of low volume periods to make its move.

        """
        return NegativeVolumeIndex(self)

    def add_on_balance_volume(self):
        """
        Adds the On Balance Volume (OBV) indicator to the chart.

        The On Balance Volume indicator measures buying and selling pressure based on the volume flow to predict future price movements.

        """
        return OnBalanceVolume(self)

    def add_open_interest(self):
        """
        Adds the Open Interest indicator to the chart.

        Open Interest is the total number of outstanding contracts for an asset in futures or options trading.

        """
        return OpenInterest(self)

    def add_parabolic_sar(self):
        """
        Adds the Parabolic SAR indicator to the chart.

        The Parabolic SAR is used to identify potential reversals in market trends.

        """
        return ParabolicSAR(self)

    def add_percentage_price_oscillator(self):
        """
        Adds the Percentage Price Oscillator (PPO) to the chart.

        The Percentage Price Oscillator is a momentum indicator that shows the relationship between two moving averages of a security’s price.

        """
        return PercentagePriceOscillator(self)

    def add_performance_index(self):
        """
        Adds the Performance Index indicator to the chart.

        The Performance Index is used to analyze how well a security is performing over time, typically in comparison to a benchmark.

        """
        return PerformanceIndex(self)

    def add_positive_volume_index(self):
        """
        Adds the Positive Volume Index (PVI) indicator to the chart.

        The Positive Volume Index is used to measure changes in volume and identify market trends when the volume is high.

        """
        return PositiveVolumeIndex(self)

    def add_pretty_good_oscillator(self):
        """
        Adds the Pretty Good Oscillator to the chart.

        The Pretty Good Oscillator is used to identify overbought and oversold levels.

        """
        return PrettyGoodOscillator(self)

    def add_price_volume_trend(self):
        """
        Adds the Price Volume Trend (PVT) indicator to the chart.

        The Price Volume Trend indicator helps to confirm trends in price by considering the amount of traded volume.

        """
        return PriceVolumeTrend(self)

    def add_prime_number_bands(self):
        """
        Adds the Prime Number Bands indicator to the chart.

        The Prime Number Bands show significant price levels based on prime numbers.

        """
        return PrimeNumberBands(self)

    def add_prime_number_oscillator(self):
        """
        Adds the Prime Number Oscillator to the chart.

        The Prime Number Oscillator highlights key levels of support and resistance using prime numbers.

        """
        return PrimeNumberOscillator(self)

    def add_qstick(self, period_count: int):
        """
        Adds the QStick indicator to the chart.

        The QStick is a technical analysis indicator that measures the average of the difference between the open and close prices over a specified period.

        Args:
            period_count (int): The number of periods over which to calculate the QStick.
        """
        return QStick(self, period_count)

    def add_rainbow_oscillator(self):
        """
        Adds the Rainbow Oscillator to the chart.

        The Rainbow Oscillator uses a series of moving averages to identify trends and potential reversals.

        """
        return RainbowOscillator(self)

    def add_random_walk_index(self):
        """
        Adds the Random Walk Index (RWI) to the chart.

        The Random Walk Index is a technical analysis indicator used to determine if a security is trending or in a range.

        Args:
            period_count (int): The number of periods used in the RWI calculation.
        """
        return RandomWalkIndex(self)

    def add_range_action_verification_index(self):
        """
        Adds the Range Action Verification Index (RAVI) to the chart.

        The RAVI measures the strength of a price trend and can indicate if a market is trending or consolidating.

        """
        return RangeActionVerificationIndex(self)

    def add_rate_of_change(self, period_count: int = 9):
        """
        Adds the Rate of Change (ROC) indicator to the chart.

        The Rate of Change measures the percentage change in a security's price between the current price and a price in a previous period.

        Args:
            period_count (int): The number of periods over which to calculate the ROC.
        """
        return RateOfChange(self, period_count)

    def add_relative_strength_index(self, period_count: int = 14):
        """
        Adds the Relative Strength Index (RSI) to the chart.

        The RSI measures the speed and change of price movements and is used to identify overbought or oversold conditions.

        Args:
            period_count (int): The number of periods over which to calculate the RSI.
        """
        return RelativeStrengthIndex(self, period_count)

    def add_sqn_trend(self):
        """
        Adds the System Quality Number (SQN) Trend indicator to the chart.

        The SQN Trend measures the quality of a trading system over a specific time frame.

        Args:
            period_count (int): The number of periods used to calculate the SQN.
        """
        return SQNTrend(self)

    def add_schaff_trend_cycle(self):
        """
        Adds the Schaff Trend Cycle (STC) to the chart.

        The Schaff Trend Cycle is a technical analysis tool that uses moving averages to determine market trends.

        """
        return SchaffTrendCycle(self)

    def add_schaff_trend_cycle_signal(self):
        """
        Adds the Schaff Trend Cycle Signal indicator to the chart.

        This is used to generate signals based on the Schaff Trend Cycle for potential market entry and exit points.

        """
        return SchaffTrendCycleSignal(self)

    def add_simple_moving_average(self, period_count: int = 14):
        """
        Adds the Simple Moving Average (SMA) to the chart.

        The SMA is a widely used indicator that calculates the average price over a specific period.

        Args:
            period_count (int): The number of periods over which to calculate the SMA.
        """
        return SimpleMovingAverage(self, period_count)

    def add_skewness(self):
        """
        Adds the Skewness indicator to the chart.

        The Skewness indicator measures the asymmetry of the returns distribution for a security.

        Args:
            period_count (int): The number of periods used for the calculation of skewness.
        """
        return Skewness(self)

    def add_standard_deviation(self, period_count: int = 20):
        """
        Adds the Standard Deviation indicator to the chart.

        Standard Deviation is a statistical measure of price volatility over a specified period.

        Args:
            period_count (int): The number of periods used for the Standard Deviation calculation.
        """
        return StandardDeviation(self, period_count)

    def add_standard_error(self, period_count: int = 14):
        """
        Adds the Standard Error indicator to the chart.

        The Standard Error shows the standard deviation of the regression line over a specified period.

        Args:
            period_count (int): The number of periods over which to calculate the Standard Error.
        """
        return StandardError(self, period_count)

    def add_standard_error_bands(self):
        """
        Adds the Standard Error Bands to the chart.

        These bands represent a range above and below a moving average based on the standard error.

        """
        return StandardErrorBands(self)

    def add_stochastic_momentum_index(self):
        """
        Adds the Stochastic Momentum Index (SMI) to the chart.

        The SMI helps identify trend direction and potential reversal points.

        """
        return StochasticMomentumIndex(self)

    def add_stochastic_oscillator(self):
        """
        Adds the Stochastic Oscillator to the chart.

        The Stochastic Oscillator is a momentum indicator that compares a security's closing price to its price range over a specific period.

        """
        return StochasticOscillator(self)

    def add_stochastic_oscillator_smoothed(self):
        """
        Adds the Smoothed Stochastic Oscillator to the chart.

        This is a variation of the traditional Stochastic Oscillator with additional smoothing to reduce false signals.

        """
        return StochasticOscillatorSmoothed(self)

    def add_stoller_average_range_channel(self):
        """
        Adds the Stoller Average Range Channel (STARC) to the chart.

        The STARC bands are a volatility-based indicator that can help identify overbought and oversold conditions.

        """
        return StollerAverageRangeChannel(self)

    def add_super_trend(self, period_count: int = 10):
        """
        Adds the Super Trend indicator to the chart.

        The Super Trend is used to identify market trends and potential reversals.

        Args:
            period_count (int): The number of periods used in the Super Trend calculation.
        """
        return SuperTrend(self, period_count)

    def add_swing_index(self):
        """
        Adds the Swing Index to the chart.

        The Swing Index identifies the overall trend direction by comparing the current price with previous prices.

        """
        return SwingIndex(self)

    def add_time_series_moving_average(self, period_count: int = 25):
        """
        Adds the Time Series Moving Average (TSMA) to the chart.

        The TSMA is a moving average based on linear regression.

        Args:
            period_count (int): The number of periods used to calculate the TSMA.
        """
        return TimeSeriesMovingAverage(self, period_count)

    def add_trade_volume_index(self):
        """
        Adds the Trade Volume Index (TVI) to the chart.

        The TVI is used to determine whether a security is under accumulation or distribution by measuring the volume traded at different price levels.

        """
        return TradeVolumeIndex(self)

    def add_triangular_moving_average(self, period_count: int = 20):
        """
        Adds the Triangular Moving Average (TMA) to the chart.

        The TMA gives more weight to middle data points and less to extremes, smoothing price trends.

        Args:
            period_count (int): The number of periods used for the TMA calculation.
        """
        return TriangularMovingAverage(self, period_count)

    def add_triple_exponential_average(self):
        """
        Adds the Triple Exponential Moving Average (TEMA) to the chart.

        The TEMA is a variation of the exponential moving average that aims to reduce lag in trend identification.

        Args:
            period_count (int): The number of periods used in the TEMA calculation.
        """
        return TripleExponentialAverage(self)

    def add_true_strength_index(self):
        """
        Adds the True Strength Index (TSI) to the chart.

        The TSI measures momentum based on price changes and is used to identify trend strength and reversals.

        """
        return TrueStrengthIndex(self)

    def add_twiggs_money_flow(self):
        """
        Adds the Twiggs Money Flow (TMF) indicator to the chart.

        The TMF measures buying and selling pressure over a specified period and is used to identify market trends.

        Args:
            period_count (int): The number of periods used for the TMF calculation.
        """
        return TwiggsMoneyFlow(self)

    def add_typical_price(self):
        """
        Adds the Typical Price indicator to the chart.

        The Typical Price is an average of the high, low, and close prices for a trading period, used to identify trends.

        """
        return TypicalPrice(self)

    def add_ultimate_oscillator(self):
        """
        Adds the Ultimate Oscillator to the chart.

        The Ultimate Oscillator combines short, medium, and long-term price movements into a single indicator to identify overbought and oversold conditions.

        """
        return UltimateOscillator(self)

    def add_ultimate_oscillator_smoothed(self):
        """
        Adds the Smoothed Ultimate Oscillator to the chart.

        This is a variation of the Ultimate Oscillator with additional smoothing to reduce noise.

        """
        return UltimateOscillatorSmoothed(self)

    def add_vidya(self, period_count: int = 9):
        """
        Adds the Variable Index Dynamic Average (VIDYA) to the chart.

        The VIDYA is a type of adaptive moving average that adjusts its sensitivity based on market volatility.

        Args:
            period_count (int): The number of periods used for the VIDYA calculation.
        """
        return VIDYA(self, period_count)

    def add_variable_moving_average(self, period_count: int = 9):
        """
        Adds the Variable Moving Average (VMA) to the chart.

        The VMA is a moving average that adjusts its period length based on market volatility.

        Args:
            period_count (int): The number of periods used to calculate the VMA.
        """
        return VariableMovingAverage(self, period_count)

    def add_vertical_horizontal_filter(self, period_count: int = 28):
        """
        Adds the Vertical Horizontal Filter (VHF) to the chart.

        The VHF helps identify whether the market is trending or ranging.

        Args:
            period_count (int): The number of periods used in the VHF calculation.
        """
        return VerticalHorizontalFilter(self, period_count)

    def add_volume(
        self,
        add_as_overlay: bool = True,
        two_colored_bars: bool = True,
        bar_color: str = '#0000FF',
        offset: int = 0,
    ):
        """
        Adds the Volume indicator to the chart.

        Volume shows the number of traded securities over a specific time period and can help identify market activity and trends.

        Args:
            add_as_overlay (bool, optional): Whether to display volume as an overlay. Defaults to True.
            two_colored_bars (bool, optional): Whether to use two-colored bars for up/down volume. Defaults to True.
            bar_color (str, optional): The color for the volume bars. Defaults to '#0000FF'.
            offset (int, optional): The offset for volume data. Defaults to 0.
        """
        return Volume(self)

    def add_volume_oscillator(self):
        """
        Adds the Volume Oscillator to the chart.

        The Volume Oscillator measures the difference between two moving averages of volume to indicate market trends.

        """
        return VolumeOscillator(self)

    def add_volume_rate_of_change(self):
        """
        Adds the Volume Rate of Change (VROC) indicator to the chart.

        The VROC shows the percentage change in volume between two periods.

        """
        return VolumeRateOfChange(self)

    def add_volume_weighted_moving_average(self, period_count: int = 20):
        """
        Adds the Volume Weighted Moving Average (VWMA) to the chart.

        The VWMA calculates the average price weighted by volume, giving more significance to price movements with higher volume.

        Args:
            period_count (int): The number of periods used to calculate the VWMA.
        """
        return VolumeWeightedMovingAverage(self, period_count)

    def add_weighted_close(self):
        """
        Adds the Weighted Close indicator to the chart.

        The Weighted Close averages the high, low, and close prices, with more weight given to the close.

        """
        return WeightedClose(self)

    def add_weighted_moving_average(self, period_count: int = 14):
        """
        Adds the Weighted Moving Average (WMA) to the chart.

        The WMA gives more weight to recent data points, helping to identify trends more quickly.

        Args:
            period_count (int): The number of periods used to calculate the WMA.
        """
        return WeightedMovingAverage(self, period_count)

    def add_welles_wilder_smoothing_average(self, period_count: int = 14):
        """
        Adds the Welles Wilder Smoothing Average to the chart.

        This is a variation of the exponential moving average developed by Welles Wilder.

        Args:
            period_count (int): The number of periods used to calculate the smoothing average.
        """
        return WellesWilderSmoothingAverage(self, period_count)

    def add_williams_accumulation_distribution(self):
        """
        Adds the Williams Accumulation Distribution indicator to the chart.

        This indicator measures market accumulation and distribution based on price and volume movements.

        Args:
            period_count (int): The number of periods used to calculate the indicator.
        """
        return WilliamsAccumulationDistribution(self)

    def add_williams_percent_range(self, period_count: int = 14):
        """
        Adds the Williams Percent Range (%R) indicator to the chart.

        The Williams %R measures overbought and oversold levels, similar to the RSI.

        Args:
            period_count (int): The number of periods used to calculate the %R.
        """
        return WilliamsPercentRange(self, period_count)

    def add_williams_variable_accumulation_distribution(self):
        """
        Adds the Williams Variable Accumulation Distribution (WVAD) indicator to the chart.

        The WVAD helps identify buying and selling pressure by combining volume and price movements.

        Args:
            period_count (int): The number of periods used to calculate the WVAD.
        """
        return WilliamsVariableAccumulationDistribution(self)

    def add_z_value(self, period_count: int = 20):
        """
        Adds the Z-Value indicator to the chart.

        The Z-Value measures how many standard deviations a security's price is from the mean, helping to identify overbought or oversold conditions.

        Args:
            period_count (int): The number of periods used to calculate the Z-Value.
        """
        return ZValue(self, period_count)

    def dispose_all_indicators(self, dispose_secondary_symbol=False):
        """
        Disposes of all indicators on the chart.

        Args:
            dispose_secondary_symbol (bool, optional): Whether to dispose the secondary symbol as well. Defaults to False.
        """
        self.instance.send(
            self.id,
            'disposeAllIndicators',
            {'disposeSecondarySymbol': dispose_secondary_symbol},
        )

    # DRAWING TOOLS:

    def add_vertical_line(self, x_position: int | float):
        """Adds Vertical Line to the chart. Draws a line across the whole chart.

        Args:
            x_position (int | float): X-position for the line. Given as a number.
        """
        return VerticalLine(self, x_position=x_position)

    def add_arrow(self, x_position: int | float, y_position: int | float):
        """Adds an Arrow to the chart.

        Args:
            x_position (int | float): X-value for the cross point.
            y_position (int | float): Y-value for the cross point.
        """
        return Arrow(self, x_position=x_position, y_position=y_position, arrow_type=0)

    def add_cross_line(self, x_position: int | float, y_position: int | float):
        """Adds Cross Line to the chart. Draws horizontal and vertical lines crossing at the selected point of the chart.

        Args:
            x_position (int | float): X-position for the cross point.
            y_position (int | float): Y-position for the cross point.
        """
        return CrossLine(self, x_position=x_position, y_position=y_position)

    def add_date_range(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Date Range measurement tool to the chart. Measures the date range, bar count, and total volume between two points.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return DateRange(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_elliot_wave(
        self,
        waveType: int,
        startX: int | float,
        startY: int | float,
        secondX: int | float = None,
        secondY: int | float = None,
        thirdX: int | float = None,
        thirdY: int | float = None,
        fourthX: int | float = None,
        fourthY: int | float = None,
        fifthX: int | float = None,
        fifthY: int | float = None,
        sixthX: int | float = None,
        sixthY: int | float = None,
        seventhX: int | float = None,
        seventhY: int | float = None,
        eighthX: int | float = None,
        eighthY: int | float = None,
        ninthX: int | float = None,
        ninthY: int | float = None,
    ):
        """Adds Elliot Wave tool to the chart. Draws a wave pattern between several control points.

        Args:
            waveType (int): Type of Elliot Wave.
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            secondX (int | float, optional): Second point X-position. Defaults to None.
            secondY (int | float, optional): Second point Y-position. Defaults to None.
            thirdX (int | float, optional): Third point X-position. Defaults to None.
            thirdY (int | float, optional): Third point Y-position. Defaults to None.
            fourthX (int | float, optional): Fourth point X-position. Defaults to None.
            fourthY (int | float, optional): Fourth point Y-position. Defaults to None.
            fifthX (int | float, optional): Fifth point X-position. Defaults to None.
            fifthY (int | float, optional): Fifth point Y-position. Defaults to None.
            sixthX (int | float, optional): Sixth point X-position. Defaults to None.
            sixthY (int | float, optional): Sixth point Y-position. Defaults to None.
            seventhX (int | float, optional): Seventh point X-position. Defaults to None.
            seventhY (int | float, optional): Seventh point Y-position. Defaults to None.
            eighthX (int | float, optional): Eighth point X-position. Defaults to None.
            eighthY (int | float, optional): Eighth point Y-position. Defaults to None.
            ninthX (int | float, optional): Ninth point X-position. Defaults to None.
            ninthY (int | float, optional): Ninth point Y-position. Defaults to None.
        """
        return ElliotWave(
            self,
            waveType,
            startX,
            startY,
            secondX,
            secondY,
            thirdX,
            thirdY,
            fourthX,
            fourthY,
            fifthX,
            fifthY,
            sixthX,
            sixthY,
            seventhX,
            seventhY,
            eighthX,
            eighthY,
            ninthX,
            ninthY,
        )

    def add_ellipse(
        self,
        startX: int | float,
        startY: int | float,
        radiusX: int | float = None,
        radiusY: int | float = None,
    ):
        """Adds an Ellipse to the chart.

        Args:
            startX (int | float): Start point X-position. If radius parameters are not supplied, this is where the drawing starts. Otherwise, this is the center X-value of the ellipse.
            startY (int | float): Start point Y-position. If radius parameters are not supplied, this is where the drawing starts. Otherwise, this is the center Y-value of the ellipse.
            radiusX (int | float, optional): Radius of the ellipse in X-direction. Defaults to None.
            radiusY (int | float, optional): Radius of the ellipse in Y-direction. Defaults to None.
        """
        return Ellipse(self, startX=startX, startY=startY, radiusX=radiusX, radiusY=radiusY)

    def add_extended_line(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Extended Line tool to the chart. Draws a straight line between two control points, then extends the line to the left and right edges of the chart.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return ExtendedLine(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_fibonacci_arc(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Fibonacci Arc tool to the chart. Draws a trend line between two control points, followed by multiple arcs intersecting the line at levels 38.2%, 50.0%, 61.8% and 100%. The arcs are centered on the second control point.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return FibonacciArc(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_fibonacci_extension(
        self,
        firstX: int | float,
        firstY: int | float,
        secondX: int | float = None,
        secondY: int | float = None,
        thirdX: int | float = None,
        thirdY: int | float = None,
    ):
        """Adds Fibonacci Extension tool to the chart. Fibonacci Extensions are based on three chosen points on chart: the first two points determine the price move while the third point is the end of retracement against that move. Extension lines using Fibonacci ratios are then drawn based on the price moves.

        Args:
            firstX (int | float): First point X-position.
            firstY (int | float): First point Y-position.
            secondX (int | float, optional): Second point X-position. Defaults to None.
            secondY (int | float, optional): Second point Y-position. Defaults to None.
            thirdX (int | float, optional): Third point X-position. Defaults to None.
            thirdY (int | float, optional): Third point Y-position. Defaults to None.
        """
        return FibonacciExtension(
            self,
            firstX=firstX,
            firstY=firstY,
            secondX=secondX,
            secondY=secondY,
            thirdX=thirdX,
            thirdY=thirdY,
        )

    def add_fibonacci_fan(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Fibonacci Fan tool to the chart. Draws a trend line between two control points, then several Fibonacci fan lines starting from the first point and crossing an “invisible” vertical line at the X-value of the second point based on Fibonacci levels at 38.2%, 50.0% and 61.8%.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return FibonacciFan(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_fibonacci_retracements(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Fibonacci Retracements tool to the chart. Draws a trend line between two control points, then several horizontal retracement lines based on selected price range (height) of the trend line. The retracement lines are drawn at Fibonacci levels of 38.2%, 50.0% and 61.8%.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return FibonacciRetracements(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_fibonacci_time_zones(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Fibonacci Time Zones tool to the chart. Draws vertical lines corresponding to elapsed time periods based on Fibonacci number sequence. Can be used to spot potential price reversal points.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return FibonacciTimeZones(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_flat_top_bottom(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
        flatYValue: int | float = None,
    ):
        """Adds Flat Top/Bottom tool to the chart. Draws a line between two points and another horizontal line above or below it. The area between the lines is then colored.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
            flatYValue (int | float, optional): The price value of the flat horizontal line. Defaults to None.
        """
        return FlatTopBottom(
            self,
            startX=startX,
            startY=startY,
            endX=endX,
            endY=endY,
            flatYValue=flatYValue,
        )

    def add_head_and_shoulders(
        self,
        startX: int | float,
        startY: int | float,
        leftShoulderX: int | float = None,
        leftShoulderY: int | float = None,
        firstTroughX: int | float = None,
        firstTroughY: int | float = None,
        headX: int | float = None,
        headY: int | float = None,
        secondTroughX: int | float = None,
        secondTroughY: int | float = None,
        rightShoulderX: int | float = None,
        rightShoulderY: int | float = None,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Head and Shoulders pattern to the chart. Appears as a baseline with three peaks.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            leftShoulderX (int | float, optional): Left Shoulder point X-position. Defaults to None.
            leftShoulderY (int | float, optional): Left Shoulder point Y-position. Defaults to None.
            firstTroughX (int | float, optional): First Trough point X-position. Defaults to None.
            firstTroughY (int | float, optional): First Trough point Y-position. Defaults to None.
            headX (int | float, optional): Head point X-position. Defaults to None.
            headY (int | float, optional): Head point Y-position. Defaults to None.
            secondTroughX (int | float, optional): Second Trough point X-position. Defaults to None.
            secondTroughY (int | float, optional): Second Trough point Y-position. Defaults to None.
            rightShoulderX (int | float, optional): Right Shoulder point X-position. Defaults to None.
            rightShoulderY (int | float, optional): Right Shoulder point Y-position. Defaults to None.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return HeadAndShoulders(
            self,
            startX=startX,
            startY=startY,
            leftShoulderX=leftShoulderX,
            leftShoulderY=leftShoulderY,
            firstTroughX=firstTroughX,
            firstTroughY=firstTroughY,
            headX=headX,
            headY=headY,
            secondTroughX=secondTroughX,
            secondTroughY=secondTroughY,
            rightShoulderX=rightShoulderX,
            rightShoulderY=rightShoulderY,
            endX=endX,
            endY=endY,
        )

    def add_horizontal_line(self, yPosition: int | float):
        """Adds Horizontal Line to the chart. Draws a line across the whole chart.

        Args:
            yPosition (int | float): Y-position for the line.
        """
        return HorizontalLine(self, yPosition=yPosition)

    def add_horizontal_ray(self, xPosition: int | float, yPosition: int | float):
        """Adds Horizontal Ray to the chart. Draws a straight line from a selected point to the right edge of the chart.

        Args:
            xPosition (int | float): Starting point X-value for the ray.
            yPosition (int | float): Y-position for the line.
        """
        return HorizontalRay(self, xPosition=xPosition, yPosition=yPosition)

    def add_linear_regression_channel(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Linear Regression Channel tool to the chart. Calculates and draws a linear regression line between two control points. Then draws two channel lines, one above and one below the regression line based on the selected channel type.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return LinearRegressionChannel(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_parallel_channel(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
        channelHeight: int | float = None,
    ):
        """Adds Parallel Channel tool to the chart. Draws a line between two points and another parallel line above or below it, thus forming a channel. The middle value of the channel is displayed with a dashed line.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
            channelHeight (int | float, optional): The height of the channel in price values. Defaults to None.
        """
        return ParallelChannel(
            self,
            startX=startX,
            startY=startY,
            endX=endX,
            endY=endY,
            channelHeight=channelHeight,
        )

    def add_pitchfork(
        self,
        startX: int | float,
        startY: int | float,
        endX1: int | float = None,
        endY1: int | float = None,
        endX2: int | float = None,
        endY2: int | float = None,
    ):
        """Adds Pitchfork tool to the chart. Places three control points on the chart and draws a line from the first point through the midpoint of the other points. Can be used to identify support and resistance levels for a stock's price.

        Args:
            startX (int | float): First point X-position.
            startY (int | float): First point Y-position.
            endX1 (int | float, optional): Second point X-position. Defaults to None.
            endY1 (int | float, optional): Second point Y-position. Defaults to None.
            endX2 (int | float, optional): Third point X-position. Defaults to None.
            endY2 (int | float, optional): Third point Y-position. Defaults to None.
        """
        return Pitchfork(
            self,
            startX=startX,
            startY=startY,
            endX1=endX1,
            endY1=endY1,
            endX2=endX2,
            endY2=endY2,
        )

    def add_price_range(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds a Price Range measurement tool to the chart, which measures the price change between two points on the chart.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return PriceRange(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_rectangle(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds a Rectangle tool to the chart.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return Rectangle(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_text_box(self, positionX: int | float, positionY: int | float, text: str = 'Text'):
        """Adds a text box to the chart.

        Args:
            positionX (int | float): Text X-position.
            positionY (int | float): Text Y-position.
            text (str, optional): The text content. Defaults to 'Text'.
        """
        return TextBox(self, positionX=positionX, positionY=positionY, text=text)

    def add_plain_text(self, positionX: int | float, positionY: int | float, text: str = 'Text'):
        """Adds a simple text to the chart.

        Args:
            positionX (int | float): Text X-position.
            positionY (int | float): Text Y-position.
            text (str, optional): The text content. Defaults to 'Text'.
        """
        return PlainText(self, positionX=positionX, positionY=positionY, text=text)

    def add_trend_line(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Trend Line tool to the chart. Draws a straight line between two control points.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return TrendLine(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_triangle(
        self,
        startX: int | float,
        startY: int | float,
        endX1: int | float = None,
        endY1: int | float = None,
        endX2: int | float = None,
        endY2: int | float = None,
    ):
        """Adds a Triangle tool to the chart.

        Args:
            startX (int | float): First point X-position.
            startY (int | float): First point Y-position.
            endX1 (int | float, optional): Second point X-position. Defaults to None.
            endY1 (int | float, optional): Second point Y-position. Defaults to None.
            endX2 (int | float, optional): Third point X-position. Defaults to None.
            endY2 (int | float, optional): Third point Y-position. Defaults to None.
        """
        return Triangle(
            self,
            startX=startX,
            startY=startY,
            endX1=endX1,
            endY1=endY1,
            endX2=endX2,
            endY2=endY2,
        )

    def add_xabcd_pattern(
        self,
        startX: int | float,
        startY: int | float,
        positionAX: int | float = None,
        positionAY: int | float = None,
        positionBX: int | float = None,
        positionBY: int | float = None,
        positionCX: int | float = None,
        positionCY: int | float = None,
        positionDX: int | float = None,
        positionDY: int | float = None,
    ):
        """Adds a XABCD pattern tool to the chart.

        Args:
            startX (int | float): Start X-position (X-point)
            startY (int | float): Start Y-position (X-point)
            positionAX (int | float, optional): A-point X-position. Defaults to None.
            positionAY (int | float, optional): A-point Y-position. Defaults to None.
            positionBX (int | float, optional): B-point X-position. Defaults to None.
            positionBY (int | float, optional): B-point Y-position. Defaults to None.
            positionCX (int | float, optional): C-point X-position. Defaults to None.
            positionCY (int | float, optional): C-point Y-position. Defaults to None.
            positionDX (int | float, optional): D-point X-position. Defaults to None.
            positionDY (int | float, optional): D-point Y-position. Defaults to None.
        """
        return XABCDpattern(
            self,
            startX=startX,
            startY=startY,
            positionAX=positionAX,
            positionAY=positionAY,
            positionBX=positionBX,
            positionBY=positionBY,
            positionCX=positionCX,
            positionCY=positionCY,
            positionDX=positionDX,
            positionDY=positionDY,
        )

    def add_cycle_lines(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Cycle Lines tool to the chart.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return CycleLines(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def add_sine_wave(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float = None,
        endY: int | float = None,
    ):
        """Adds Sine Wave tool to the chart.

        Args:
            startX (int | float): Start point X-position.
            startY (int | float): Start point Y-position.
            endX (int | float, optional): End point X-position. Defaults to None.
            endY (int | float, optional): End point Y-position. Defaults to None.
        """
        return SineWave(self, startX=startX, startY=startY, endX=endX, endY=endY)

    def dispose_all_drawing_tools(self):
        """Disposes all current drawing tools."""
        self.instance.send(self.id, 'disposeAllDrawingTools', {})

    def change_time_range(self, index: int):
        """Programmatically changes the value of the time range selection element.

        Args:
            index (int): Index of the selected time range. See documentation for the correct values.

        """
        if 0 <= index <= 16:
            self.instance.send(self.id, 'changeTimeRange', {'index': index})
        else:
            raise ValueError('Index out of range. Valid range is from 0 to 16.')
        return self

    def set_time_range(self, start_time: datetime, end_time: datetime):
        """Sets the time range. Data values only within this range will be shown.

        Args:
            start_time (datetime): The start time for the range.
            end_time (datetime): The end time for the range.

        """
        # Convert datetime objects to string in ISO format (e.g., '2023-01-01T00:00:00')
        start_time_str = start_time.isoformat()
        end_time_str = end_time.isoformat()

        self.instance.send(
            self.id,
            'setTimeRange',
            {'startTime': start_time_str, 'endTime': end_time_str},
        )
        return self

    def set_price_chart_type(self, chart_type: str):
        """Set the price chart type.

        Args:
            chart_type (str): The type of the chart to set. Example values: 'CandleStick', 'Bar', 'Line', 'Mountain', 'HeikinAshi', 'Renko', 'Kagi', 'PointAndFigure'

        """
        valid_chart_types = [
            'CandleStick',
            'Bar',
            'Line',
            'Mountain',
            'HeikinAshi',
            'Renko',
            'Kagi',
            'PointAndFigure',
        ]
        if chart_type in valid_chart_types:
            self.instance.send(self.id, 'setPriceChartType', {'chartType': chart_type})
        else:
            raise ValueError(f'Invalid chart type: {chart_type}. Valid types are: {", ".join(valid_chart_types)}')
        return self

    def save_as_template(self, template_name: str = '_'):
        """Save the current chart layout as a template.

        Args:
            template_name (str): The name of the template file to save. Defaults to '_'.

        """
        self.instance.send(self.id, 'saveAsTemplate', {'fileName': template_name})
        return self

    def load_template(self):
        """Load a chart configuration from a template.

        This method will open a File Upload window to browse and load a previously saved template file.

        """
        self.instance.send(self.id, 'loadTemplate', {})
        return self

    def add_indicator(self, indicator_name: str, **kwargs):
        """Add a technical indicator to the chart.

        Args:
            indicator_name (str): The name of the indicator to add (e.g., 'SimpleMovingAverage', 'Aroon').
            **kwargs: Additional arguments specific to the indicator (e.g., period, fastPeriod, slowPeriod).

        """
        args = {'indicatorName': indicator_name}

        # Add any additional arguments provided (e.g., period, fastPeriod, slowPeriod)
        args.update(kwargs)

        self.instance.send(self.id, 'addIndicator', args)
        return self

    def add_secondary_symbol(self, symbol: str):
        """Add a secondary symbol to the chart for comparison.

        Args:
            symbol (str): The symbol to add as a secondary comparison.

        """
        self.instance.send(self.id, 'addSecondarySymbol', {'symbol': symbol})
        return self

    def add_symbol_search_results(self, response_array):
        """Add symbol search results to the chart.

        Args:
            response_array (list of list): An array of symbol search results, where each sublist can contain Symbol, Name, Region, and Currency.

        """
        self.instance.send(self.id, 'addSymbolSearchResults', {'responseArray': response_array})
        return self

    def set_open_interest_data(self, open_interest_data: list):
        """Sets new Open Interest data to the chart.

        Args:
            open_interest_data (list): A list of numbers representing the new Open Interest data.

        """
        self.instance.send(self.id, 'setOpenInterestData', {'openInterestData': open_interest_data})
        return self

    def remove_chart(self):
        """Removes and disposes of the chart.

        This method will remove the chart from the view and dispose of it properly.

        """
        self.instance.send(self.id, 'removeChart', {})
        return self

    def clear_everything(self):
        """Cleans the chart by removing all added data, indicators, drawing tools, and heatmaps."""
        self.instance.send(self.id, 'clearEverything', {})
        return self

    def restore_default_settings(self):
        """Restores the default chart and color settings.

        This method will reset the chart's visual settings to their defaults. Indicators and drawing tools will remain unaffected.

        """
        self.instance.send(self.id, 'restoreDefaultSettings', {})
        return self

    def set_axis_alignment(self, axes_on_right: bool):
        """Sets the alignment of the price axes.

        Args:
            axes_on_right (bool): Set True to place the price axes on the right side of the chart, False to place them on the left.

        """
        self.instance.send(self.id, 'setAxisAlignment', {'axesOnRight': axes_on_right})
        return self

    def set_color_theme(self, color_theme: str):
        """Sets the color theme of the chart.

        This method will change the chart's color theme and override all manually set colors.

        Args:
            color_theme (str): The new color theme. Example values: 'cyberSpace', 'darkGold', 'light', 'lightNature', 'turquoiseHexagon'.

        """
        self.instance.send(self.id, 'setColorTheme', {'colorTheme': color_theme})
        return self

    def set_currency(self, currency: str):
        """Manually sets the currency shown on the chart.

        Args:
            currency (str): The new currency to display.

        """
        self.instance.send(self.id, 'setCurrency', {'currency': currency})
        return self

    def set_data_packing(self, packing_enabled: bool):
        """Sets whether OHLC-data should be packed when showing a large number of data values.

        Enabling packing improves performance but may lose accuracy of the data.

        Args:
            packing_enabled (bool): Set True to enable packing, False to disable it.

        """
        self.instance.send(self.id, 'setDataPacking', {'packingEnabled': packing_enabled})
        return self

    def set_line_color(self, color: str):
        """Sets the color for Line and Mountain chart types.

        Args:
            color (str): The new color as a string in HEX format, e.g., '#FFFFFF'.

        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_negative_body_color(self, new_color: str):
        """Sets the color for negative candlesticks.

        Args:
            new_color (str): The new color for negative candlesticks as a string in HEX format, e.g., '#FF0000' for red.

        """
        self.instance.send(self.id, 'setNegativeBodyColor', {'newColor': new_color})
        return self

    def set_positive_body_color(self, new_color: str):
        """Sets the color for positive candlesticks.

        Args:
            new_color (str): The new color for positive candlesticks as a string in HEX format, e.g., '#00FF00' for green.

        """
        self.instance.send(self.id, 'setPositiveBodyColor', {'newColor': new_color})
        return self

    def set_negative_wick_color(self, new_color: str):
        """Sets the color for wicks (shadows) of negative candlesticks.

        Args:
            new_color (str): The new color for negative wicks as a string in HEX format, e.g., '#FF0000' for red.

        """
        self.instance.send(self.id, 'setNegativeWickColor', {'newColor': new_color})
        return self

    def set_positive_wick_color(self, new_color: str):
        """Sets the color for wicks (shadows) of positive candlesticks.

        Args:
            new_color (str): The new color for positive wicks as a string in HEX format, e.g., '#00FF00' for green.

        """
        self.instance.send(self.id, 'setPositiveWickColor', {'newColor': new_color})
        return self

    def set_ohlc_cursor_tracking(self, tracking_type: int):
        """Sets which value the cursor tracks and is shown in the price axis label.

        Args:
            tracking_type (int): The OHLCTrackingType value to track. Should be one of the following:
                0 for All (shows each of the OHLC-data values),
                1 for Open,
                2 for High,
                3 for Low,
                4 for Close,
                5 for CursorLocation (show the price value of the current cursor position).

        """
        self.instance.send(self.id, 'setOHLCCursorTracking', {'trackingType': tracking_type})
        return self

    def set_percent_scale(self, use_percentage: bool):
        """Allows showing price value changes as percentages.

        Args:
            use_percentage (bool): Set True to show price changes as percentages, False to show absolute values.

        """
        self.instance.send(self.id, 'setPercentScale', {'usePercentage': use_percentage})
        return self

    def set_result_table_position(self, result_table_position: int):
        """Sets the visibility and the position of the result table.

        Args:
            result_table_position (int): The position of the result table. Should be one of the following:
                0 for Hidden,
                1 for TopLeft (top-left corner of the chart),
                2 for CursorLocation (shown next to the cursor).

        """
        self.instance.send(
            self.id,
            'setResultTablePosition',
            {'resultTablePosition': result_table_position},
        )
        return self

    def set_volume_data(self, volume_data: list):
        """Sets new Volume data to the chart.

        Note that if the length of the Volume data array is different from the length of the current OHLC-data set,
        some indicators cannot be calculated correctly.

        Args:
            volume_data (list): A list of numbers representing the new Volume data.

        """
        self.instance.send(self.id, 'setVolumeData', {'volumeData': volume_data})
        return self

    def show_symbol_watermark(self, show_symbol_watermark: bool):
        """Shows or hides the symbol watermark written on the middle of the price chart.

        Args:
            show_symbol_watermark (bool): Set True to show the watermark, False to hide it.

        """
        self.instance.send(
            self.id,
            'showSymbolWatermark',
            {'showSymbolWatermark': show_symbol_watermark},
        )
        return self

    def set_watermark_text(self, watermark_text: str):
        """Sets the text shown in the symbol watermark.

        Note: `showSymbolWatermark` needs to be set to True for the text to show up.

        Args:
            watermark_text (str): The new watermark text to display.

        """
        self.instance.send(self.id, 'setWatermarkText', {'watermarkText': watermark_text})
        return self

    def show_horizontal_cursor_line(self, show_line: bool):
        """Shows or hides the horizontal cursor line and its label.

        Args:
            show_line (bool): Set True to show the horizontal cursor line, False to hide it.

        """
        self.instance.send(self.id, 'showHorizontalCursorLine', {'showLine': show_line})
        return self

    def show_vertical_cursor_line(self, show_line: bool):
        """Shows or hides the vertical cursor line and its label.

        Args:
            show_line (bool): Set True to show the vertical cursor line, False to hide it.

        """
        self.instance.send(self.id, 'showVerticalCursorLine', {'showLine': show_line})
        return self

    def show_searchbar(self, show_searchbar: bool):
        """Shows or hides the search bar for symbols.

        Args:
            show_searchbar (bool): Set True to show the search bar, False to hide it.

        """
        self.instance.send(self.id, 'showSearchbar', {'showSearchbar': show_searchbar})
        return self

    def show_theme_image(self, show_theme_image: bool):
        """Shows or hides the background image.

        This works with Cyber Space and Turquoise Hexagon themes.

        Args:
            show_theme_image (bool): Set True to show the image, False to hide it.

        """
        self.instance.send(self.id, 'showThemeImage', {'showThemeImage': show_theme_image})
        return self

    def show_toolbar(self, show_toolbar: bool):
        """Shows or hides the whole toolbar on the left side of the chart.

        This includes data addition UI like "Dataset from file" button, time range selection,
        and all the settings buttons in the top-right corner.

        Args:
            show_toolbar (bool): Set True to show the toolbar, False to hide it.

        """
        self.instance.send(self.id, 'showToolbar', {'showToolbar': show_toolbar})
        return self

    def show_zoom_band_chart(self, show_zoom_band_chart: bool):
        """Shows or hides the zoom band chart below the main chart.

        When enabled, the zoom band chart depicts the whole X-axis range of the main chart.

        Args:
            show_zoom_band_chart (bool): Set True to show the zoom band chart, False to hide it.

        """
        self.instance.send(self.id, 'showZoomBandChart', {'showZoomBandChart': show_zoom_band_chart})
        return self

    def add_heatmap(self, start_x, start_y, end_x, end_y, data_values):
        """Adds a heatmap visualization to the chart.

        A heatmap is a graphical representation of data where individual values are represented as colors.
        It helps to visualize complex data and identify patterns within the chart.

        Args:
            start_x (float): The starting X-coordinate for the heatmap.
            start_y (float): The starting Y-coordinate for the heatmap.
            end_x (float): The ending X-coordinate for the heatmap.
            end_y (float): The ending Y-coordinate for the heatmap.
            data_values (list): A 2D array of data values used to generate the heatmap, where each value represents a color intensity.
        """
        return Heatmap(self, start_x, start_y, end_x, end_y, data_values)

    def dispose_all_heatmaps(self):
        """Disposes all heatmaps from the chart."""
        self.instance.send(self.id, 'disposeAllHeatmaps', {})
        return self

    def show_splitter_lines(self, show_splitter_lines: bool):
        """Shows or hides splitter lines between the chart segments.

        When enabled, splitter lines between the chart segments are shown, and they can be dragged to resize the segments.

        Args:
            show_splitter_lines (bool): Set True to show splitter lines, False to hide them.

        """
        self.instance.send(self.id, 'showSplitterLines', {'showSplitterLines': show_splitter_lines})
        return self

    def add_gann_box(self, startX, startY, endX, endY, lineColor, lineWidth, areaColor):
        """Adds a Gann Box to the trading chart.

        Args:
            startX (float): X-coordinate of the starting point.
            startY (float): Y-coordinate of the starting point.
            endX (float): X-coordinate of the ending point.
            endY (float): Y-coordinate of the ending point.
            lineColor (str): Line color in HEX format.
            lineWidth (float): Line width.
            areaColor (str): Area fill color in HEX format.

        Returns:
            GannBox: The created Gann Box instance.
        """
        return GannBox(
            trader=self,
            startX=startX,
            startY=startY,
            endX=endX,
            endY=endY,
            lineColor=lineColor,
            lineWidth=lineWidth,
            areaColor=areaColor,
        )

    def add_gann_fan(self, startX, startY, endX, endY, lineColor, lineWidth):
        """Adds a Gann Fun to the trading chart.

        Args:
            startX (float): X-coordinate of the starting point.
            startY (float): Y-coordinate of the starting point.
            endX (float): X-coordinate of the ending point.
            endY (float): Y-coordinate of the ending point.
            lineColor (str): Line color in HEX format.
            lineWidth (float): Line width.
            areaColor (str): Area fill color in HEX format.

        Returns:
            GannFun: The created Gann Fun instance.
        """
        return GannFan(
            trader=self,
            startX=startX,
            startY=startY,
            endX=endX,
            endY=endY,
            lineColor=lineColor,
            lineWidth=lineWidth,
        )

    def show_chart_title(self, showTitle: bool):
        """ ""
        Shows or hides the chart title.

        Args:
            showTitle (bool): Set True to show the chart title, or False to hide it.
        """
        self.instance.send(self.id, 'showChartTitle', {'showTitle': showTitle})
        return self

    def zoom_to_fit(self):
        """
        Zooms the chart so that all data is visible.

        This method automatically adjusts the chart view to ensure all data points
        are displayed within the visible area.
        """
        self.instance.send(self.id, 'zoomToFit', {})
        return self

    def set_wheel_zooming(self, zooming_mode: int):
        """
        Sets the zooming mode for the mouse wheel.

        This method configures how the chart responds to mouse wheel zooming.
        The zooming behavior is also influenced by the vertical zooming setting.

        Args:
        zooming_mode (int): The desired wheel zooming mode, based on the following enumeration:
            - 0 (KeepEnd): Zooms towards the latest data points.
            - 1 (KeepStart): Zooms towards the earliest data points.
            - 2 (TowardPointer): Zooms towards the pointer location.
            - 3 (Centered): Zooms towards the center of the chart.
            - 4 (Off): Disables mouse wheel zooming.
        """
        self.instance.send(self.id, 'setWheelZooming', {'zoomingMode': zooming_mode})
        return self

    def set_rectangle_zooming_button(self, rectangleZoomingButton: int):
        """Sets the mouse button used for rectangle zooming.

        Args:
            rectangleZoomingButton (int): The mouse button to be used for rectangle zooming.
                Options are based on the `MouseButtonSelection` enumeration:
                - 0 (LeftButton): Use the left mouse button for interaction.
                - 1 (RightButton): Use the right mouse button for interaction.
                - 2 (MiddleButton): Use the middle mouse button for interaction.
                - 3 (Off): Disable rectangle zooming.

        Note:
            Rectangle zooming and panning cannot be assigned to the same mouse button.
        """
        self.instance.send(
            self.id,
            'setRectangleZoomingButton',
            {'rectangleZoomingButton': rectangleZoomingButton},
        )
        return self

    def set_panning_button(self, panningButton: int):
        """
        Sets the mouse button used for panning.

        Note: Panning and rectangle zooming cannot be assigned to the same button.

        Args:
            panningButton (int): Specifies the mouse button for panning.
                The value should be from the `MouseButtonSelection` enumeration:
                - 0 (LeftButton): Interaction is controlled by the left mouse button.
                - 1 (RightButton): Interaction is controlled by the right mouse button.
                - 2 (MiddleButton): Interaction is controlled by the middle mouse button.
                - 3 (Off): Interaction is disabled.
        """
        self.instance.send(self.id, 'setPanningButton', {'panningButton': panningButton})
        return self

    def set_vertical_zooming(self, verticalZooming: bool):
        """
        Enables or disables vertical zooming, affecting the Y-axis range.

        Args:
            verticalZooming (bool): Set True to enable vertical zooming, or False to disable it.
        """
        self.instance.send(self.id, 'setVerticalZooming', {'verticalZooming': verticalZooming})
        return self

    def set_vertical_panning(self, verticalPanning: bool):
        """
        Enables or disables vertical panning, affecting the Y-axis range.

        Args:
            verticalPanning (bool): Set True to enable vertical panning, or False to disable it.
        """
        self.instance.send(self.id, 'setVerticalPanning', {'verticalPanning': verticalPanning})
        return self

    def enable_x_axis_restrictions(self, enableRestrictions: bool):
        """
        Enables or disables X-axis restrictions.

        When enabled, the X-axis cannot be zoomed or panned outside the minimum and maximum
        values of the data set. Disabling this allows free zooming and panning, but other
        zoom/pan-related settings may still apply.

        Args:
            enableRestrictions (bool): Set True to enable X-axis restrictions, or False to disable them.
        """
        self.instance.send(
            self.id,
            'enableXAxisrestrictions',
            {'enableRestrictions': enableRestrictions},
        )
        return self

    def enable_y_axis_restrictions(self, enableRestrictions: bool):
        """
        Enables or disables Y-axis restrictions.

        When enabled, the Y-axis cannot be zoomed or panned outside the minimum and maximum
        values of the data set. Disabling this allows free zooming and panning, but other
        zoom/pan-related settings may still apply.

        Args:
            enableRestrictions (bool): Set True to enable Y-axis restrictions, or False to disable them.
        """
        self.instance.send(
            self.id,
            'enableYAxisrestrictions',
            {'enableRestrictions': enableRestrictions},
        )
        return self

    def enable_effects(self, enableEffect: bool):
        """
        Enables or disables chart effects.

        When enabled, a glow effect is added to most chart components.

        Args:
            enableEffect (bool): Set True to enable the glow effect, or False to disable it.
        """
        self.instance.send(self.id, 'enableEffects', {'enableEffect': enableEffect})
        return self

    def set_background_color(self, color: str):
        """
        Sets the background color of the entire chart, including both the margin and series areas.

        Note:
            The series area background color can also be controlled via the `setSeriesBackgroundColor` method.

        Args:
            color (str): New background color in HEX format, e.g., '#FFFFFF'.
        """
        self.instance.send(self.id, 'setBackgroundColor', {'newColor': color})
        return self

    def set_series_background_color(self, color: str, **kwargs):
        """Sets the background color of the series area where data is drawn.

        Args:
            color (str): The new background color in HEX format (e.g., #FFFFFF).
            **kwargs: Optional parameters for customizing the background fill style:
                - fillStyle (int, optional): The fill style for the background.
                    - 0 (Solid): Solid, single color fill (default).
                    - 1 (LinearGradient): Linear gradient fill using two colors.
                    - 2 (RadialGradient): Radial gradient fill using two colors.
                - gradientColor (str, optional): The second color used for gradients (in HEX format).
                - angle (float, optional): The angle of the linear gradient in degrees (0-360).
                - gradientSpeed (float, optional): Speed of gradient transition.
                    - 1 signifies even distribution between colors.
                    - Values smaller than 1 cause faster transitions.
                    - Values larger than 1 cause slower transitions.
                - positionX (float, optional): X-position of the radial gradient center.
                    - 0 = left edge, 1 = right edge.
                - positionY (float, optional): Y-position of the radial gradient center.
                    - 0 = bottom of the chart, 1 = top of the chart.
        """
        args = {'newColor': color, **kwargs}
        self.instance.send(self.id, 'setSeriesBackgroundColor', args)
        return self

    def set_background_image(self, source: str):
        """
        Set the chart background image.

        Args:
            source (str): The image source. This can be:
                - A URL (remote image).
                - A local file path.
                - An already Base64-encoded image string.
        """

        def to_base64(image_source):
            """Helper to convert an image to Base64 from URL or local file."""
            try:
                if image_source.startswith('http://') or image_source.startswith('https://'):
                    response = requests.get(image_source)
                    response.raise_for_status()
                    data = response.content
                else:
                    with open(image_source, 'rb') as f:
                        data = f.read()
                return 'data:image/png;base64,' + base64.b64encode(data).decode('utf-8')
            except Exception as e:
                print(f'Error loading image: {e}')
                return None

        if not source:
            raise ValueError('Image source is required.')

        if not source.startswith('data:image'):
            source = to_base64(source)

        self.instance.send(self.id, 'setBackgroundImage', {'imagePath': source})
        return self

    def show_file_selection(self, showFileSelection: bool):
        """
        Shows or hides the file selection button.

        Args:
            showFileSelection (bool): Set True to show the file selection button, or False to hide it.
        """
        self.instance.send(self.id, 'showFileSelection', {'showFileSelection': showFileSelection})
        return self

    def restore_default_background(self):
        """
        Restores the default background colors and settings.

        This method resets any custom background settings to the default configuration.
        """
        self.instance.send(self.id, 'restoreDefaultBackground', {})
        return self

    def get_renko_instance(self):
        """Retrieve the Renko instance for customizing Renko-specific settings."""
        return Renko(self.instance, self.id)

    def get_point_and_figure_instance(self):
        """Retrieve the Point-and-Figure instance for customizing Point-and-Figure-specific settings."""
        return PointAndFigure(self.instance, self.id)

    def get_kagi_instance(self):
        """
        Retrieve the Kagi instance for customizing Kagi-specific settings.
        """
        return Kagi(self.instance, self.id)

    def set_transparent_chart(self, transparent=bool):
        "Sets the chart to use transparent background"
        self.instance.send(self.id, 'setTransparentChart', {'transparent': transparent})
        return self

    def enable_mountain_gradient(self, mountainGradient=bool):
        "When enabled, mountain price chart type uses gradient coloring for fill."
        self.instance.send(self.id, 'enableMountainGradient', {'mountainGradient': mountainGradient})
        return self

    def zoom_to_range(self, start_time: datetime, end_time: datetime):
        """Zooms horizontally to given time range..

        Args:
            start_time (datetime): The start time for the range.
            end_time (datetime): The end time for the range.

        Examples:
            >>> start_time = datetime(2013, 3, 3)
            >>> end_time = datetime(2013, 4, 4)
            >>> chart.zoom_to_range(start_time, end_time)
        """
        start_time_str = start_time.isoformat()
        end_time_str = end_time.isoformat()

        self.instance.send(
            self.id,
            'zoomToRange',
            {'startTime': start_time_str, 'endTime': end_time_str},
        )
        return self

    def menu_options(self):
        """Returns the menu options manager for this trading chart.

        The menu options manager provides methods to control various menu-related
        settings and UI elements of the trading chart interface.

        Returns:
            MenuOptions: The menu options manager instance.

        Example:
            # Hide the chart title input
            trader.menu_options().show_chart_title_input(False)

            # Show the chart title input
            trader.menu_options().show_chart_title_input(True)

            # Method chaining is supported
            trader.menu_options().show_chart_title_input(False)
        """
        return MenuOptions(self)

    def get_data(self, single_array: bool = False):
        """Gets the current data set loaded to the chart as separate arrays or as a single XOHLC-type array.

        Important:
            This method should be used after the chart is opened with open() method.

        Args:
            single_array (bool): When enabled, returns the data set as a single XOHLC-typed array.
                            Does not contain DateTime values. Default = False.
        Returns:
            If single_array is True, returns the XOHLC-array.
            If single_array is False, returns an array of arrays containing:
            - Date array (dates in string format)
            - Array of Open values
            - Array of High values
            - Array of Low values
            - Array of Close values
        """
        result = self.instance.get(
            self.id,
            'getData',
            {'singleArray': single_array},
        )
        return result

    def get_search_button(self):
        """Gets the search input component. Can be used to subscribe to various events when using the search bar with user-defined data provider.

        Important:
            This method should be used after the chart is opened with open() method.

        Returns:
            The search input component.
        """
        result = self.instance.get(
            self.id,
            'getSearchButton',
            {},
        )
        return result

    def get_search_input(self):
        """Gets the search input component. Can be used to subscribe to various events when using the search bar with user-defined data provider.

        Important:
            This method should be used after the chart is opened with open() method.

        Returns:
            The search input component.S
        """
        return self.instance.get(self.id, 'getSearchInput', {})

    def get_symbol_search_result_table(self):
        """Gets the table component used to display Symbol search results. Each result is a separate table row. Can be used to subscribe to various events when using the search bar with user-defined data provider.

        Important:
            This method should be used after the chart is opened with open() method.

        Returns:
            Symbol search table component.
        """
        result = self.instance.get(
            self.id,
            'getSymbolSearchResultTable',
            {},
        )
        return result

    def get_time_range(self):
        """Gets the current time range of the chart. To get the current selected time range (time range button value), use getTimeRangeSelection() method.

        Important:
            This method should be used after the chart is opened with open() method.

        Returns:
            Array containing two Date values: start time and end time.

        """
        result = self.instance.get(
            self.id,
            'getTimeRange',
            {},
        )
        return result

    def get_time_range_selection(self):
        """Gets the current selected time range (time range button value). To get the exact time range start and end values, use getTimeRange() method.

        Important:
            This method should be used after the chart is opened with open() method.

        Returns:
            Selected time range button value as a number (0 = All, 1 = 10Y, 2 = 5Y, 3 = 3Y, 4 = 1Y, 5 = 6M, 6 = 3M, 7 = 1M, 8 = 10D, 9 = 5D, 10 = 1D, 11 = 12H, 12 = 3H, 13 = 1H, 14 = 30m, 15 = 10m, 16 = 1m)
        """
        result = self.instance.get(
            self.id,
            'getTimeRangeSelection',
            {},
        )
        return result

    def get_volume_data(self):
        """Gets the Volume data currently loaded to the chart.

        Important:
            This method should be used after the chart is opened with open() method.

        Returns:
            The Volume data array.
        """
        result = self.instance.get(
            self.id,
            'getVolumeData',
            {},
        )
        return result

    def technical_analysis_methods(self):
        """Returns instance of TechnicalAnalysisMethods class."""
        return TechnicalAnalysisMethods(self)

    def create_dashboard(self, rows: int, cols: int):
        """Creates a dashboard grid layout.

        Args:
            columns (int): The amount of columns in the dashboard.
            rows (int): The amount of rows in the dashboard.
        """
        self.instance.send(self.id, 'createDashboard', {'rows': rows, 'cols': cols})
        return Dashboard(self.instance, self.id, rows, cols)


class Dashboard:
    def __init__(self, instance, parent_chart_id, rows, cols):
        self.instance = instance
        self.parent_chart_id = parent_chart_id
        self.rows = rows
        self.cols = cols
        self.charts = {}

    def add_chart(self, chart_type: str, row_index: int, column_index: int, row_span: int = 1, column_span: int = 1, title: str = None):
        """Adds a chart to the dashboard at specified position.

        Args:
            chart_type (str): The type of the chart to set. Example values: 'CandleStick', 'Bar', 'Line', 'Mountain', 'HeikinAshi', 'Renko', 'Kagi', 'PointAndFigure'.
            row_index (int): Row index (0-based) where the chart will be located. First row is 0.
            column_index (int): Column index (0-based) where the chart will be located. First column is 0.
            row_span (int): How many rows the chart will occupy (height). Default = 1.
            column_span (int): How many columns the chart will occupy (width). Default = 1.
            title (str, optional): The title of the chart. If None, no title will be set. Default = None.
        """
        valid_chart_types = ['CandleStick', 'Bar', 'Line', 'Mountain', 'HeikinAshi', 'Renko', 'Kagi', 'PointAndFigure']

        if chart_type not in valid_chart_types:
            raise ValueError(f'Invalid chart type: {chart_type}. Valid types are: {", ".join(valid_chart_types)}')

        chart_id = str(uuid.uuid4()).split('-')[0]

        chart_config = {
            'chartId': chart_id,
            'chartType': chart_type,
            'rowIndex': row_index,
            'colIndex': column_index,
            'rowSpan': row_span,
            'colSpan': column_span,
        }

        if title is not None:
            chart_config['title'] = title

        self.instance.send(self.parent_chart_id, 'addChartToDashboard', chart_config)

        dashboard_chart = DashboardChart(self.instance, chart_id)
        self.charts[chart_id] = dashboard_chart
        return dashboard_chart

    def load_csv_to_all_charts(self, csv: str, dataset_name='', delimiter=','):
        """Load CSV data to all charts in the dashboard.

        Args:
            csv (str): Path to the CSV file or CSV file content as string.
            dataset_name (str, optional): Name of the dataset, shown as the chart title. Defaults to ''.
            delimiter (str, optional): Delimiter used in the CSV file. Defaults to ','.
        """
        for chart in self.charts.values():
            chart.load_csv(csv, dataset_name, delimiter)
        return self


class DashboardChart(TAChart):
    """Individual chart within a dashboard"""

    def __init__(self, instance, chart_id):
        self.instance = instance
        self.chart_id = chart_id
        self.id = chart_id
        self.point_count = 0
        self.settings = {}

    def set_chart_title(self, title: str):
        """Sets the title of this dashboard chart."""
        self.instance.send(self.chart_id, 'setChartTitle', {'title': title})
        return self
