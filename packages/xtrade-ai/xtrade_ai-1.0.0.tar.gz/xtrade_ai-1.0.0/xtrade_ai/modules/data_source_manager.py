"""
Data Source Manager for XTrade-AI Framework.

This module provides a unified interface for loading data from multiple sources:
- Yahoo Finance (yfinance)
- CSV files
- Variable data (pandas DataFrame)
- MetaTrader5 (existing integration)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class DataSourceManager:
    """
    Unified data source manager for XTrade-AI Framework.
    
    Supports multiple data sources:
    - Yahoo Finance (yfinance)
    - CSV files
    - Variable data (pandas DataFrame)
    - MetaTrader5 (existing integration)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize DataSourceManager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data source configurations
        self.yfinance_config = self.config.get("yfinance", {})
        self.csv_config = self.config.get("csv", {})
        
        # Cache for yfinance data
        self._yfinance_cache = {}
        
        self.logger.info("DataSourceManager initialized successfully")

    def load_data(
        self,
        source: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from specified source.
        
        Args:
            source: Data source type ('yfinance', 'csv', 'variable', 'metatrader5')
            **kwargs: Source-specific parameters
            
        Returns:
            DataFrame with market data
            
        Raises:
            ValueError: If source is not supported
        """
        source = source.lower()
        
        if source == "yfinance":
            return self._load_yfinance_data(**kwargs)
        elif source == "csv":
            return self._load_csv_data(**kwargs)
        elif source == "variable":
            return self._load_variable_data(**kwargs)
        elif source == "metatrader5":
            return self._load_metatrader5_data(**kwargs)
        else:
            raise ValueError(f"Unsupported data source: {source}")

    def _load_yfinance_data(
        self,
        symbols: Union[str, List[str]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d",
        period: Optional[str] = None,
        auto_adjust: bool = True,
        prepost: bool = False,
        threads: bool = True,
        proxy: Optional[str] = None,
        rounding: bool = True,
        timeout: Optional[int] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from Yahoo Finance.
        
        Args:
            symbols: Stock symbol(s) to download
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            auto_adjust: Auto-adjust OHLC
            prepost: Include pre/post market data
            threads: Use threads for downloading
            proxy: Proxy URL
            rounding: Round values
            timeout: Request timeout
            **kwargs: Additional yfinance parameters
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            self.logger.info(f"Loading yfinance data for symbols: {symbols}")
            
            # Convert single symbol to list
            if isinstance(symbols, str):
                symbols = [symbols]
            
            # Create cache key
            cache_key = f"{','.join(symbols)}_{start_date}_{end_date}_{interval}_{period}"
            
            # Check cache first
            if cache_key in self._yfinance_cache:
                self.logger.info("Using cached yfinance data")
                return self._yfinance_cache[cache_key].copy()
            
            # Download data
            data = yf.download(
                tickers=symbols,
                start=start_date,
                end=end_date,
                interval=interval,
                period=period,
                auto_adjust=auto_adjust,
                prepost=prepost,
                threads=threads,
                proxy=proxy,
                rounding=rounding,
                timeout=timeout,
                **kwargs
            )
            
            # Handle multi-symbol data
            if len(symbols) == 1:
                # Single symbol - flatten column names
                data.columns = [col[1] if isinstance(col, tuple) else col for col in data.columns]
            else:
                # Multiple symbols - keep multi-level columns
                pass
            
            # Standardize column names
            data = self._standardize_columns(data)
            
            # Cache the data
            self._yfinance_cache[cache_key] = data.copy()
            
            self.logger.info(f"Successfully loaded yfinance data: {data.shape}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading yfinance data: {e}")
            raise

    def _load_csv_data(
        self,
        file_path: Union[str, Path],
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Args:
            file_path: Path to CSV file
            **kwargs: Additional pandas read_csv parameters
            
        Returns:
            DataFrame with market data
        """
        try:
            file_path = Path(file_path)
            self.logger.info(f"Loading CSV data from: {file_path}")
            
            if not file_path.exists():
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            
            # Load CSV with default parameters
            default_params = {
                "index_col": 0,
                "parse_dates": True,
                "infer_datetime_format": True
            }
            default_params.update(kwargs)
            
            data = pd.read_csv(file_path, **default_params)
            
            # Standardize column names
            data = self._standardize_columns(data)
            
            self.logger.info(f"Successfully loaded CSV data: {data.shape}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading CSV data: {e}")
            raise

    def _load_variable_data(
        self,
        data: pd.DataFrame,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from variable (pandas DataFrame).
        
        Args:
            data: Input DataFrame
            **kwargs: Additional parameters (ignored)
            
        Returns:
            DataFrame with market data
        """
        try:
            self.logger.info(f"Loading variable data: {data.shape}")
            
            if not isinstance(data, pd.DataFrame):
                raise ValueError("Input data must be a pandas DataFrame")
            
            # Standardize column names
            data = self._standardize_columns(data)
            
            self.logger.info(f"Successfully loaded variable data: {data.shape}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading variable data: {e}")
            raise

    def _load_metatrader5_data(
        self,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from MetaTrader5 (existing integration).
        
        Args:
            **kwargs: MetaTrader5 specific parameters
            
        Returns:
            DataFrame with market data
        """
        try:
            self.logger.info("Loading MetaTrader5 data")
            
            # Use existing MetaTrader5 integration
            # This would integrate with the existing broker setup
            # For now, return empty DataFrame as placeholder
            self.logger.warning("MetaTrader5 integration not yet implemented")
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Error loading MetaTrader5 data: {e}")
            raise

    def _standardize_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to match expected format.
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with standardized column names
        """
        # Create a copy to avoid modifying original
        data = data.copy()
        
        # Column name mapping
        column_mapping = {
            # Common variations
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Adj Close': 'adj_close',
            
            # Lowercase variations
            'open': 'open',
            'high': 'high',
            'low': 'low', 
            'close': 'close',
            'volume': 'volume',
            'adj_close': 'adj_close',
            
            # Other common names
            'price': 'close',
            'amount': 'volume',
            'vol': 'volume',
            'adj_close': 'adj_close',
            'adjusted_close': 'adj_close'
        }
        
        # Rename columns
        data.columns = [column_mapping.get(col, col) for col in data.columns]
        
        # Ensure required columns exist
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            self.logger.warning(f"Missing required columns: {missing_columns}")
            
            # Try to infer missing columns
            if 'close' in data.columns and 'open' not in data.columns:
                data['open'] = data['close'].shift(1)
                data['open'].iloc[0] = data['close'].iloc[0]
            
            if 'close' in data.columns and 'high' not in data.columns:
                data['high'] = data['close']
                
            if 'close' in data.columns and 'low' not in data.columns:
                data['low'] = data['close']
                
            if 'volume' not in data.columns:
                data['volume'] = 1000  # Default volume
        
        return data

    def get_available_symbols(self, query: str = "") -> List[str]:
        """
        Get available symbols from Yahoo Finance.
        
        Args:
            query: Search query
            
        Returns:
            List of available symbols
        """
        try:
            # This is a simplified implementation
            # In practice, you might want to use a more comprehensive symbol database
            common_symbols = [
                "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX",
                "SPY", "QQQ", "IWM", "GLD", "SLV", "USO", "TLT", "VTI", "VEA",
                "EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTC-USD", "ETH-USD"
            ]
            
            if query:
                return [s for s in common_symbols if query.upper() in s]
            else:
                return common_symbols
                
        except Exception as e:
            self.logger.error(f"Error getting available symbols: {e}")
            return []

    def clear_cache(self):
        """Clear yfinance data cache."""
        self._yfinance_cache.clear()
        self.logger.info("YFinance cache cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache information.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cache_size": len(self._yfinance_cache),
            "cached_keys": list(self._yfinance_cache.keys())
        }
