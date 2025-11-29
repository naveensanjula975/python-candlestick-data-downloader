"""
Unit tests for CandlestickDownloader

Run with: pytest tests/
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from candlestick_downloader import (
    CandlestickDownloader,
    DownloadConfig,
    Period,
    Interval,
    download_candlestick_data,
)


class TestDownloadConfig:
    """Test DownloadConfig dataclass."""
    
    def test_valid_config(self):
        """Test creating a valid configuration."""
        config = DownloadConfig(ticker="AAPL", period="1y", interval="1d")
        assert config.ticker == "AAPL"
        assert config.period == "1y"
        assert config.interval == "1d"
    
    def test_ticker_normalization(self):
        """Test that ticker is normalized to uppercase."""
        config = DownloadConfig(ticker="  aapl  ")
        assert config.ticker == "AAPL"
    
    def test_empty_ticker_raises_error(self):
        """Test that empty ticker raises ValueError."""
        with pytest.raises(ValueError, match="Ticker symbol cannot be empty"):
            DownloadConfig(ticker="")
    
    def test_default_values(self):
        """Test default period and interval."""
        config = DownloadConfig(ticker="AAPL")
        assert config.period == Period.ONE_MONTH
        assert config.interval == Interval.ONE_DAY


class TestCandlestickDownloader:
    """Test CandlestickDownloader class."""
    
    @pytest.fixture
    def downloader(self, tmp_path):
        """Create a downloader instance with temp directory."""
        return CandlestickDownloader(default_output_dir=tmp_path)
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=5),
            'Open': [100, 101, 102, 103, 104],
            'High': [105, 106, 107, 108, 109],
            'Low': [95, 96, 97, 98, 99],
            'Close': [102, 103, 104, 105, 106],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        })
    
    def test_initialization(self, tmp_path):
        """Test downloader initialization."""
        downloader = CandlestickDownloader(default_output_dir=tmp_path)
        assert downloader.default_output_dir == tmp_path
        assert tmp_path.exists()
    
    def test_initialization_default_dir(self):
        """Test downloader with default directory."""
        downloader = CandlestickDownloader()
        assert downloader.default_output_dir == Path.cwd()
    
    @patch('candlestick_downloader.yf.download')
    def test_download_success(self, mock_download, downloader, sample_dataframe):
        """Test successful data download."""
        # Setup mock
        mock_download.return_value = sample_dataframe.set_index('Date')
        
        # Download data
        result = downloader.download("AAPL", period="1mo", interval="1d")
        
        # Verify
        assert result is not None
        assert len(result) == 5
        assert 'Date' in result.columns
        mock_download.assert_called_once()
    
    @patch('candlestick_downloader.yf.download')
    def test_download_empty_data(self, mock_download, downloader):
        """Test download with no data returned."""
        # Setup mock to return empty DataFrame
        mock_download.return_value = pd.DataFrame()
        
        # Download data
        result = downloader.download("INVALID")
        
        # Verify
        assert result is None
    
    @patch('candlestick_downloader.yf.download')
    def test_download_exception(self, mock_download, downloader):
        """Test download when exception occurs."""
        # Setup mock to raise exception
        mock_download.side_effect = Exception("Network error")
        
        # Download data
        result = downloader.download("AAPL")
        
        # Verify
        assert result is None
    
    def test_save_to_csv_success(self, downloader, sample_dataframe, tmp_path):
        """Test successful CSV save."""
        filename = "test_output.csv"
        result = downloader.save_to_csv(sample_dataframe, filename)
        
        assert result is True
        output_file = tmp_path / filename
        assert output_file.exists()
        
        # Verify content
        loaded_df = pd.read_csv(output_file)
        assert len(loaded_df) == 5
    
    def test_save_to_csv_none_dataframe(self, downloader):
        """Test saving None DataFrame."""
        result = downloader.save_to_csv(None, "output.csv")
        assert result is False
    
    def test_save_to_csv_empty_dataframe(self, downloader):
        """Test saving empty DataFrame."""
        result = downloader.save_to_csv(pd.DataFrame(), "output.csv")
        assert result is False
    
    def test_save_to_csv_with_path(self, downloader, sample_dataframe, tmp_path):
        """Test saving to custom path."""
        subdir = tmp_path / "subdir"
        filepath = subdir / "output.csv"
        
        result = downloader.save_to_csv(sample_dataframe, filepath, create_dir=True)
        
        assert result is True
        assert filepath.exists()
    
    @patch.object(CandlestickDownloader, 'download')
    @patch.object(CandlestickDownloader, 'save_to_csv')
    def test_download_and_save(self, mock_save, mock_download, downloader, sample_dataframe):
        """Test download_and_save convenience method."""
        # Setup mocks
        mock_download.return_value = sample_dataframe
        mock_save.return_value = True
        
        # Call method
        result = downloader.download_and_save("AAPL", filename="test.csv")
        
        # Verify
        assert result is True
        mock_download.assert_called_once()
        mock_save.assert_called_once()
    
    @patch.object(CandlestickDownloader, 'download')
    def test_download_and_save_auto_filename(self, mock_download, downloader, sample_dataframe):
        """Test download_and_save with auto-generated filename."""
        mock_download.return_value = sample_dataframe
        
        result = downloader.download_and_save("AAPL", filename=None)
        
        # Should succeed and generate filename
        assert result is True
        mock_download.assert_called_once()
    
    def test_process_dataframe(self, downloader):
        """Test DataFrame processing."""
        # Create raw dataframe with index
        raw_df = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [95, 96, 97],
            'Close': [102, 103, 104],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2024-01-01', periods=3))
        
        result = downloader._process_dataframe(raw_df, "AAPL")
        
        assert 'Date' in result.columns
        assert len(result) == 3
        assert result['Date'].is_monotonic_increasing


class TestEnums:
    """Test Period and Interval enums."""
    
    def test_period_enum(self):
        """Test Period enum values."""
        assert Period.ONE_DAY == "1d"
        assert Period.ONE_MONTH == "1mo"
        assert Period.ONE_YEAR == "1y"
    
    def test_interval_enum(self):
        """Test Interval enum values."""
        assert Interval.ONE_MINUTE == "1m"
        assert Interval.ONE_DAY == "1d"
        assert Interval.ONE_WEEK == "1wk"


class TestLegacyFunctions:
    """Test backward compatibility functions."""
    
    @patch('candlestick_downloader.yf.download')
    def test_download_candlestick_data(self, mock_download):
        """Test legacy download function."""
        # Setup mock
        sample_df = pd.DataFrame({
            'Open': [100],
            'High': [105],
            'Low': [95],
            'Close': [102],
            'Volume': [1000]
        }, index=pd.date_range('2024-01-01', periods=1))
        mock_download.return_value = sample_df
        
        # Call legacy function
        result = download_candlestick_data("AAPL", period="1mo", interval="1d")
        
        # Verify
        assert result is not None
        assert 'Date' in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
