"""
Data fetching module for stock market data.

This module provides functionality to fetch stock market data from various sources.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf
from tqdm import tqdm

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Fetches stock market data from various sources.

    This class provides methods to fetch historical and real-time stock data
    from sources like Yahoo Finance and Google Finance.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the DataFetcher.

        Args:
            cache_dir: Directory to cache fetched data (optional)
        """
        self.cache_dir = cache_dir
        self._setup_cache()

    def _setup_cache(self) -> None:
        """Set up the cache directory if caching is enabled."""
        if self.cache_dir:
            import os

            os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_stock_data(
        self, symbol: str, days: int = 365, interval: str = "1d", **kwargs
    ) -> pd.DataFrame:
        """
        Fetch historical stock data for a given symbol.

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            days: Number of days of historical data to fetch
            interval: Data interval ('1d', '1h', etc.)
            **kwargs: Additional arguments to pass to yfinance

        Returns:
            DataFrame with historical stock data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            logger.debug(f"Fetching {days} days of {interval} data for {symbol}")
            data = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False,
                **kwargs,
            )

            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()

            return data

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()

    def fetch_multiple_stocks(
        self, symbols: List[str], days: int = 365, interval: str = "1d", **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stock symbols.

        Args:
            symbols: List of stock symbols
            days: Number of days of historical data to fetch
            interval: Data interval ('1d', '1h', etc.)
            **kwargs: Additional arguments to pass to yfinance

        Returns:
            Dictionary mapping symbols to their DataFrames
        """
        results = {}

        for symbol in tqdm(symbols, desc="Fetching stock data"):
            data = self.fetch_stock_data(symbol, days, interval, **kwargs)
            if not data.empty:
                results[symbol] = data

        return results

    def get_company_info(self, symbol: str) -> Dict[str, str]:
        """
        Get company information for a given symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with company information
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "description": info.get("longBusinessSummary", ""),
                "website": info.get("website", ""),
            }
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            return {}

    def get_market_index(
        self, index_symbol: str = "^NSEI", days: int = 365
    ) -> pd.DataFrame:
        """
        Fetch market index data.

        Args:
            index_symbol: Index symbol (e.g., '^NSEI' for NIFTY 50)
            days: Number of days of historical data to fetch

        Returns:
            DataFrame with index data
        """
        return self.fetch_stock_data(index_symbol, days=days)
