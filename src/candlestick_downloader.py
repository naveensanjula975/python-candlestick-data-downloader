"""
Candlestick Data Downloader
A module to download OHLCV data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd

def download_candlestick_data(ticker, period="1mo", interval="1d"):
    """
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
    print(f"📊 Downloading: {ticker} | Period: {period} | Interval: {interval}")
    
    try:
        data = yf.download(
            tickers=ticker, 
            period=period, 
            interval=interval, 
            auto_adjust=True, 
            progress=False
        )
        
        if data.empty:
            print(f"❌ No data found for {ticker}")
            return None
        
        data = data.reset_index()
        print(f"✅ Downloaded {len(data)} records")
        return data
        
    except Exception as e:
        print(f"❌ Error downloading {ticker}: {str(e)}")
        return None

def save_to_csv(dataframe, filename):
    """Save DataFrame to CSV file"""
    if dataframe is not None:
        dataframe.to_csv(filename, index=False)
        print(f"💾 Saved to {filename}")
    else:
        print("❌ No data to save")
