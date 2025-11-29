"""
Candlestick Data Downloader

A robust module to download, validate, and save OHLCV (candlestick) data from Yahoo Finance.
Supports various ticker symbols, time periods, and intervals with comprehensive error handling.

Author: Naveen Sanjula
License: MIT
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Literal
from dataclasses import dataclass
from enum import Enum

import yfinance as yf
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Period(str, Enum):
    """Valid period values for historical data."""
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YTD = "ytd"
    MAX = "max"


class Interval(str, Enum):
    """Valid interval values for candlestick data."""
    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"


@dataclass
class DownloadConfig:
    """Configuration for downloading candlestick data."""
    ticker: str
    period: Union[str, Period] = Period.ONE_MONTH
    interval: Union[str, Interval] = Interval.ONE_DAY
    auto_adjust: bool = True
    progress: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.ticker = self.ticker.strip().upper()
        if not self.ticker:
            raise ValueError("Ticker symbol cannot be empty")


class CandlestickDownloader:
    """
    A class to download and manage candlestick (OHLCV) data from Yahoo Finance.
    
    This class provides methods to download historical market data with proper
    validation, error handling, and data quality checks.
    
    Examples:
        >>> downloader = CandlestickDownloader()
        >>> data = downloader.download("AAPL", period="1y", interval="1d")
        >>> downloader.save_to_csv(data, "apple_daily.csv")
        
        >>> # Using configuration object
        >>> config = DownloadConfig(ticker="BTC-USD", period="3mo", interval="1h")
        >>> data = downloader.download_with_config(config)
    """
    
    def __init__(self, default_output_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the CandlestickDownloader.
        
        Args:
            default_output_dir: Default directory for saving CSV files.
                              If None, uses current directory.
        """
        self.default_output_dir = Path(default_output_dir) if default_output_dir else Path.cwd()
        self.default_output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized CandlestickDownloader with output dir: {self.default_output_dir}")
    
    def download(
        self,
        ticker: str,
        period: Union[str, Period] = Period.ONE_MONTH,
        interval: Union[str, Interval] = Interval.ONE_DAY,
        auto_adjust: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Download historical OHLCV data from Yahoo Finance.
        
        Args:
            ticker: Yahoo Finance ticker symbol.
                   Examples: "AAPL", "^NSEI" (NIFTY), "BTC-USD", "INR=X" (USD/INR)
            period: Time period for historical data.
                   Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            interval: Candlestick interval.
                     Options: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            auto_adjust: Automatically adjust all OHLC values for splits and dividends.
        
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
            Returns None if download fails or no data is available.
            
        Raises:
            ValueError: If ticker is empty or invalid parameters provided.
        """
        config = DownloadConfig(
            ticker=ticker,
            period=period,
            interval=interval,
            auto_adjust=auto_adjust
        )
        return self.download_with_config(config)
    
    def download_with_config(self, config: DownloadConfig) -> Optional[pd.DataFrame]:
        """
        Download data using a DownloadConfig object.
        
        Args:
            config: DownloadConfig object with all parameters.
            
        Returns:
            DataFrame with OHLCV data or None if failed.
        """
        logger.info(
            f"📊 Downloading: {config.ticker} | "
            f"Period: {config.period} | "
            f"Interval: {config.interval}"
        )
        
        try:
            # Download data from Yahoo Finance
            data = yf.download(
                tickers=config.ticker,
                period=config.period,
                interval=config.interval,
                auto_adjust=config.auto_adjust,
                progress=config.progress
            )
            
            # Validate downloaded data
            if data.empty:
                logger.warning(f"❌ No data found for {config.ticker}")
                return None
            
            # Process and clean the data
            data = self._process_dataframe(data, config.ticker)
            
            logger.info(f"✅ Successfully downloaded {len(data)} records for {config.ticker}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error downloading {config.ticker}: {type(e).__name__}: {str(e)}")
            return None
    
    def _process_dataframe(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Process and clean the downloaded dataframe.
        
        Args:
            df: Raw dataframe from yfinance
            ticker: Ticker symbol for reference
            
        Returns:
            Cleaned and processed dataframe
        """
        # Reset index to make Date a column
        df = df.reset_index()
        
        # Rename 'Datetime' to 'Date' if present (for intraday data)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'Date'})
        
        # Ensure required columns exist
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            logger.warning(f"Missing columns for {ticker}: {missing_cols}")
        
        # Remove any NaN values
        initial_count = len(df)
        df = df.dropna()
        if len(df) < initial_count:
            logger.info(f"Removed {initial_count - len(df)} rows with missing data")
        
        # Sort by date
        df = df.sort_values('Date').reset_index(drop=True)
        
        return df
    
    def save_to_csv(
        self,
        dataframe: Optional[pd.DataFrame],
        filename: Union[str, Path],
        create_dir: bool = True
    ) -> bool:
        """
        Save DataFrame to CSV file with validation.
        
        Args:
            dataframe: DataFrame to save
            filename: Output filename (can include path)
            create_dir: Whether to create parent directories if they don't exist
            
        Returns:
            True if save was successful, False otherwise
        """
        if dataframe is None or dataframe.empty:
            logger.warning("❌ No data to save")
            return False
        
        try:
            filepath = Path(filename)
            
            # Use default output directory if only filename provided
            if not filepath.parent or filepath.parent == Path('.'):
                filepath = self.default_output_dir / filepath
            
            # Create directory if needed
            if create_dir:
                filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to CSV
            dataframe.to_csv(filepath, index=False)
            logger.info(f"💾 Successfully saved {len(dataframe)} records to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving to CSV: {type(e).__name__}: {str(e)}")
            return False
    
    def download_and_save(
        self,
        ticker: str,
        filename: Optional[str] = None,
        period: Union[str, Period] = Period.ONE_MONTH,
        interval: Union[str, Interval] = Interval.ONE_DAY,
        auto_adjust: bool = True
    ) -> bool:
        """
        Convenience method to download and save in one call.
        
        Args:
            ticker: Yahoo Finance ticker symbol
            filename: Output filename. If None, auto-generates based on ticker and timestamp
            period: Time period for historical data
            interval: Candlestick interval
            auto_adjust: Automatically adjust all OHLC values
            
        Returns:
            True if successful, False otherwise
        """
        # Download data
        data = self.download(ticker, period, interval, auto_adjust)
        
        if data is None:
            return False
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{ticker}_{period}_{interval}_{timestamp}.csv"
        
        # Save to CSV
        return self.save_to_csv(data, filename)


# Convenience functions for backward compatibility
def download_candlestick_data(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    Legacy function for backward compatibility.
    
    Downloads historical OHLCV data from Yahoo Finance.
    
    Parameters:
        ticker (str): Yahoo Finance ticker symbol
            Examples: ^NSEI (NIFTY), BTC-USD (Bitcoin), INR=X (USD/INR)
        period (str): Time period
            Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval (str): Data interval
            Options: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    
    Returns:
        pd.DataFrame: DataFrame with Date, Open, High, Low, Close, Volume
    """
    downloader = CandlestickDownloader()
    return downloader.download(ticker, period, interval)


def save_to_csv(dataframe: Optional[pd.DataFrame], filename: str) -> bool:
    """
    Legacy function for backward compatibility.
    Save DataFrame to CSV file.
    
    Args:
        dataframe: DataFrame to save
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    downloader = CandlestickDownloader()
    return downloader.save_to_csv(dataframe, filename)


if __name__ == "__main__":
    # Example usage
    downloader = CandlestickDownloader(default_output_dir="data")
    
    # Example 1: Download Apple stock data
    data = downloader.download("AAPL", period="1y", interval="1d")
    if data is not None:
        downloader.save_to_csv(data, "apple_1year_daily.csv")
    
    # Example 2: Download and save in one call
    downloader.download_and_save("BTC-USD", period="3mo", interval="1h")
    
    # Example 3: Using configuration object
    config = DownloadConfig(ticker="^NSEI", period="1mo", interval="1d")
    data = downloader.download_with_config(config)
    if data is not None:
        print(data.head())
