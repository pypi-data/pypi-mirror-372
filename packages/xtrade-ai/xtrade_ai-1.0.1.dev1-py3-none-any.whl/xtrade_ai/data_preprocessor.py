"""
Data preprocessing module for XTrade-AI Framework.

This module handles preprocessing of market data including OHLCV data,
technical indicators, normalization, and feature engineering.
"""

import logging
import warnings
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import savgol_filter
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Enhanced data preprocessor with automatic padding and custom indicators.

    This class provides comprehensive data preprocessing capabilities including:
    - OHLCV data validation and cleaning
    - Technical indicator calculation with dynamic windows
    - Automatic NaN handling and padding
    - Custom indicator support
    - Data normalization and scaling
    - Feature engineering
    - Market regime detection
    - Advanced statistical features
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize DataPreprocessor.

        Args:
            config: Configuration dictionary with preprocessing parameters
        """
        self.config = config or {}
        self.min_data_length = self.config.get("min_data_length", 50)
        self.scaler = StandardScaler()
        self.feature_scalers = {}
        self.custom_indicators = {}
        self.market_regime_detector = None

        # Default technical indicators
        self.default_indicators = [
            "rsi",
            "macd",
            "bollinger_hband",
            "bollinger_lband",
            "sma_20",
            "sma_50",
            "ema_12",
            "ema_26",
            "stoch_k",
            "stoch_d",
            "williams_r",
            "cci",
            "atr",
            "adx",
            "obv",
            "vwap",
            "supertrend",
            "ichimoku_tenkan",
            "ichimoku_kijun",
            "ichimoku_senkou_a",
        ]

        # Advanced feature engineering options
        self.enable_advanced_features = self.config.get(
            "enable_advanced_features", True
        )
        self.enable_market_regime = self.config.get("enable_market_regime", True)
        self.enable_statistical_features = self.config.get(
            "enable_statistical_features", True
        )

        logger.info("DataPreprocessor initialized successfully")

    def preprocess_data(
        self,
        market_data: pd.DataFrame,
        technical_indicators: Optional[List[str]] = None,
        custom_indicators: Optional[Dict[str, Callable]] = None,
    ) -> pd.DataFrame:
        """
        Preprocess market data with comprehensive feature engineering.

        Args:
            market_data: OHLCV DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
            technical_indicators: List of technical indicators to calculate
            custom_indicators: Dictionary of custom indicator functions

        Returns:
            Preprocessed DataFrame with technical indicators and normalized features

        Raises:
            ValueError: If market_data is invalid or too short
        """
        try:
            # Validate input data
            self._validate_market_data(market_data)

            # Handle short data with padding
            if len(market_data) < self.min_data_length:
                market_data = self._pad_short_data(market_data)

            # Calculate technical indicators
            indicators_to_use = (
                technical_indicators
                if technical_indicators is not None and not technical_indicators.empty
                else self.default_indicators
            )
            processed_data = self._calculate_technical_indicators(
                market_data, indicators_to_use
            )

            # Add custom indicators
            if custom_indicators:
                processed_data = self._add_custom_indicators(
                    processed_data, custom_indicators
                )

            # Add advanced features if enabled
            if self.enable_advanced_features:
                processed_data = self._add_advanced_features(processed_data)

            # Add market regime detection if enabled
            if self.enable_market_regime:
                processed_data = self._add_market_regime_features(processed_data)

            # Add statistical features if enabled
            if self.enable_statistical_features:
                processed_data = self._add_statistical_features(processed_data)

            # Handle NaN values
            processed_data = self._handle_nan_values(processed_data)

            # Normalize features
            processed_data = self._normalize_features(processed_data)

            # Add engineered features
            processed_data = self._add_engineered_features(processed_data)

            logger.info(f"Data preprocessing completed. Shape: {processed_data.shape}")
            return processed_data

        except Exception as e:
            logger.error(f"Data preprocessing failed: {e}")
            raise

    def _validate_market_data(self, market_data: pd.DataFrame) -> None:
        """
        Validate market data format and content.

        Args:
            market_data: DataFrame to validate

        Raises:
            ValueError: If data is invalid
        """
        required_columns = ["open", "high", "low", "close", "volume"]

        if not isinstance(market_data, pd.DataFrame):
            raise ValueError("market_data must be a pandas DataFrame")

        if len(market_data) == 0:
            raise ValueError("market_data cannot be empty")

        missing_columns = [
            col for col in required_columns if col not in market_data.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Check for negative values
        for col in ["open", "high", "low", "close", "volume"]:
            if (market_data[col] < 0).any():
                raise ValueError(f"Negative values found in {col} column")

        # Check OHLC consistency
        if not (
            (market_data["high"] >= market_data["low"]).all()
            and (market_data["high"] >= market_data["open"]).all()
            and (market_data["high"] >= market_data["close"]).all()
            and (market_data["low"] <= market_data["open"]).all()
            and (market_data["low"] <= market_data["close"]).all()
        ):
            raise ValueError("OHLC data consistency check failed")

    def _pad_short_data(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Pad short data with appropriate values.

        Args:
            market_data: Original market data

        Returns:
            Padded market data
        """
        if len(market_data) >= self.min_data_length:
            return market_data

        padding_length = self.min_data_length - len(market_data)
        logger.warning(
            f"Data too short ({len(market_data)} rows), padding with {padding_length} rows"
        )

        # Create padding data using the first row
        first_row = market_data.iloc[0]
        padding_data = pd.DataFrame(
            [first_row] * padding_length, columns=market_data.columns
        )

        # Combine padding with original data
        padded_data = pd.concat([padding_data, market_data], ignore_index=True)

        return padded_data

    def _calculate_technical_indicators(
        self, market_data: pd.DataFrame, indicators: List[str]
    ) -> pd.DataFrame:
        """
        Calculate technical indicators with dynamic windows.

        Args:
            market_data: OHLCV DataFrame
            indicators: List of indicator names

        Returns:
            DataFrame with technical indicators
        """
        processed_data = market_data.copy()

        try:
            import pandas_ta as ta
        except ImportError:
            logger.warning("pandas_ta not available, using basic indicators")
            return self._calculate_basic_indicators(processed_data, indicators)

        # Dynamic window calculation based on data length
        data_length = len(market_data)
        short_window = max(5, min(20, data_length // 10))
        long_window = max(20, min(50, data_length // 5))

        indicator_functions = {
            "rsi": lambda df: ta.rsi(df["close"], length=short_window),
            "macd": lambda df: ta.macd(df["close"])["MACD_12_26_9"],
            "bollinger_hband": lambda df: self._calculate_bollinger_safe(df, "upper"),
            "bollinger_lband": lambda df: self._calculate_bollinger_safe(df, "lower"),
            "bollinger_upper": lambda df: self._calculate_bollinger_safe(df, "upper"),
            "bollinger_lower": lambda df: self._calculate_bollinger_safe(df, "lower"),
            "sma_20": lambda df: ta.sma(df["close"], length=20),
            "sma_50": lambda df: ta.sma(df["close"], length=50),
            "ema_12": lambda df: ta.ema(df["close"], length=12),
            "ema_26": lambda df: ta.ema(df["close"], length=26),
            "ema_20": lambda df: ta.ema(df["close"], length=20),
            "stoch_k": lambda df: ta.stoch(df["high"], df["low"], df["close"])[
                "STOCHk_14_3_3"
            ],
            "stoch_d": lambda df: ta.stoch(df["high"], df["low"], df["close"])[
                "STOCHd_14_3_3"
            ],
            "stochastic_k": lambda df: ta.stoch(df["high"], df["low"], df["close"])[
                "STOCHk_14_3_3"
            ],
            "stochastic_d": lambda df: ta.stoch(df["high"], df["low"], df["close"])[
                "STOCHd_14_3_3"
            ],
            "williams_r": lambda df: ta.willr(df["high"], df["low"], df["close"]),
            "cci": lambda df: ta.cci(df["high"], df["low"], df["close"]),
            "atr": lambda df: ta.atr(df["high"], df["low"], df["close"]),
            "adx": lambda df: ta.adx(df["high"], df["low"], df["close"])["ADX_14"],
            "obv": lambda df: ta.obv(df["close"], df["volume"]),
            "vwap": lambda df: self._calculate_vwap_safe(df),
            "supertrend": lambda df: ta.supertrend(df["high"], df["low"], df["close"])[
                "SUPERT_7_3.0"
            ],
            "ichimoku_tenkan": lambda df: self._calculate_ichimoku_safe(df, "ITS_9"),
            "ichimoku_kijun": lambda df: self._calculate_ichimoku_safe(df, "IKS_26"),
            "ichimoku_senkou_a": lambda df: self._calculate_ichimoku_safe(df, "ISA_9"),
            "kst": lambda df: self._calculate_kst_safe(df),
            "tsi": lambda df: self._calculate_tsi_safe(df),
            "ultimate_oscillator": lambda df: ta.uo(df["high"], df["low"], df["close"]),
            "money_flow_index": lambda df: ta.mfi(
                df["high"], df["low"], df["close"], df["volume"]
            ),
            "on_balance_volume": lambda df: ta.obv(df["close"], df["volume"]),
            "accumulation_distribution": lambda df: ta.ad(
                df["high"], df["low"], df["close"], df["volume"]
            ),
        }

        # Suppress pandas_ta warnings
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            for indicator in indicators:
                if indicator in indicator_functions:
                    try:
                        processed_data[indicator] = indicator_functions[indicator](
                            processed_data
                        )
                        logger.debug(f"Calculated {indicator}")
                    except Exception as e:
                        logger.warning(f"Failed to calculate {indicator}: {e}")
                else:
                    logger.warning(f"Unknown indicator: {indicator}")

        return processed_data

    def _calculate_bollinger_safe(self, df: pd.DataFrame, band_type: str) -> pd.Series:
        """Calculate Bollinger Bands safely with error handling."""
        try:
            import pandas_ta as ta

            bbands_result = ta.bbands(df["close"])

            # Try different possible column names
            if band_type == "upper":
                for col in ["BBH_20_2.0", "BBU_20_2.0", "BBU_20_2", "BBH_20_2"]:
                    if col in bbands_result.columns:
                        return bbands_result[col]
                # Fallback: calculate manually
                sma = df["close"].rolling(window=20).mean()
                std = df["close"].rolling(window=20).std()
                return sma + (std * 2)
            else:  # lower
                for col in ["BBL_20_2.0", "BBL_20_2"]:
                    if col in bbands_result.columns:
                        return bbands_result[col]
                # Fallback: calculate manually
                sma = df["close"].rolling(window=20).mean()
                std = df["close"].rolling(window=20).std()
                return sma - (std * 2)
        except Exception as e:
            logger.warning(f"Failed to calculate Bollinger {band_type} band: {e}")
            # Return simple moving average as fallback
            return df["close"].rolling(window=20).mean()

    def _calculate_vwap_safe(self, df: pd.DataFrame) -> pd.Series:
        """Calculate VWAP safely with error handling."""
        try:
            import pandas_ta as ta

            # Ensure index is datetime for VWAP calculation
            df_copy = df.copy()
            if not isinstance(df_copy.index, pd.DatetimeIndex):
                # Create a proper datetime index
                if "timestamp" in df_copy.columns:
                    df_copy.index = pd.to_datetime(df_copy["timestamp"])
                else:
                    # Create a dummy datetime index
                    df_copy.index = pd.date_range(
                        start="2023-01-01", periods=len(df_copy), freq="D"
                    )

            # Suppress pandas_ta warnings
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return ta.vwap(
                    df_copy["high"], df_copy["low"], df_copy["close"], df_copy["volume"]
                )
        except Exception as e:
            logger.warning(f"Failed to calculate VWAP: {e}")
            # Return simple VWAP calculation
            typical_price = (df["high"] + df["low"] + df["close"]) / 3
            return (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()

    def _calculate_ichimoku_safe(self, df: pd.DataFrame, component: str) -> pd.Series:
        """Calculate Ichimoku components safely."""
        try:
            import pandas_ta as ta

            ichimoku_result = ta.ichimoku(df["high"], df["low"], df["close"])

            # Check if result is a DataFrame or tuple
            if isinstance(ichimoku_result, tuple):
                # If it's a tuple, pandas_ta returned multiple values
                # Usually the first element is the main DataFrame
                if len(ichimoku_result) > 0 and hasattr(ichimoku_result[0], "columns"):
                    ichimoku_df = ichimoku_result[0]
                else:
                    # Fallback to manual calculation
                    raise ValueError("Ichimoku result is tuple but no DataFrame found")
            else:
                ichimoku_df = ichimoku_result

            # Try different possible column names for each component
            if component == "ITS_9":
                for col in ["ITS_9", "ITS9", "ITS_9_9", "TENKAN_9"]:
                    if col in ichimoku_df.columns:
                        return ichimoku_df[col]
                # Fallback: calculate manually
                return (
                    df["high"].rolling(window=9).max()
                    + df["low"].rolling(window=9).min()
                ) / 2
            elif component == "IKS_26":
                for col in ["IKS_26", "IKS26", "IKS_26_26", "KIJUN_26"]:
                    if col in ichimoku_df.columns:
                        return ichimoku_df[col]
                # Fallback: calculate manually
                return (
                    df["high"].rolling(window=26).max()
                    + df["low"].rolling(window=26).min()
                ) / 2
            elif component == "ISA_9":
                for col in ["ISA_9", "ISA9", "ISA_9_9", "SENKOU_A"]:
                    if col in ichimoku_df.columns:
                        return ichimoku_df[col]
                # Fallback: calculate manually
                tenkan = (
                    df["high"].rolling(window=9).max()
                    + df["low"].rolling(window=9).min()
                ) / 2
                kijun = (
                    df["high"].rolling(window=26).max()
                    + df["low"].rolling(window=26).min()
                ) / 2
                return ((tenkan + kijun) / 2).shift(26)
            else:
                # Generic fallback
                return df["close"].rolling(window=9).mean()
        except Exception as e:
            logger.warning(f"Failed to calculate ichimoku_{component}: {e}")
            # Return simple moving average as fallback
            if component == "ITS_9":
                return df["close"].rolling(window=9).mean()
            elif component == "IKS_26":
                return df["close"].rolling(window=26).mean()
            else:
                return df["close"].rolling(window=9).mean()

    def _calculate_kst_safe(self, df: pd.DataFrame) -> pd.Series:
        """Calculate KST safely."""
        try:
            import pandas_ta as ta

            kst_result = ta.kst(df["close"])

            # KST returns a DataFrame with multiple columns, we need to extract the main KST line
            if isinstance(kst_result, pd.DataFrame):
                # Try to find the main KST column
                for col in ["KST_10_15_20_30_10_10_10_15", "KST", "KST_10_15_20_30"]:
                    if col in kst_result.columns:
                        return kst_result[col]
                # If no specific column found, return the first column
                return kst_result.iloc[:, 0]
            else:
                return kst_result
        except Exception as e:
            logger.warning(f"Failed to calculate kst: {e}")
            # Return simple momentum indicator as fallback
            return df["close"].pct_change(10)

    def _calculate_tsi_safe(self, df: pd.DataFrame) -> pd.Series:
        """Calculate TSI safely."""
        try:
            import pandas_ta as ta

            tsi_result = ta.tsi(df["close"])

            # TSI returns a DataFrame with multiple columns, we need to extract the main TSI line
            if isinstance(tsi_result, pd.DataFrame):
                # Try to find the main TSI column
                for col in ["TSI_13_25", "TSI", "TSI_13_25_13"]:
                    if col in tsi_result.columns:
                        return tsi_result[col]
                # If no specific column found, return the first column
                return tsi_result.iloc[:, 0]
            else:
                return tsi_result
        except Exception as e:
            logger.warning(f"Failed to calculate tsi: {e}")
            # Return simple momentum indicator as fallback
            return df["close"].pct_change(5)

    def _calculate_basic_indicators(
        self, market_data: pd.DataFrame, indicators: List[str]
    ) -> pd.DataFrame:
        """
        Calculate basic technical indicators without pandas_ta.

        Args:
            market_data: OHLCV DataFrame
            indicators: List of indicator names

        Returns:
            DataFrame with basic indicators
        """
        processed_data = market_data.copy()

        # Simple moving averages
        if "sma_20" in indicators:
            processed_data["sma_20"] = processed_data["close"].rolling(window=20).mean()

        if "sma_50" in indicators:
            processed_data["sma_50"] = processed_data["close"].rolling(window=50).mean()

        # RSI calculation
        if "rsi" in indicators:
            delta = processed_data["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            processed_data["rsi"] = 100 - (100 / (1 + rs))

        # MACD calculation
        if "macd" in indicators:
            ema_12 = processed_data["close"].ewm(span=12).mean()
            ema_26 = processed_data["close"].ewm(span=26).mean()
            processed_data["macd"] = ema_12 - ema_26

        return processed_data

    def _add_custom_indicators(
        self, data: pd.DataFrame, custom_indicators: Dict[str, Callable]
    ) -> pd.DataFrame:
        """
        Add custom indicators to the dataset.

        Args:
            data: Processed DataFrame
            custom_indicators: Dictionary of custom indicator functions

        Returns:
            DataFrame with custom indicators
        """
        processed_data = data.copy()

        for name, func in custom_indicators.items():
            try:
                processed_data[name] = func(processed_data)
                logger.debug(f"Added custom indicator: {name}")
            except Exception as e:
                logger.warning(f"Failed to add custom indicator {name}: {e}")

        return processed_data

    def _add_advanced_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add advanced features to the dataset.

        Args:
            data: Processed DataFrame

        Returns:
            DataFrame with advanced features
        """
        processed_data = data.copy()

        # Price action features
        processed_data["price_range"] = processed_data["high"] - processed_data["low"]
        processed_data["body_size"] = abs(
            processed_data["close"] - processed_data["open"]
        )
        processed_data["upper_shadow"] = processed_data["high"] - np.maximum(
            processed_data["open"], processed_data["close"]
        )
        processed_data["lower_shadow"] = (
            np.minimum(processed_data["open"], processed_data["close"])
            - processed_data["low"]
        )

        # Candlestick patterns
        processed_data["doji"] = (
            abs(processed_data["close"] - processed_data["open"])
            < processed_data["price_range"] * 0.1
        ).astype(int)
        processed_data["hammer"] = (
            (processed_data["lower_shadow"] > processed_data["body_size"] * 2)
            & (processed_data["upper_shadow"] < processed_data["body_size"] * 0.5)
        ).astype(int)
        processed_data["shooting_star"] = (
            (processed_data["upper_shadow"] > processed_data["body_size"] * 2)
            & (processed_data["lower_shadow"] < processed_data["body_size"] * 0.5)
        ).astype(int)

        # Support and resistance levels
        processed_data["support_level"] = processed_data["low"].rolling(window=20).min()
        processed_data["resistance_level"] = (
            processed_data["high"].rolling(window=20).max()
        )

        # Fibonacci retracement levels
        high_20 = processed_data["high"].rolling(window=20).max()
        low_20 = processed_data["low"].rolling(window=20).min()
        diff = high_20 - low_20
        processed_data["fib_236"] = high_20 - diff * 0.236
        processed_data["fib_382"] = high_20 - diff * 0.382
        processed_data["fib_500"] = high_20 - diff * 0.500
        processed_data["fib_618"] = high_20 - diff * 0.618

        return processed_data

    def _add_market_regime_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add market regime detection features.

        Args:
            data: Processed DataFrame

        Returns:
            DataFrame with market regime features
        """
        processed_data = data.copy()

        # Volatility regime
        returns = processed_data["close"].pct_change()
        volatility = returns.rolling(window=20).std()
        processed_data["volatility_regime"] = pd.cut(
            volatility,
            bins=[0, volatility.quantile(0.33), volatility.quantile(0.67), np.inf],
            labels=[0, 1, 2],
        )

        # Trend regime
        sma_20 = processed_data["close"].rolling(window=20).mean()
        sma_50 = processed_data["close"].rolling(window=50).mean()
        processed_data["trend_regime"] = np.where(sma_20 > sma_50, 1, 0)

        # Market structure
        processed_data["higher_highs"] = (
            processed_data["high"] > processed_data["high"].shift(1)
        ).astype(int)
        processed_data["lower_lows"] = (
            processed_data["low"] < processed_data["low"].shift(1)
        ).astype(int)

        # Momentum regime
        momentum = processed_data["close"] / processed_data["close"].shift(20) - 1
        processed_data["momentum_regime"] = pd.cut(
            momentum,
            bins=[-np.inf, momentum.quantile(0.33), momentum.quantile(0.67), np.inf],
            labels=[0, 1, 2],
        )

        return processed_data

    def _add_statistical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add statistical features to the dataset.

        Args:
            data: Processed DataFrame

        Returns:
            DataFrame with statistical features
        """
        processed_data = data.copy()

        # Rolling statistics
        for window in [5, 10, 20]:
            processed_data[f"mean_{window}"] = (
                processed_data["close"].rolling(window=window).mean()
            )
            processed_data[f"std_{window}"] = (
                processed_data["close"].rolling(window=window).std()
            )
            processed_data[f"skew_{window}"] = (
                processed_data["close"].rolling(window=window).skew()
            )
            processed_data[f"kurt_{window}"] = (
                processed_data["close"].rolling(window=window).kurt()
            )

        # Z-score
        processed_data["z_score_20"] = (
            processed_data["close"] - processed_data["close"].rolling(window=20).mean()
        ) / processed_data["close"].rolling(window=20).std()

        # Percentile ranks
        processed_data["price_percentile"] = (
            processed_data["close"]
            .rolling(window=20)
            .apply(lambda x: stats.percentileofscore(x, x.iloc[-1]))
        )

        # Autocorrelation
        returns = processed_data["close"].pct_change()
        for lag in [1, 5, 10]:
            processed_data[f"autocorr_{lag}"] = returns.rolling(window=20).apply(
                lambda x: x.autocorr(lag=lag) if len(x) > lag else 0
            )

        return processed_data

    def _handle_nan_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Handle NaN values in the dataset.

        Args:
            data: DataFrame with potential NaN values

        Returns:
            DataFrame with NaN values handled
        """
        processed_data = data.copy()

        # Forward fill for technical indicators
        indicator_columns = [
            col
            for col in processed_data.columns
            if col not in ["open", "high", "low", "close", "volume"]
        ]

        if indicator_columns:
            processed_data[indicator_columns] = processed_data[
                indicator_columns
            ].fillna(method="ffill")

        # Backward fill for remaining NaN values
        processed_data = processed_data.fillna(method="bfill")

        # Fill any remaining NaN values with 0
        processed_data = processed_data.fillna(0)

        logger.debug(
            f"Handled NaN values. Remaining NaN: {processed_data.isna().sum().sum()}"
        )
        return processed_data

    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize features using appropriate scaling methods.

        Args:
            data: DataFrame to normalize

        Returns:
            Normalized DataFrame
        """
        processed_data = data.copy()

        # Separate price and indicator columns
        price_columns = ["open", "high", "low", "close"]
        volume_columns = ["volume"]

        # Exclude non-numeric columns like timestamp
        non_numeric_columns = ["timestamp"]
        indicator_columns = [
            col
            for col in processed_data.columns
            if col not in price_columns + volume_columns + non_numeric_columns
            and processed_data[col].dtype in ["int64", "float64"]
        ]

        # Normalize price data using MinMaxScaler
        if price_columns:
            price_scaler = MinMaxScaler()
            processed_data[price_columns] = price_scaler.fit_transform(
                processed_data[price_columns]
            )
            self.feature_scalers["price"] = price_scaler

        # Normalize volume data using StandardScaler
        if volume_columns:
            volume_scaler = StandardScaler()
            processed_data[volume_columns] = volume_scaler.fit_transform(
                processed_data[volume_columns]
            )
            self.feature_scalers["volume"] = volume_scaler

        # Normalize indicator data using RobustScaler for better handling of outliers
        if indicator_columns:
            indicator_scaler = RobustScaler()
            processed_data[indicator_columns] = indicator_scaler.fit_transform(
                processed_data[indicator_columns]
            )
            self.feature_scalers["indicators"] = indicator_scaler

        return processed_data

    def _add_engineered_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add engineered features to the dataset.

        Args:
            data: Processed DataFrame

        Returns:
            DataFrame with engineered features
        """
        processed_data = data.copy()

        # Price-based features
        processed_data["price_change"] = processed_data["close"].pct_change()
        processed_data["price_change_abs"] = processed_data["price_change"].abs()
        processed_data["high_low_ratio"] = (
            processed_data["high"] / processed_data["low"]
        )
        processed_data["close_open_ratio"] = (
            processed_data["close"] / processed_data["open"]
        )

        # Volume-based features
        processed_data["volume_ma"] = processed_data["volume"].rolling(window=20).mean()
        processed_data["volume_ratio"] = (
            processed_data["volume"] / processed_data["volume_ma"]
        )

        # Volatility features
        processed_data["volatility"] = (
            processed_data["price_change"].rolling(window=20).std()
        )
        processed_data["volatility_ma"] = (
            processed_data["volatility"].rolling(window=10).mean()
        )

        # Momentum features
        processed_data["momentum_5"] = (
            processed_data["close"] / processed_data["close"].shift(5) - 1
        )
        processed_data["momentum_10"] = (
            processed_data["close"] / processed_data["close"].shift(10) - 1
        )
        processed_data["momentum_20"] = (
            processed_data["close"] / processed_data["close"].shift(20) - 1
        )

        # Smoothing features using Savitzky-Golay filter
        try:
            processed_data["close_smooth"] = savgol_filter(
                processed_data["close"], window_length=11, polyorder=3
            )
            processed_data["volume_smooth"] = savgol_filter(
                processed_data["volume"], window_length=11, polyorder=3
            )
        except Exception as e:
            logger.warning(f"Savitzky-Golay smoothing failed: {e}")
            processed_data["close_smooth"] = processed_data["close"]
            processed_data["volume_smooth"] = processed_data["volume"]

        # Handle NaN values in engineered features
        engineered_columns = [
            col for col in processed_data.columns if col not in data.columns
        ]
        processed_data[engineered_columns] = processed_data[engineered_columns].fillna(
            0
        )

        return processed_data

    def get_feature_names(self) -> List[str]:
        """
        Get list of feature names.

        Returns:
            List of feature names
        """
        return list(self.feature_scalers.keys())

    def inverse_transform(
        self, data: pd.DataFrame, feature_type: str = "all"
    ) -> pd.DataFrame:
        """
        Inverse transform normalized data.

        Args:
            data: Normalized DataFrame
            feature_type: Type of features to inverse transform ('price', 'volume', 'indicators', 'all')

        Returns:
            DataFrame with inverse transformed features
        """
        if feature_type not in ["price", "volume", "indicators", "all"]:
            raise ValueError(
                "feature_type must be 'price', 'volume', 'indicators', or 'all'"
            )

        if feature_type not in self.feature_scalers:
            raise ValueError(f"No scaler found for {feature_type}")

        scaler = self.feature_scalers[feature_type]
        return scaler.inverse_transform(data)

    def get_feature_importance(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate feature importance using correlation with price changes.

        Args:
            data: Processed DataFrame

        Returns:
            Dictionary mapping feature names to importance scores
        """
        price_changes = data["close"].pct_change().abs()
        feature_importance = {}

        for column in data.columns:
            if column not in ["open", "high", "low", "close", "volume"]:
                try:
                    correlation = abs(data[column].corr(price_changes))
                    feature_importance[column] = (
                        correlation if not np.isnan(correlation) else 0.0
                    )
                except Exception:
                    feature_importance[column] = 0.0

        return dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )


# Convenience function for backward compatibility
def preprocess_data(
    market_data: pd.DataFrame,
    technical_indicators: Optional[List[str]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Convenience function for data preprocessing.

    Args:
        market_data: OHLCV DataFrame
        technical_indicators: List of technical indicators
        config: Configuration dictionary

    Returns:
        Preprocessed DataFrame
    """
    preprocessor = DataPreprocessor(config)
    return preprocessor.preprocess_data(market_data, technical_indicators)
