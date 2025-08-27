import uuid
from .instance import Instance


class TechnicalAnalysisMethods:
    def __init__(self, trader):
        self.id = str(uuid.uuid4()).split('-')[0]
        self.trader = trader
        self.instance: Instance = trader.instance
        self.trader_id = trader.id
        self.instance.send(self.id, 'createTechnicalAnalysisMethods', {'traderID': trader.id})

    def calculate_welles_wilder_smoothing(self, data_values: list[int | float], n: int):
        """Calculates Welles Wilder Smoothing (WWS) for the data values using the given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.

        Returns:
            An array of WWS values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateWellesWilderSmoothing',
            {'dataValues': data_values, 'n': n},
        )
        return result

    def calculate_z_value(self, data_values: list[int | float], n: int, movingAverageType: int):
        """Calculates Z-Value values based on given moving average type and number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.
            movingAverageType: The type of moving average to use between 0 and 9.

        Returns:
            An array of Z-Values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateZValue',
            {'dataValues': data_values, 'n': n, 'movingAverageType': movingAverageType},
        )
        return result

    def calculate_williams_accumulation_distribution(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        use_volume: bool,
        volumes: list[int | float] = None,
    ):
        """Calculates Williams Accumulation Distribution (WAD) values.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            use_volume: Sets whether to take Volume into account during calculations.
            volumes: Volume values. Can be null if useVolume is set false (Volume values not incorporated into calculations).

        Returns:
            An array of WAD values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateWilliamsAccumulationDistribution',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'useVolume': use_volume,
                'volumes': volumes,
            },
        )
        return result

    def calculate_standard_deviation(self, data_values: list[int | float], n: int, movingAverageType: int):
        """Calculates Standard Deviation values using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.
            movingAverageType: The type of moving average to use between 0 and 9.

        Returns:
            An array of Standard Deviation values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateStandardDeviation',
            {'dataValues': data_values, 'n': n, 'movingAverageType': movingAverageType},
        )
        return result

    def calculate_accumulation_distribution(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        volumes: list[int | float],
    ):
        """Calculates Accumulation/distribution indicator (A/D) values based on given OHLC and Volume values.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            volumes: Volume values.

        Returns:
            An array of Accumulation/Distribution values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateAccumulationDistribution',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'volumes': volumes,
            },
        )
        return result

    def calculate_accumulative_swing_index(
        self,
        open_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        close_values: list[int | float],
        limit_move_value: int | float,
    ):
        """Calculates Accumulative Swing Index (ASI) values using given data and maximum price change (limit move) values.

        Args:
            open_values: OHLC-data Open values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            close_values: OHLC-data Close values.
            limit_move_value: Maximum price change in one direction.

        Returns:
            An array of Accumulative Swing Index values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateAccumulativeSwingIndex',
            {
                'openValues': open_values,
                'highValues': high_values,
                'lowValues': low_values,
                'closeValues': close_values,
                'limitMoveValue': limit_move_value,
            },
        )
        return result

    def calculate_aroon(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates Aroon Up and Aroon Down values using given number of time periods (n).

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: Time period count.

        Returns:
            An array containing two arrays, the first one has Aroon Up values and the second one Aroon Down values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateAroon',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_aroon_oscillator(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates Aroon Oscillator values using given number of time periods (n).

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: Time period count.

        Returns:
            An array of Aroon Oscillator values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateAroonOscillator',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_average_directional_index(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates Average Directional Index (ADX) values. Returns also values for Directional Movement Indicators (-DI and +DI).

        Args:
            close_values: OHLC data Close values.
            high_values: OHLC data High values.
            low_values: OHLC data Low values.
            n: Period count.

        Returns:
            An array containing three arrays, the first one has ADX values, the second one -DI values, and the third one +DI values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateAverageDirectionalIndex',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_average_true_range(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates Average True Range values using given number of time periods (n).

        Args:
            close_values: OHLC data Close values.
            high_values: OHLC data High values.
            low_values: OHLC data Low values.
            n: Period count.

        Returns:
            An array of Average True Range values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateAverageTrueRange',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_awesome_oscillator(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        short_period_count: int,
        long_period_count: int,
    ):
        """Calculates Awesome Oscillator values using given short-term and long-term time period counts.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            short_period_count: Short-term period count.
            long_period_count: Long-term period count.

        Returns:
            An array of Awesome Oscillator values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateAwesomeOscillator',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'shortPeriodCount': short_period_count,
                'longPeriodCount': long_period_count,
            },
        )
        return result

    def calculate_balance_of_power(
        self,
        open_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        close_values: list[int | float],
        n: int,
        moving_average_type: int,
    ):
        """Calculates Balance of Power (BOP) values using given moving average type and number of time periods (n) for smoothing.

        Args:
            open_values: OHLC-data Open values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            close_values: OHLC-data Close values.
            n: Time period count.
            moving_average_type: The type of moving average to use between 0 and 9.

        Returns:
            An array of Balance of Power values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateBalanceOfPower',
            {
                'openValues': open_values,
                'highValues': high_values,
                'lowValues': low_values,
                'closeValues': close_values,
                'n': n,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_bollinger_band(
        self,
        source_values: list[int | float],
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
        standard_deviation_multiplier: int | float,
    ):
        """Calculates Bollinger Band values based on given number of time periods.

        Args:
            source_values: Data values used as a basis for calculations, most commonly OHLC-data Close values.
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: Period count.
            standard_deviation_multiplier: Number of standard deviations between the moving average line and the upper and the lower bands.

        Returns:
            An array containing three arrays. The first array has the middle band values, the second has the upper band values, and the third one the lower band values. Returns null if calculations are not possible with given parameters.
        """
        result = self.instance.get(
            self.id,
            'calculateBollingerBand',
            {
                'sourceValues': source_values,
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
                'standardDeviationMultiplier': standard_deviation_multiplier,
            },
        )
        return result

    def calculate_center_of_gravity(
        self,
        data_values: list[int | float],
        n: int,
        signal_periods: int,
    ):
        """Calculates Center of Gravity (COG) values using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Period count.
            signal_periods: Period count for the Signal line.

        Returns:
            An array containing two arrays: the first one has COG values and the second one Signal values.
        """
        result = self.instance.get(
            self.id,
            'calculateCenterOfGravity',
            {
                'dataValues': data_values,
                'n': n,
                'signalPeriods': signal_periods,
            },
        )
        return result

    def calculate_chaikin_money_flow(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        volumes: list[int | float],
        period_count: int,
    ):
        """Calculates Chaikin Money Flow values using given number of time periods.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            volumes: Volume values.
            period_count: Period count.

        Returns:
            An array of Chaikin Money Flow values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateChaikinMoneyFlow',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'volumes': volumes,
                'periodCount': period_count,
            },
        )
        return result

    def calculate_chaikin_oscillator(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        volumes: list[int | float],
        fast_period_count: int,
        slow_period_count: int,
    ):
        """Calculates Chaikin Oscillator values using given number of fast and slow time periods.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            volumes: Volume values.
            fast_period_count: Fast period count.
            slow_period_count: Slow period count.

        Returns:
            An array of Chaikin Oscillator values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateChaikinOscillator',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'volumes': volumes,
                'fastPeriodCount': fast_period_count,
                'slowPeriodCount': slow_period_count,
            },
        )
        return result

    def calculate_chaikin_volatility(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        period_count: int,
        period_count_ma: int,
        moving_average_type: int,
    ):
        """Calculates Chaikin Volatility using given values and moving average.

        Args:
        high_values: OHLC-data High values.
        low_values: OHLC-data Low values.
        period_count: Period count for Chaikin Volatility.
        period_count_ma: Period count for the moving average used in calculations.
        moving_average_type: Moving average type (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of Chaikin Volatility values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateChaikinVolatility',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'periodCount': period_count,
                'periodCountMA': period_count_ma,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_chande_forecast_oscillator(
        self,
        data_values: list[int | float],
        n: int,
    ):
        """Calculates Chande Forecast Oscillator (CFO) values using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.

        Returns:
            An array of CFO values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateChandeForecastOscillator',
            {
                'dataValues': data_values,
                'n': n,
            },
        )
        return result

    def calculate_chande_momentum_oscillator(
        self,
        data_values: list[int | float],
        n: int,
    ):
        """Calculates Chande Momentum Oscillator (CMO) values using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.

        Returns:
            An array of CMO values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateChandeMomentumOscillator',
            {
                'dataValues': data_values,
                'n': n,
            },
        )
        return result

    def calculate_commodity_channel_index(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates Commodity Channel Index (CCI) values using given number of time periods (n).

        Args:
            close_values: OHLC data Close values.
            high_values: OHLC data High values.
            low_values: OHLC data Low values.
            n: Period count.

        Returns:
            Array of Commodity Channel Index values, or null if calculation is not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateCommodityChannelIndex',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_coppock_curve(
        self,
        data_values: list[int | float],
        period_count_long_roc: int,
        period_count_short_roc: int,
        period_count_wma: int,
    ):
        """Calculates Coppock Curve values using given time period counts.

        Args:
            data_values: Data values to calculate from.
            period_count_long_roc: Period count for long Rate of Change.
            period_count_short_roc: Period count for short Rate of Change.
            period_count_wma: Period count for Weighted Moving Average.

        Returns:
            An array of Coppock Curve values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateCoppockCurve',
            {
                'dataValues': data_values,
                'periodCountLongROC': period_count_long_roc,
                'periodCountShortROC': period_count_short_roc,
                'periodCountWMA': period_count_wma,
            },
        )
        return result

    def calculate_correlation_coefficient(
        self,
        data_values1: list[int | float],
        data_values2: list[int | float],
        n: int,
    ):
        """Calculates Correlation Coefficient between the two given datasets.

        Args:
            data_values1: First dataset values.
            data_values2: Second dataset values.
            n: Time period count.

        Returns:
            An array of Correlation Coefficient values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateCorrelationCoefficient',
            {
                'dataValues1': data_values1,
                'dataValues2': data_values2,
                'n': n,
            },
        )
        return result

    def calculate_detrended_price_oscillator(
        self,
        data_values: list[int | float],
        n: int,
        moving_average_type: int,
    ):
        """Calculates Detrended Price Oscillator (DPO) values using given moving average type and number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Period count.
            moving_average_type: Moving average to use during calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of DPO values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateDetrendedPriceOscillator',
            {
                'dataValues': data_values,
                'n': n,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_donchian_channels(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates values for Donchian Channels using given period count (n).

        Args:
            high_values: OHLC data High values.
            low_values: OHLC data Low values.
            n: Period count.

        Returns:
            An array containing three arrays. The first array has the upper band values, the second has the lower band values, and the third one the middle band values. Returns null if calculations are not possible with given parameters.
        """
        result = self.instance.get(
            self.id,
            'calculateDonchianChannels',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_ease_of_movement(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        volumes: list[int | float],
        n: int,
        scale: int | float,
        moving_average_type: int = 2,
    ):
        """Calculates Ease of Movement (EOM) values based on given number of time periods (n).

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            volumes: Volume values.
            n: Period count.
            scale: Scale for the Volume values to keep them compatible with the other values.
            moving_average_type: Moving average to use during calculations. Defaults to 2. (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of EOM values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateEaseOfMovement',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'volumes': volumes,
                'n': n,
                'scale': scale,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_ehler_fisher_transform(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        period_count: int,
        raw_smoothing_periods: int,
        fisher_smoothing_periods: int,
        signal_period_count: int,
    ):
        """Calculates Ehler Fisher Transform (EFT) values based on given time period counts.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            period_count: The number of overall time periods (lookup periods).
            raw_smoothing_periods: The number of time periods used for raw smoothing before fisher transform.
            fisher_smoothing_periods: The number of time periods used for final smoothing with EMA.
            signal_period_count: The number of time periods used to calculate the signal line.

        Returns:
            An array containing two arrays: the first one has EFT-values and the second one Signal values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateEhlerFisherTransform',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'periodCount': period_count,
                'rawSmoothingPeriods': raw_smoothing_periods,
                'fisherSmoothingPeriods': fisher_smoothing_periods,
                'signalPeriodCount': signal_period_count,
            },
        )
        return result

    def calculate_elder_ray_index(
        self,
        source_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
        moving_average_type: int,
    ):
        """Calculates Elder-Ray Index (Elder-Ray Power Indicator) using given moving average type and number of time periods (n).

        Args:
            source_values: Data values used as a basis for calculations, most commonly OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: Period count.
            moving_average_type: Moving average to use during calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing two arrays: the first one has Bull Power values and the second one Bear Power values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateElderRayIndex',
            {
                'sourceValues': source_values,
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_elder_thermometer_custom(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates custom Elder Thermometer using given number of time periods.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: Time period count.

        Returns:
            An array containing two arrays: Thermometer Bull values and Thermometer Bear values.
        """
        result = self.instance.get(
            self.id,
            'calculateElderThermometerCustom',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_elders_force_index(
        self,
        data_values: list[int | float],
        volumes: list[int | float],
        n: int,
    ):
        """Calculates Elder's Force Index (EFI) using the given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            volumes: Volume values.
            n: Period count.

        Returns:
            An array of EFI values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateEldersForceIndex',
            {
                'dataValues': data_values,
                'volumes': volumes,
                'n': n,
            },
        )
        return result

    def calculate_exponential_moving_average(
        self,
        values: list[int | float],
        n: int,
    ):
        """Calculates Exponential Moving Average using given number of time periods (n).

        Args:
            values: Data values to calculate from.
            n: The number of values to use in averaging each round (period count).

        Returns:
            Array of Exponential Moving Average values, or null if averaging is not possible for the given values.
        """
        result = self.instance.get(
            self.id,
            'calculateExponentialMovingAverage',
            {
                'values': values,
                'n': n,
            },
        )
        return result

    def calculate_fractal_chaos_bands(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        period_count: int,
    ):
        """Calculates Fractal Chaos Bands based on the given values and number of time periods.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            period_count: The number of bars/candles needed to form a fractal.

        Returns:
            An array containing two arrays; the first one has the upper band values and the second lower band values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateFractalChaosBands',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'periodCount': period_count,
            },
        )
        return result

    def calculate_fractal_chaos_oscillator(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        period_count: int,
    ):
        """Calculates Fractal Chaos Oscillator (FCO) using given number of time periods.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            period_count: The number of bars/candles needed to form a fractal.

        Returns:
            An array of FCO values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateFractalChaosOscillator',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'periodCount': period_count,
            },
        )
        return result

    def calculate_gopalakrishnan_range_index(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates Gopalakrishnan Range Index (GAPO) values based on given number of time periods (n).

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: Period count.

        Returns:
            An array of GAPO values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateGopalakrishnanRangeIndex',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_high_low_bands(
        self,
        data_values: list[int | float],
        n: int,
        percentage: int | float,
    ):
        """Calculates High Low Bands based on given data values and period count. Uses Triangular Moving Average to calculate the middle band.

        Args:
            data_values: Data values to calculate from.
            n: Period count.
            percentage: Percentage of the TMA line to position the upper and lower bands.

        Returns:
            An array containing three arrays. The first array has the middle band values, the second has the upper band values, and the third one the lower band values. Returns null if calculations are not possible with given parameters.
        """
        result = self.instance.get(
            self.id,
            'calculateHighLowBands',
            {
                'dataValues': data_values,
                'n': n,
                'percentage': percentage,
            },
        )
        return result

    def calculate_high_minus_low(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
    ):
        """Calculates High Minus Low values.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.

        Returns:
            An array of High Minus Low values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateHighMinusLow',
            {
                'highValues': high_values,
                'lowValues': low_values,
            },
        )
        return result

    def calculate_historical_volatility_index(
        self,
        data_values: list[int | float],
        n: int,
        periods_per_year: int,
        standard_deviations: int | float,
        use_moving_average: bool,
    ):
        """Calculates Historical Volatility Index (HVI) using given number of time periods.

        Args:
            data_values: Data values to calculate from.
            n: Period count.
            periods_per_year: The number of time periods used for annualizing the indicator.
            standard_deviations: The number of standard deviations used in calculations.
            use_moving_average: Whether Simple Moving average is used to smooth the standard deviations values during the calculations.

        Returns:
            An array of HVI values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateHistoricalVolatilityIndex',
            {
                'dataValues': data_values,
                'n': n,
                'periodsPerYear': periods_per_year,
                'standardDeviations': standard_deviations,
                'useMovingAverage': use_moving_average,
            },
        )
        return result

    def calculate_ichimoku_cloud(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        tenkan_sen_period_count: int,
        kijun_sen_period_count: int,
        senkou_span_b_period_count: int,
    ):
        """Calculates various values related to Ichimoku Cloud.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            tenkan_sen_period_count: Tenkan-Sen (Conversion Line) period count.
            kijun_sen_period_count: Kijun-Sen (Base Line) period count.
            senkou_span_b_period_count: Senkou Span B (Leading Span B) period count.

        Returns:
            An array of arrays containing: Tenkan-Sen, Kijun-Sen, Senkou Span A, and Senkou Span B values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateIchimokuCloud',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'tenkanSenPeriodCount': tenkan_sen_period_count,
                'kijunSenPeriodCount': kijun_sen_period_count,
                'senkouSpanBPeriodCount': senkou_span_b_period_count,
            },
        )
        return result

    def calculate_intraday_momentum_index(
        self,
        open_values: list[int | float],
        close_values: list[int | float],
        n: int,
    ):
        """Calculates Intraday Momentum Index (IMI) values using given number of time periods (n).

        Args:
            open_values: OHLC-data Open values.
            close_values: OHLC-data Close values.
            n: Period count.

        Returns:
            An array of IMI values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateIntradayMomentumIndex',
            {
                'openValues': open_values,
                'closeValues': close_values,
                'n': n,
            },
        )
        return result

    def calculate_keltner_channels(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        period_count_ema: int,
        period_count_atr: int,
        multiplier: int | float,
    ):
        """Calculates values Keltner Channels. Uses Exponential Moving Average (EMA) of the typical price for the middle line and Average True Range (ATR) for the upper and lower bands.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            period_count_ema: Period count for EMA.
            period_count_atr: Period count for ATR.
            multiplier: Multiplier for ATR.

        Returns:
            An array containing three arrays: an array for EMA values, an array for upper channel values, and an array for lower channel values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateKeltnerChannels',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'periodCountEMA': period_count_ema,
                'periodCountATR': period_count_atr,
                'multiplier': multiplier,
            },
        )
        return result

    def calculate_klinger_volume_oscillator(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        volumes: list[int | float],
        short_period_count: int,
        long_period_count: int,
        signal_period_count: int,
        moving_average_type: int,
        moving_average_signal: int,
    ):
        """Calculates Klinger Volume Oscillator (KVO) using given time period count and moving average types.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            volumes: Volume values.
            short_period_count: Time period count for the shorter moving average.
            long_period_count: Time period count for the longer moving average.
            signal_period_count: Time period count for the Signal line.
            moving_average_type: Moving average to use during calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            moving_average_signal: Moving average used to calculate the Signal line (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing three arrays. The first has the KVO values, the second the Signal values, and the third has the histogram values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateKlingerVolumeOscillator',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'volumes': volumes,
                'shortPeriodCount': short_period_count,
                'longPeriodCount': long_period_count,
                'signalPeriodCount': signal_period_count,
                'movingAverageType': moving_average_type,
                'movingAverageSignal': moving_average_signal,
            },
        )
        return result

    def calculate_kurtosis(
        self,
        data_values: list[int | float],
        n: int,
        moving_average_type: int,
    ):
        """Calculates Kurtosis values based on given moving average type and number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Period count.
            moving_average_type: Moving average to use during calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of Kurtosis values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateKurtosis',
            {
                'dataValues': data_values,
                'n': n,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_linear_regression(
        self,
        data_values: list[int | float],
        period_count: int,
    ):
        """Calculates Linear Regression indicator values using given number of time periods.

        Args:
            data_values: Data values to calculate from.
            period_count: Time period count.

        Returns:
            An array containing four data arrays: Linear Regression Slope, Intercept, Forecast, and R Squared values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateLinearRegression',
            {
                'dataValues': data_values,
                'periodCount': period_count,
            },
        )
        return result

    def calculate_macd(
        self,
        data_values: list[int | float],
        long_period: int,
        short_period: int,
        signal_period: int,
    ):
        """Calculates MACD, Signal Line, and Histogram.

        Args:
            data_values: Data values to calculate from.
            long_period: Long period count.
            short_period: Short period count.
            signal_period: Signal period count.

        Returns:
            An array containing three arrays: MACD values, Signal values, and Histogram values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateMACD',
            {
                'dataValues': data_values,
                'longPeriod': long_period,
                'shortPeriod': short_period,
                'signalPeriod': signal_period,
            },
        )
        return result

    def calculate_macd_custom(
        self,
        data_values: list[int | float],
        short_period: int,
        long_period: int,
        signal_period: int,
        moving_average_short: int,
        moving_average_long: int,
        moving_average_signal: int,
    ):
        """Calculates MACD, Signal Line, and Histogram using given moving average types.

        Args:
            data_values: Data values to calculate from.
            short_period: Short period count.
            long_period: Long period count.
            signal_period: Signal period count.
            moving_average_short: Moving average type (0-9) for short moving average (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            moving_average_long: Moving average type (0-9) for long moving average (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            moving_average_signal: Moving average type (0-9) for signal line (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing three arrays: MACD values, Signal values, and Histogram values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateMACDCustom',
            {
                'dataValues': data_values,
                'shortPeriod': short_period,
                'longPeriod': long_period,
                'signalPeriod': signal_period,
                'movingAverageShort': moving_average_short,
                'movingAverageLong': moving_average_long,
                'movingAverageSignal': moving_average_signal,
            },
        )
        return result

    def calculate_market_facilitation_index(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        volumes: list[int | float],
    ):
        """Calculates Market Facilitation Index values.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            volumes: Volume values.

        Returns:
            An array containing two arrays: MFI values and bar colors as numbers (1=green, 2=blue, 3=pink, 4=brown). Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateMarketFacilitationIndex',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'volumes': volumes,
            },
        )
        return result

    def calculate_mass_index(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates Mass Index values using given number of time periods (n).

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: Period count.

        Returns:
            An array of Mass Index values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateMassIndex',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_median_price(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
    ):
        """Calculates Median Prices based on given High and Low values.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.

        Returns:
            An array of Median Prices, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateMedianPrice',
            {
                'highValues': high_values,
                'lowValues': low_values,
            },
        )
        return result

    def calculate_momentum_oscillator(
        self,
        data_values: list[int | float],
        n: int,
    ):
        """Calculates Momentum Oscillator values using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Period count.

        Returns:
            An array of Momentum Oscillator values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateMomentumOscillator',
            {
                'dataValues': data_values,
                'n': n,
            },
        )
        return result

    def calculate_money_flow_index(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        volumes: list[int | float],
        n: int,
    ):
        """Calculates Money Flow Index values using given number of time periods (n).

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            volumes: Volume values.
            n: Period count.

        Returns:
            An array of Money Flow Index values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateMoneyFlowIndex',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'volumes': volumes,
                'n': n,
            },
        )
        return result

    def calculate_moving_average_envelopes(
        self,
        data_values: list[int | float],
        n: int,
        percentage: int | float,
        moving_average_type: int,
    ):
        """Calculates Moving Average Envelopes based on given values and moving average type.

        Args:
            data_values: Data values to calculate from.
            n: Period count for the moving average.
            percentage: Percentage of the moving average line to position the upper and lower bands.
            moving_average_type: The moving average type used to calculate the envelopes (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing three arrays. The first array has the middle band values, the second has the upper band values, and the third one the lower band values. Returns null if calculations are not possible with given parameters.
        """
        result = self.instance.get(
            self.id,
            'calculateMovingAverageEnvelopes',
            {
                'dataValues': data_values,
                'n': n,
                'percentage': percentage,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_negative_volume_index(
        self,
        data_values: list[int | float],
        volumes: list[int | float],
    ):
        """Calculates Negative Volume Index (NVI) values based on given data and volume values.

        Args:
            data_values: Data values to calculate from.
            volumes: Volume values.

        Returns:
            An array of NVI values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateNegativeVolumeIndex',
            {
                'dataValues': data_values,
                'volumes': volumes,
            },
        )
        return result

    def calculate_on_balance_volume(
        self,
        data_values: list[int | float],
        volumes: list[int | float],
        start_obv: int | float = 0,
    ):
        """Calculates On-Balance Volume values based on given data and Volume values.

        Args:
            data_values: Data values to calculate from.
            volumes: Volume values.
            start_obv: Optional starting value to which Volume values are added or subtracted from. Defaults to 0.

        Returns:
            An array of On-Balance Volume values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateOnBalanceVolume',
            {
                'dataValues': data_values,
                'volumes': volumes,
                'startOBV': start_obv,
            },
        )
        return result

    def calculate_parabolic_sar(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        acceleration_factor: int | float,
        maximum_acceleration_factor: int | float,
    ):
        """Calculates Parabolic SAR values using given values.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            acceleration_factor: Acceleration Factor. Used as an initial values and as an incremental value.
            maximum_acceleration_factor: Maximum value for Acceleration Factor.

        Returns:
            An array of Parabolic SAR values. Return null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateParabolicSAR',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'accelerationFactor': acceleration_factor,
                'maximumAccelerationFactor': maximum_acceleration_factor,
            },
        )
        return result

    def calculate_percentage_price_oscillator(
        self,
        data_values: list[int | float],
        long_period: int,
        short_period: int,
        signal_period: int,
    ):
        """Calculates Percentage Price Oscillator values using given number of time periods (n). Returns also Signal and Histogram values.

        Args:
            data_values: Data values to calculate from.
            long_period: Long period count.
            short_period: Short period count.
            signal_period: Signal period count.

        Returns:
            An array containing three arrays: PPO values, Signal values, and Histogram values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculatePercentagePriceOscillator',
            {
                'dataValues': data_values,
                'longPeriod': long_period,
                'shortPeriod': short_period,
                'signalPeriod': signal_period,
            },
        )
        return result

    def calculate_performance_index(
        self,
        data_values: list[int | float],
    ):
        """Calculates Performance Index values.

        Args:
            data_values: Data values to calculate from.

        Returns:
            An array of Performance Index values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculatePerformanceIndex',
            {
                'dataValues': data_values,
            },
        )
        return result

    def calculate_positive_volume_index(
        self,
        data_values: list[int | float],
        volumes: list[int | float],
    ):
        """Calculates Positive Volume Index (PVI) values based on given data and volume values.

        Args:
            data_values: Data values to calculate from.
            volumes: Volume values.

        Returns:
            An array of PVI values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculatePositiveVolumeIndex',
            {
                'dataValues': data_values,
                'volumes': volumes,
            },
        )
        return result

    def calculate_pretty_good_oscillator(
        self,
        source_values: list[int | float],
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        period_count_ma: int,
        period_count_atr: int,
        moving_average_ma: int,
        moving_average_atr: int,
    ):
        """Calculates Pretty Good Oscillator (PGO) values using given number of time periods and moving average types.

        Args:
            source_values: Data values used as a basis for calculations, most commonly OHLC-data Close values.
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            period_count_ma: The number of time periods used to calculate the moving averages.
            period_count_atr: The number of time periods used to calculate the Average True Range.
            moving_average_ma: The type of the OHLC-data based moving average (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            moving_average_atr: The type of the Average True Range based moving average (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of PGO values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculatePrettyGoodOscillator',
            {
                'sourceValues': source_values,
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'periodCountMA': period_count_ma,
                'periodCountATR': period_count_atr,
                'movingAverageMA': moving_average_ma,
                'movingAverageATR': moving_average_atr,
            },
        )
        return result

    def calculate_price_volume_trend(
        self,
        data_values: list[int | float],
        volumes: list[int | float],
    ):
        """Calculates Price Volume Trend (PVT) using given price and volume values.

        Args:
            data_values: Data values to calculate from.
            volumes: Volume values.

        Returns:
            An array of PVT values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculatePriceVolumeTrend',
            {
                'dataValues': data_values,
                'volumes': volumes,
            },
        )
        return result

    def calculate_prime_number_bands(
        self,
        data_values: list[int | float],
    ):
        """Calculates Prime Number Bands based on given values.

        Args:
            data_values: Data values to calculate from.

        Returns:
            An array containing two arrays. The first one has upper bands values and the second lower band values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculatePrimeNumberBands',
            {
                'dataValues': data_values,
            },
        )
        return result

    def calculate_prime_number_oscillator(
        self,
        data_values: list[int | float],
    ):
        """Calculates Prime Number Oscillator (PNO) values based on given data values.

        Args:
            data_values: Data values to calculate from.

        Returns:
            An array of PNO values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculatePrimeNumberOscillator',
            {
                'dataValues': data_values,
            },
        )
        return result

    def calculate_q_stick(
        self,
        open_values: list[int | float],
        close_values: list[int | float],
        n: int,
        moving_average_type: int,
    ):
        """Calculates QStick values using given moving average and number of time periods (n).

        Args:
            open_values: OHLC-data Open values.
            close_values: OHLC-data Close values.
            n: Period count.
            moving_average_type: Moving average to use during calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of QStick values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateQStick',
            {
                'openValues': open_values,
                'closeValues': close_values,
                'n': n,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_rainbow_oscillator(
        self,
        data_values: list[int | float],
        period_count: int,
        lookback_periods: int,
        smoothing_levels: int,
        moving_average_type: int,
    ):
        """Calculates Rainbow Oscillator values using given parameters and moving average type.

        Args:
            data_values: Data values to calculate from.
            period_count: The number of time periods used for calculating the series of moving averages.
            lookback_periods: The number of time periods checked when finding out the highest and lowest prices.
            smoothing_levels: The number of times the oscillator is smoothed by calculating a moving average.
            moving_average_type: Moving average type used for calculating the series of averages (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing three arrays: Rainbow Oscillator values, upper band values, and lower band values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateRainbowOscillator',
            {
                'dataValues': data_values,
                'periodCount': period_count,
                'lookbackPeriods': lookback_periods,
                'smoothingLevels': smoothing_levels,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_random_walk_index(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates Random Walk Index (RWI) values using given number of time periods (n).

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: Time period count.

        Returns:
            An array containing two arrays: RWI High values and RWI Low values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateRandomWalkIndex',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_range_action_verification_index(
        self,
        data_values: list[int | float],
        period_count_short: int,
        period_count_long: int,
        moving_average_short: int,
        moving_average_long: int,
    ):
        """Calculates Range Action Verification Index (RAVI) using given moving average types and time period counts.

        Args:
            data_values: Data values to calculate from.
            period_count_short: Period count for the shorter moving average.
            period_count_long: Period count for the longer moving average.
            moving_average_short: The type of the shorter moving average (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            moving_average_long: The type of the longer moving average (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of RAVI values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateRangeActionVerificationIndex',
            {
                'dataValues': data_values,
                'periodCountShort': period_count_short,
                'periodCountLong': period_count_long,
                'movingAverageShort': moving_average_short,
                'movingAverageLong': moving_average_long,
            },
        )
        return result

    def calculate_rate_of_change(
        self,
        data_values: list[int | float],
        n: int,
    ):
        """Calculates Rate of Change (ROC) values using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.

        Returns:
            Array of Rate of Change values, or null if calculation is not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateRateOfChange',
            {
                'dataValues': data_values,
                'n': n,
            },
        )
        return result

    def calculate_relative_strength_index(
        self,
        values: list[int | float],
        n: int,
    ):
        """Calculates Relative Strength Index (RSI) using given number of time periods, N.

        Args:
            values: Values to calculate from.
            n: Number of values over which the smoothing calculation is applied.

        Returns:
            Array of Relative Strength Index values, or null if calculations are not possible.
        """
        result = self.instance.get(
            self.id,
            'calculateRelativeStrengthIndex',
            {
                'values': values,
                'n': n,
            },
        )
        return result

    def calculate_sqn_trend(
        self,
        data_values: list[int | float],
        n: int,
        moving_average_type: int,
    ):
        """Calculates SQN Trend (System Quality Number) using given values, moving average type and number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.
            moving_average_type: Moving average type (0-9) used during calculations.

        Returns:
            An array of SQN Trend values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateSQNTrend',
            {
                'dataValues': data_values,
                'n': n,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_schaff_trend_cycle(
        self,
        data_values: list[int | float],
        macd_short_periods: int,
        macd_long_periods: int,
        first_stoch_periods: int,
        first_stoch_k_periods: int,
        first_stoch_d_periods: int,
        second_stoch_periods: int,
        second_stoch_k_periods: int,
        second_stoch_d_periods: int,
        macd_short_ma: int,
        macd_long_ma: int,
        first_stoch_k_ma: int,
        first_stoch_d_ma: int,
        second_stoch_k_ma: int,
        second_stoch_d_ma: int,
    ):
        """Calculates Schaff Trend Cycle (STC) values using given time period counts and moving averages.

        Args:
            data_values: Data values to calculate from.
            macd_short_periods: The short period count for MACD calculations.
            macd_long_periods: The long period count for MACD calculations.
            first_stoch_periods: The time period count used to calculate the first Stochastic, that is the lookback periods when finding the highest and lowest values.
            first_stoch_k_periods: The time period count used to smooth the first Stochastic (%K).
            first_stoch_d_periods: The time period count used to calculate the first %D values.
            second_stoch_periods: The time period count used to calculate the second Stochastic, that is the lookback periods when finding the highest and lowest values.
            second_stoch_k_periods: The time period count used to smooth the second Stochastic (%K).
            second_stoch_d_periods: The time period count used to calculate the second %D values, in other words the final STC values.
            macd_short_ma: Moving average type (0-9) to calculate the short moving average during MACD calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            macd_long_ma: Moving average type (0-9) to calculate the long moving average during MACD calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            first_stoch_k_ma: Moving average type (0-9) to calculate the first Stochastic %K values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            first_stoch_d_ma: Moving average type (0-9) to calculate the first Stochastic %D values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            second_stoch_k_ma: Moving average type (0-9) to calculate the second Stochastic %K values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            second_stoch_d_ma: Moving average type (0-9) to calculate the second Stochastic %D values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of STC values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateSchaffTrendCycle',
            {
                'dataValues': data_values,
                'macdShortPeriods': macd_short_periods,
                'macdLongPeriods': macd_long_periods,
                'firstStochPeriods': first_stoch_periods,
                'firstStochKPeriods': first_stoch_k_periods,
                'firstStochDPeriods': first_stoch_d_periods,
                'secondStochPeriods': second_stoch_periods,
                'secondStochKPeriods': second_stoch_k_periods,
                'secondStochDPeriods': second_stoch_d_periods,
                'macdShortMA': macd_short_ma,
                'macdLongMA': macd_long_ma,
                'firstStochKMA': first_stoch_k_ma,
                'firstStochDMA': first_stoch_d_ma,
                'secondStochKMA': second_stoch_k_ma,
                'secondStochDMA': second_stoch_d_ma,
            },
        )
        return result

    def calculate_schaff_trend_cycle_signal(
        self,
        data_values: list[int | float],
        macd_short_periods: int,
        macd_long_periods: int,
        macd_signal_periods: int,
        first_stoch_periods: int,
        first_stoch_k_periods: int,
        first_stoch_d_periods: int,
        second_stoch_periods: int,
        second_stoch_k_periods: int,
        second_stoch_d_periods: int,
        macd_short_ma: int,
        macd_long_ma: int,
        macd_signal_ma: int,
        first_stoch_k_ma: int,
        first_stoch_d_ma: int,
        second_stoch_k_ma: int,
        second_stoch_d_ma: int,
    ):
        """Calculates Schaff Trend Cycle (STC) values using given time period counts and moving averages. This version uses MACD's Signal line as basis for Stochastic calculations.

        Args:
            data_values: Data values to calculate from.
            macd_short_periods: The short period count for MACD calculations.
            macd_long_periods: The long period count for MACD calculations.
            macd_signal_periods: The signal period count for MACD calculations.
            first_stoch_periods: The time period count used to calculate the first Stochastic, that is the lookback periods when finding the highest and lowest values.
            first_stoch_k_periods: The time period count used to smooth the first Stochastic (%K).
            first_stoch_d_periods: The time period count used to calculate the first %D values.
            second_stoch_periods: The time period count used to calculate the second Stochastic, that is the lookback periods when finding the highest and lowest values.
            second_stoch_k_periods: The time period count used to smooth the second Stochastic (%K).
            second_stoch_d_periods: The time period count used to calculate the second %D values, in other words the final STC values.
            macd_short_ma: Moving average type (0-9) to calculate the short moving average during MACD calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            macd_long_ma: Moving average type (0-9) to calculate the long moving average during MACD calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            macd_signal_ma: Moving average type (0-9) to calculate the signal line during MACD calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            first_stoch_k_ma: Moving average type (0-9) to calculate the first Stochastic %K values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            first_stoch_d_ma: Moving average type (0-9) to calculate the first Stochastic %D values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            second_stoch_k_ma: Moving average type (0-9) to calculate the second Stochastic %K values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            second_stoch_d_ma: Moving average type (0-9) to calculate the second Stochastic %D values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of STC values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateSchaffTrendCycleSignal',
            {
                'dataValues': data_values,
                'macdShortPeriods': macd_short_periods,
                'macdLongPeriods': macd_long_periods,
                'macdSignalPeriods': macd_signal_periods,
                'firstStochPeriods': first_stoch_periods,
                'firstStochKPeriods': first_stoch_k_periods,
                'firstStochDPeriods': first_stoch_d_periods,
                'secondStochPeriods': second_stoch_periods,
                'secondStochKPeriods': second_stoch_k_periods,
                'secondStochDPeriods': second_stoch_d_periods,
                'macdShortMA': macd_short_ma,
                'macdLongMA': macd_long_ma,
                'macdSignalMA': macd_signal_ma,
                'firstStochKMA': first_stoch_k_ma,
                'firstStochDMA': first_stoch_d_ma,
                'secondStochKMA': second_stoch_k_ma,
                'secondStochDMA': second_stoch_d_ma,
            },
        )
        return result

    def calculate_simple_moving_average(
        self,
        values: list[int | float],
        n: int,
    ):
        """Calculates Simple Moving Average using given averaging frame length (window length, or period count N).

        Args:
            values: Data values to calculate from.
            n: The number of values to use in averaging each round (period count).

        Returns:
            Array of Simple Moving Average values, or null if averaging is not possible for the given values.
        """
        result = self.instance.get(
            self.id,
            'calculateSimpleMovingAverage',
            {
                'values': values,
                'n': n,
            },
        )
        return result

    def calculate_skewness(
        self,
        data_values: list[int | float],
        n: int,
        moving_average_type: int,
    ):
        """Calculates Skewness values based on given moving average type and number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.
            moving_average_type: The type of moving average (0-9) to use (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of Skewness values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateSkewness',
            {
                'dataValues': data_values,
                'n': n,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_standard_error(
        self,
        data_values: list[int | float],
        n: int,
        moving_average_type: int,
    ):
        """Calculates Standard Error values using given moving average and number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Period count.
            moving_average_type: Moving average type (0-9) to use during calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of Standard Error values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateStandardError',
            {
                'dataValues': data_values,
                'n': n,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_standard_error_bands(
        self,
        data_values: list[int | float],
        n: int,
        multiplier: int | float,
        moving_average_type: int,
    ):
        """Calculates Standard Error Bands values using given moving average type and number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.
            multiplier: Multiplier for the standard error used when calculating upper and lower bands.
            moving_average_type: The type of moving average (0-9) to use (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing three arrays. The first array has the middle band values, the second has the upper band values, and the third one the lower band values. Returns null if calculations are not possible with given parameters.
        """
        result = self.instance.get(
            self.id,
            'calculateStandardErrorBands',
            {
                'dataValues': data_values,
                'n': n,
                'multiplier': multiplier,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_stochastic_momentum_index(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        period_count: int,
        first_smooth_periods: int,
        double_smooth_periods: int,
        moving_average_periods: int,
        oscillator_moving_average: int,
        ma_moving_average: int,
    ):
        """Calculates Stochastic Momentum Index (SMI) values using given moving average types and time period counts.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            period_count: The number of time periods to calculate the stochastic (%K) line. This is the lookback period for High/Low range.
            first_smooth_periods: The number of time periods used for the first smoothing of the stochastic (%K) values.
            double_smooth_periods: The number of time periods used for the second (double) smoothing of the stochastic (%K) values.
            moving_average_periods: The number of time periods used to calculate the moving average (%D) line.
            oscillator_moving_average: The moving average type (0-9) used to smooth the oscillator (%K) line (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            ma_moving_average: The moving average type (0-9) used to calculate the moving average (%D) line (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of two arrays: the first one has SMI values (%K) while the second one has moving average values (%D). Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateStochasticMomentumIndex',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'periodCount': period_count,
                'firstSmoothPeriods': first_smooth_periods,
                'doubleSmoothPeriods': double_smooth_periods,
                'movingAveragePeriods': moving_average_periods,
                'oscillatorMovingAverage': oscillator_moving_average,
                'maMovingAverage': ma_moving_average,
            },
        )
        return result

    def calculate_stochastic_oscillator(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
        moving_average_periods: int,
    ):
        """Calculates Stochastic Oscillator values using given number of time periods (n).

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: The number of time periods used to calculate the oscillator.
            moving_average_periods: The number of time periods used to calculate the moving average.

        Returns:
            An array containing two arrays: Stochastic Oscillator values and moving average values. Returns null if calculation is not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateStochasticOscillator',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
                'movingAveragePeriods': moving_average_periods,
            },
        )
        return result

    def calculate_stochastic_oscillator_smoothed(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        oscillator_periods: int,
        oscillator_smoothing_periods: int,
        moving_average_periods: int,
        oscillator_moving_average: int,
        ma_moving_average: int,
    ):
        """Calculates Smoothed Stochastic Oscillator values using given moving average types and time period counts.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            oscillator_periods: The number of time periods used to calculate the stochastic (%K) values.
            oscillator_smoothing_periods: The number of time periods used to smooth the stochastic (%K) values.
            moving_average_periods: The number of time periods used to calculate the moving average (%D) values.
            oscillator_moving_average: The moving average type (0-9) used to smooth the stochastic (%K) values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            ma_moving_average: The moving average type (0-9) used to calculate the moving average (%D) values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing two arrays: stochastic (%K) values and moving average (%D) values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateStochasticOscillatorSmoothed',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'oscillatorPeriods': oscillator_periods,
                'oscillatorSmoothingPeriods': oscillator_smoothing_periods,
                'movingAveragePeriods': moving_average_periods,
                'oscillatorMovingAverage': oscillator_moving_average,
                'maMovingAverage': ma_moving_average,
            },
        )
        return result

    def calculate_stoller_average_channels(
        self,
        source_values: list[int | float],
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        period_count_ma: int,
        period_count_atr: int,
        multiplier: int | float,
        moving_average_type: int,
    ):
        """Calculates Stoller Average Range Channels (STARC) using given moving average type and number of time periods.

        Args:
            source_values: Data values used as a basis for calculations, most commonly OHLC-data Close values.
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            period_count_ma: Period count for the moving average.
            period_count_atr: Period count for the Average True Range.
            multiplier: Multiplier for the Average True Range.
            moving_average_type: The type of moving average (0-9) to use (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing three arrays: moving average values, upper channel values, and lower channel values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateStollerAverageChannels',
            {
                'sourceValues': source_values,
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'periodCountMA': period_count_ma,
                'periodCountATR': period_count_atr,
                'multiplier': multiplier,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_super_trend(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        period_count: int,
        multiplier: int | float,
    ):
        """Calculates Supertrend values using given number of time periods.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            period_count: Period count.
            multiplier: Multiplier for ATR.

        Returns:
            An array of Supertrend values, or null if calculations are not possible with values.
        """
        result = self.instance.get(
            self.id,
            'calculateSuperTrend',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'periodCount': period_count,
                'multiplier': multiplier,
            },
        )
        return result

    def calculate_swing_index(
        self,
        open_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        close_values: list[int | float],
        limit_move_value: int | float,
    ):
        """Calculates Swing Index (SI) values using given data and maximum price change (limit move) values.

        Args:
            open_values: OHLC-data Open values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            close_values: OHLC-data Close values.
            limit_move_value: Maximum price change in one direction.

        Returns:
            An array of Swing Index values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateSwingIndex',
            {
                'openValues': open_values,
                'highValues': high_values,
                'lowValues': low_values,
                'closeValues': close_values,
                'limitMoveValue': limit_move_value,
            },
        )
        return result

    def calculate_time_series_moving_average(
        self,
        data_values: list[int | float],
        n: int,
    ):
        """Calculates Time Series Moving Average (TSMA) values using given number of time periods (n). Uses least squares regression fitting.

        Args:
            data_values: Data values to calculate from.
            n: Time period count.

        Returns:
            An array of TSMA values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateTimeSeriesMovingAverage',
            {
                'dataValues': data_values,
                'n': n,
            },
        )
        return result

    def calculate_trade_volume_index(
        self,
        data_values: list[int | float],
        volumes: list[int | float],
        minimum_tick_value: int | float,
    ):
        """Calculates Trade Volume Index (TVI) values using given minimum tick value.

        Args:
            data_values: Data values to calculate from.
            volumes: Volume values.
            minimum_tick_value: Minimum tick value to be used in the calculations.

        Returns:
            An array of TVI values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateTradeVolumeIndex',
            {
                'dataValues': data_values,
                'volumes': volumes,
                'minimumTickValue': minimum_tick_value,
            },
        )
        return result

    def calculate_triangular_moving_average(
        self,
        data_values: list[int | float],
        n: int,
    ):
        """Calculates Triangular Moving Average (TMA) values using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.

        Returns:
            An array of TMA values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateTriangularMovingAverage',
            {
                'dataValues': data_values,
                'n': n,
            },
        )
        return result

    def calculate_triple_exponential_average(
        self,
        data_values: list[int | float],
        n: int,
    ):
        """Calculates Triple Exponential Average (TRIX) values using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.

        Returns:
            An array containing two arrays: Triple Exponential Average values and 9-day Exponential Moving Average values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateTripleExponentialAverage',
            {
                'dataValues': data_values,
                'n': n,
            },
        )
        return result

    def calculate_true_strength_index(
        self,
        data_values: list[int | float],
        price_change_periods: int,
        first_smooth_periods: int,
        double_smooth_periods: int,
        signal_periods: int,
        first_smooth_moving_average: int,
        double_smooth_moving_average: int,
        signal_moving_average: int,
    ):
        """Calculates True Strength Index (TSI) values using given time period counts and moving average types.

        Args:
            data_values: Data values to calculate from.
            price_change_periods: Time periods used to calculate the price change (value - value n periods ago).
            first_smooth_periods: Time periods used to calculate the first smoothing.
            double_smooth_periods: Time periods used to calculate the second (double) smoothing.
            signal_periods: Time periods used to calculate the signal values.
            first_smooth_moving_average: Moving average type (0-9) used for the first smoothing (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            double_smooth_moving_average: Moving average type (0-9) used for the second (double) smoothing (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            signal_moving_average: Moving average type (0-9) used to calculate the signal values (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing two arrays: TSI values and signal values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateTrueStrengthIndex',
            {
                'dataValues': data_values,
                'priceChangePeriods': price_change_periods,
                'firstSmoothPeriods': first_smooth_periods,
                'doubleSmoothPeriods': double_smooth_periods,
                'signalPeriods': signal_periods,
                'firstSmoothMovingAverage': first_smooth_moving_average,
                'doubleSmoothMovingAverage': double_smooth_moving_average,
                'signalMovingAverage': signal_moving_average,
            },
        )
        return result

    def calculate_twiggs_money_flow(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        volumes: list[int | float],
        n: int,
    ):
        """Calculates Twiggs Money Flow values using given OHLC- and Volume values and number of time periods (n).

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            volumes: Volume values.
            n: Period count.

        Returns:
            An array of Twiggs Money Flow values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateTwiggsMoneyFlow',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'volumes': volumes,
                'n': n,
            },
        )
        return result

    def calculate_typical_price(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        close_values: list[int | float],
    ):
        """Calculates Typical Prices based on given High, Low and Close values.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            close_values: OHLC-data Close values.

        Returns:
            An array of Typical Prices, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateTypicalPrice',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'closeValues': close_values,
            },
        )
        return result

    def calculate_ultimate_oscillator(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        short_periods: int,
        mid_periods: int,
        long_periods: int,
    ):
        """Calculates Ultimate Oscillator (UO) values using given time period counts.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            short_periods: Period count for the shortest average.
            mid_periods: Period count for the middle average.
            long_periods: Period count for the longest average.

        Returns:
            An array of Ultimate Oscillator values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateUltimateOscillator',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'shortPeriods': short_periods,
                'midPeriods': mid_periods,
                'longPeriods': long_periods,
            },
        )
        return result

    def calculate_ultimate_oscillator_smoothed(
        self,
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        short_periods: int,
        mid_periods: int,
        long_periods: int,
        moving_average_type: int,
    ):
        """Calculates Ultimate Oscillator Smoothed (UO ST) values using given time period counts and moving average.

        Args:
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            short_periods: Period count for the shortest average.
            mid_periods: Period count for the middle average.
            long_periods: Period count for the longest average.
            moving_average_type: Moving average type (0-9) to be used in smoothing (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of Ultimate Oscillator ST values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateUltimateOscillatorSmoothed',
            {
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'shortPeriods': short_periods,
                'midPeriods': mid_periods,
                'longPeriods': long_periods,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def calculate_vidya(
        self,
        data_values: list[int | float],
        n: int,
        period_count_st_dev_short: int,
        period_count_st_dev_long: int,
    ):
        """Calculates Variable Index Dynamic Average (VIDYA) values using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.
            period_count_st_dev_short: Short standard deviation period count used in VIDYA calculations.
            period_count_st_dev_long: Long standard deviation period count used in VIDYA calculations.

        Returns:
            An array of VIDYA values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateVIDYA',
            {
                'dataValues': data_values,
                'n': n,
                'periodCountStDevShort': period_count_st_dev_short,
                'periodCountStDevLong': period_count_st_dev_long,
            },
        )
        return result

    def calculate_variable_moving_average(
        self,
        data_values: list[int | float],
        n: int,
    ):
        """Calculates Variable Moving Average (VMA) values using the given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.

        Returns:
            An array of VMA values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateVariableMovingAverage',
            {
                'dataValues': data_values,
                'n': n,
            },
        )
        return result

    def calculate_vertical_horizontal_filter(
        self,
        data_values: list[int | float],
        n: int,
    ):
        """Calculates Vertical Horizontal Filter (VHF) using given number of time periods (n).

        Args:
            data_values: Data values to calculate from.
            n: Time period count.

        Returns:
            An array of VHF values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateVerticalHorizontalFilter',
            {
                'dataValues': data_values,
                'n': n,
            },
        )
        return result

    def calculate_volume_oscillator(
        self,
        volumes: list[int | float],
        short_period_count: int,
        long_period_count: int,
        signal_period_count: int,
        calculate_as_percentage: bool,
        moving_average_type: int,
        moving_average_signal: int,
    ):
        """Calculates Volume Oscillator (VO) using the given time period counts and moving average types.

        Args:
            volumes: Volume values to calculate from.
            short_period_count: Short-term period count.
            long_period_count: Long-term period count.
            signal_period_count: Period count for signal line.
            calculate_as_percentage: When enabled, the difference between the short and long moving averages is calculated as a percentage and not as an actual volume difference.
            moving_average_type: Moving average type (0-9) for the short and long averages (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).
            moving_average_signal: Moving average type (0-9) for the signal line (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array containing three arrays. The first has the VO values, the second the Signal values, and the third has the histogram values. Returns null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateVolumeOscillator',
            {
                'volumes': volumes,
                'shortPeriodCount': short_period_count,
                'longPeriodCount': long_period_count,
                'signalPeriodCount': signal_period_count,
                'calculateAsPercentage': calculate_as_percentage,
                'movingAverageType': moving_average_type,
                'movingAverageSignal': moving_average_signal,
            },
        )
        return result

    def calculate_volume_rate_of_change(
        self,
        volumes: list[int | float],
        n: int,
    ):
        """Calculates Volume Rate of Change (VROC) values using given number of time periods (n).

        Args:
            volumes: Volumes values to calculate from.
            n: Period count.

        Returns:
            An array of VROC values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateVolumeRateOfChange',
            {
                'volumes': volumes,
                'n': n,
            },
        )
        return result

    def calculate_volume_weighted_moving_average(
        self,
        values: list[int | float],
        volumes: list[int | float],
        n: int,
    ):
        """Calculates Volume Weighted Moving Average (VWMA) values using the given number of time periods (n).

        Args:
            values: Data values to calculate from.
            volumes: Volume values.
            n: Time period count.

        Returns:
            An array of VWMA values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateVolumeWeightedMovingAverage',
            {
                'values': values,
                'volumes': volumes,
                'n': n,
            },
        )
        return result

    def calculate_weighted_close(
        self,
        high_values: list[int | float],
        low_values: list[int | float],
        close_values: list[int | float],
    ):
        """Calculates Weighted Close values based on given High, Low and Close values.

        Args:
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            close_values: OHLC-data Close values.

        Returns:
            An array of Weighted Close values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateWeightedClose',
            {
                'highValues': high_values,
                'lowValues': low_values,
                'closeValues': close_values,
            },
        )
        return result

    def calculate_weighted_moving_average(
        self,
        values: list[int | float],
        n: int,
    ):
        """Calculates Weighted Moving Average using given number of time periods (n).

        Args:
            values: Data values to calculate from.
            n: The number of values to use in averaging each round (period count).

        Returns:
            Array of Weighted Moving Average values, or null if averaging is not possible for the given values.
        """
        result = self.instance.get(
            self.id,
            'calculateWeightedMovingAverage',
            {
                'values': values,
                'n': n,
            },
        )
        return result

    def calculate_williams_percent_range(
        self,
        source_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        n: int,
    ):
        """Calculates Williams Percent Range values using given number of time periods (n).

        Args:
            source_values: Data values used as a basis for calculations, most commonly OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            n: Time period count.

        Returns:
            An array of Williams Percent Range values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateWilliamsPercentRange',
            {
                'sourceValues': source_values,
                'highValues': high_values,
                'lowValues': low_values,
                'n': n,
            },
        )
        return result

    def calculate_williams_variable_accumulation_distribution(
        self,
        open_values: list[int | float],
        close_values: list[int | float],
        high_values: list[int | float],
        low_values: list[int | float],
        volumes: list[int | float],
        n: int,
        moving_average_type: int,
    ):
        """Calculates Williams Variable Accumulation Distribution (WVAD) values using given moving average and number of time periods (n).

        Args:
            open_values: OHLC-data Open values.
            close_values: OHLC-data Close values.
            high_values: OHLC-data High values.
            low_values: OHLC-data Low values.
            volumes: Volume values.
            n: Period count.
            moving_average_type: Moving average type (0-9) to use during calculations (0=EMA, 1=None, 2=SMA, 3=TSMA, 4=TMA, 5=VMA, 6=VIDYA, 7=VWMA, 8=WMA, 9=WWS).

        Returns:
            An array of WVAD values, or null if calculations are not possible with given values.
        """
        result = self.instance.get(
            self.id,
            'calculateWilliamsVariableAccumulationDistribution',
            {
                'openValues': open_values,
                'closeValues': close_values,
                'highValues': high_values,
                'lowValues': low_values,
                'volumes': volumes,
                'n': n,
                'movingAverageType': moving_average_type,
            },
        )
        return result

    def linear_regression(
        self,
        x_in_factorization: list[int | float],
        y_in_factorization: list[int | float],
        x_values_to_fit: list[int | float],
    ):
        """Calculate linear line fit for given points.

        Args:
            x_in_factorization: X-values that are used to calculate the factors. This is the point set where the regression line is fitted to.
            y_in_factorization: Y-values that are used to calculate the factors. Length must be equal to xInFactorization length.
            x_values_to_fit: X-values whose Y values are to be solved, using the factors.

        Returns:
            Array containing fitted Y-values. Returns null if unable to calculate with given values.
        """
        result = self.instance.get(
            self.id,
            'linearRegression',
            {
                'xInFactorization': x_in_factorization,
                'yInFactorization': y_in_factorization,
                'xValuesToFit': x_values_to_fit,
            },
        )
        return result
