import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import requests
import json


class FinancialDataFetcher:
    """Fetch and process financial data from Yahoo Finance API."""
    
    def __init__(self):
        self.data = None
        self.ticker_info = None
        
    def get_ticker_info(self, symbol):
        """Get basic information about a ticker symbol."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info
        except Exception as e:
            st.error(f"Error fetching ticker info for {symbol}: {str(e)}")
            return None
    
    def fetch_stock_data(self, symbol, period="1y", interval="1d"):
        """
        Fetch stock data for a given symbol.
        
        Parameters:
        - symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        - period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        - interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                st.error(f"No data found for symbol {symbol}")
                return None
                
            # Reset index to make Date a column
            data.reset_index(inplace=True)
            
            # Store ticker info
            self.ticker_info = self.get_ticker_info(symbol)
            
            return data
            
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def fetch_multiple_stocks(self, symbols, period="1y", interval="1d"):
        """Fetch data for multiple stock symbols."""
        try:
            # Convert symbols to string if it's a list
            if isinstance(symbols, list):
                symbols_str = " ".join(symbols)
            else:
                symbols_str = symbols
                
            data = yf.download(symbols_str, period=period, interval=interval, group_by='ticker')
            
            if data.empty:
                st.error("No data found for the specified symbols")
                return None
                
            return data
            
        except Exception as e:
            st.error(f"Error fetching multiple stocks data: {str(e)}")
            return None
    
    def add_technical_indicators(self, data):
        """Add technical indicators to the stock data."""
        try:
            df = data.copy()
            
            # Simple Moving Averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            
            # Exponential Moving Averages
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # RSI (Relative Strength Index)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            # Volume indicators
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
            
            # Price change indicators
            df['Daily_Return'] = df['Close'].pct_change()
            df['Price_Change'] = df['Close'].diff()
            df['Price_Change_Pct'] = (df['Close'] - df['Open']) / df['Open'] * 100
            
            # Volatility
            df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
            
            # High-Low spread
            df['HL_Spread'] = df['High'] - df['Low']
            df['HL_Spread_Pct'] = (df['High'] - df['Low']) / df['Close'] * 100
            
            return df
            
        except Exception as e:
            st.error(f"Error adding technical indicators: {str(e)}")
            return data
    
    def create_classification_target(self, data, method='price_direction', periods=1):
        """
        Create classification targets for ML models.
        
        Methods:
        - 'price_direction': 1 if next day's close > today's close, 0 otherwise
        - 'price_movement': 1 if price moves up by more than threshold, -1 if down, 0 otherwise
        - 'volatility_breakout': 1 if price breaks out of volatility bands
        """
        try:
            df = data.copy()
            
            if method == 'price_direction':
                df['Target'] = (df['Close'].shift(-periods) > df['Close']).astype(int)
                
            elif method == 'price_movement':
                # Define threshold as 1% price movement
                threshold = 0.01
                future_return = (df['Close'].shift(-periods) - df['Close']) / df['Close']
                df['Target'] = np.where(future_return > threshold, 1,
                                      np.where(future_return < -threshold, -1, 0))
                
            elif method == 'volatility_breakout':
                # Using Bollinger Bands for breakout detection
                df = self.add_technical_indicators(df)
                future_high = df['High'].shift(-periods)
                future_low = df['Low'].shift(-periods)
                
                breakout_up = future_high > df['BB_Upper']
                breakout_down = future_low < df['BB_Lower']
                
                df['Target'] = np.where(breakout_up, 1,
                                      np.where(breakout_down, -1, 0))
            
            # Remove rows with NaN targets (last few rows)
            df = df.dropna(subset=['Target'])
            
            return df
            
        except Exception as e:
            st.error(f"Error creating classification target: {str(e)}")
            return data
    
    def create_regression_target(self, data, target_type='next_close', periods=1):
        """
        Create regression targets for ML models.
        
        Target types:
        - 'next_close': Next day's closing price
        - 'return': Future return percentage
        - 'volatility': Future volatility
        """
        try:
            df = data.copy()
            
            if target_type == 'next_close':
                df['Target'] = df['Close'].shift(-periods)
                
            elif target_type == 'return':
                df['Target'] = (df['Close'].shift(-periods) - df['Close']) / df['Close'] * 100
                
            elif target_type == 'volatility':
                df['Target'] = df['Close'].rolling(window=periods).std().shift(-periods)
            
            # Remove rows with NaN targets
            df = df.dropna(subset=['Target'])
            
            return df
            
        except Exception as e:
            st.error(f"Error creating regression target: {str(e)}")
            return data
    
    def get_popular_stocks(self):
        """Get a list of popular stock symbols."""
        popular_stocks = {
            'Technology': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'],
            'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO'],
            'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB'],
            'Consumer': ['PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD'],
            'Indices': ['^GSPC', '^DJI', '^IXIC', '^RUT'],  # S&P 500, Dow, Nasdaq, Russell 2000
            'Crypto': ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD']
        }
        return popular_stocks
    
    def search_symbol(self, query):
        """Search for stock symbols based on company name."""
        try:
            # This is a simple implementation - in production, you might want to use
            # a more sophisticated symbol search API
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            
            if 'symbol' in info:
                return [(info.get('symbol', query), info.get('longName', 'Unknown'))]
            else:
                return []
                
        except Exception as e:
            return []
    
    def get_market_data_summary(self, symbols):
        """Get a summary of market data for multiple symbols."""
        try:
            summary_data = []
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    latest_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else latest_price
                    change = latest_price - prev_price
                    change_pct = (change / prev_price * 100) if prev_price != 0 else 0
                    
                    summary_data.append({
                        'Symbol': symbol,
                        'Name': info.get('longName', 'Unknown'),
                        'Price': round(latest_price, 2),
                        'Change': round(change, 2),
                        'Change %': round(change_pct, 2),
                        'Volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
                        'Market Cap': info.get('marketCap', 'N/A'),
                        'Sector': info.get('sector', 'Unknown')
                    })
            
            return pd.DataFrame(summary_data)
            
        except Exception as e:
            st.error(f"Error getting market summary: {str(e)}")
            return pd.DataFrame()
    
    def prepare_ml_dataset(self, data, task_type='classification', 
                          target_method='price_direction', periods=1, 
                          include_technical_indicators=True):
        """
        Prepare dataset for machine learning.
        
        Parameters:
        - data: Stock price data
        - task_type: 'classification' or 'regression'
        - target_method: Method for creating target variable
        - periods: Number of periods to look ahead
        - include_technical_indicators: Whether to include technical indicators
        """
        try:
            df = data.copy()
            
            # Add technical indicators if requested
            if include_technical_indicators:
                df = self.add_technical_indicators(df)
            
            # Create target variable
            if task_type == 'classification':
                df = self.create_classification_target(df, method=target_method, periods=periods)
            else:
                df = self.create_regression_target(df, target_type=target_method, periods=periods)
            
            # Remove non-numeric columns and handle Date column
            columns_to_drop = []
            if 'Date' in df.columns:
                # Extract date features
                df['Year'] = pd.to_datetime(df['Date']).dt.year
                df['Month'] = pd.to_datetime(df['Date']).dt.month
                df['DayOfWeek'] = pd.to_datetime(df['Date']).dt.dayofweek
                df['Quarter'] = pd.to_datetime(df['Date']).dt.quarter
                columns_to_drop.append('Date')
            
            # Remove any remaining non-numeric columns
            for col in df.columns:
                if df[col].dtype == 'object' and col != 'Target':
                    columns_to_drop.append(col)
            
            df = df.drop(columns=columns_to_drop, errors='ignore')
            
            # Remove rows with any NaN values
            df = df.dropna()
            
            return df
            
        except Exception as e:
            st.error(f"Error preparing ML dataset: {str(e)}")
            return data 