"""
Candlestick Data Downloader Package

A professional Python package for downloading and managing OHLCV data from Yahoo Finance.
"""

__version__ = "1.0.0"
__author__ = "Naveen Sanjula"
__license__ = "MIT"

from .candlestick_downloader import (
    CandlestickDownloader,
    DownloadConfig,
    Period,
    Interval,
    download_candlestick_data,
    save_to_csv,
)

__all__ = [
    "CandlestickDownloader",
    "DownloadConfig",
    "Period",
    "Interval",
    "download_candlestick_data",
    "save_to_csv",
]
