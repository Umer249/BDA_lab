#!/usr/bin/env python3
"""
Test script for Financial Data functionality
"""

import sys
sys.path.append('src')

from financial_data import FinancialDataFetcher
import pandas as pd
import matplotlib.pyplot as plt

def test_financial_data():
    """Test the financial data fetching functionality."""
    
    print("🚀 Testing Financial Data Fetcher...")
    
    # Initialize the fetcher
    fetcher = FinancialDataFetcher()
    
    # Test 1: Fetch single stock data
    print("\n📊 Test 1: Fetching AAPL stock data...")
    try:
        aapl_data = fetcher.fetch_stock_data("AAPL", period="6mo", interval="1d")
        if aapl_data is not None:
            print(f"✅ Successfully fetched AAPL data: {aapl_data.shape}")
            print(f"📈 Date range: {aapl_data['Date'].min()} to {aapl_data['Date'].max()}")
            print(f"💰 Price range: ${aapl_data['Close'].min():.2f} - ${aapl_data['Close'].max():.2f}")
        else:
            print("❌ Failed to fetch AAPL data")
    except Exception as e:
        print(f"❌ Error fetching AAPL data: {str(e)}")
    
    # Test 2: Add technical indicators
    print("\n🔧 Test 2: Adding technical indicators...")
    try:
        if aapl_data is not None:
            aapl_with_indicators = fetcher.add_technical_indicators(aapl_data)
            technical_columns = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'BB_Upper', 'BB_Lower']
            available_indicators = [col for col in technical_columns if col in aapl_with_indicators.columns]
            print(f"✅ Added technical indicators: {', '.join(available_indicators)}")
            print(f"📊 Dataset now has {aapl_with_indicators.shape[1]} columns")
        else:
            print("❌ No data available for adding indicators")
    except Exception as e:
        print(f"❌ Error adding indicators: {str(e)}")
    
    # Test 3: Create ML dataset for classification
    print("\n🤖 Test 3: Creating ML dataset for price direction prediction...")
    try:
        if aapl_data is not None:
            ml_data_classification = fetcher.prepare_ml_dataset(
                data=aapl_data,
                task_type='classification',
                target_method='price_direction',
                periods=1,
                include_technical_indicators=True
            )
            print(f"✅ Classification dataset created: {ml_data_classification.shape}")
            
            # Check target distribution
            target_counts = ml_data_classification['Target'].value_counts()
            print(f"📊 Target distribution: {dict(target_counts)}")
            
            # Show feature columns
            feature_cols = [col for col in ml_data_classification.columns if col != 'Target']
            print(f"🔢 Features ({len(feature_cols)}): {', '.join(feature_cols[:10])}{'...' if len(feature_cols) > 10 else ''}")
        else:
            print("❌ No data available for ML dataset creation")
    except Exception as e:
        print(f"❌ Error creating classification dataset: {str(e)}")
    
    # Test 4: Create ML dataset for regression
    print("\n📈 Test 4: Creating ML dataset for return prediction...")
    try:
        if aapl_data is not None:
            ml_data_regression = fetcher.prepare_ml_dataset(
                data=aapl_data,
                task_type='regression',
                target_method='return',
                periods=1,
                include_technical_indicators=True
            )
            print(f"✅ Regression dataset created: {ml_data_regression.shape}")
            
            # Check target statistics
            target_stats = ml_data_regression['Target'].describe()
            print(f"📊 Target statistics:")
            print(f"   Mean return: {target_stats['mean']:.4f}%")
            print(f"   Std return: {target_stats['std']:.4f}%")
            print(f"   Min return: {target_stats['min']:.4f}%")
            print(f"   Max return: {target_stats['max']:.4f}%")
        else:
            print("❌ No data available for ML dataset creation")
    except Exception as e:
        print(f"❌ Error creating regression dataset: {str(e)}")
    
    # Test 5: Get popular stocks
    print("\n🌟 Test 5: Getting popular stocks...")
    try:
        popular_stocks = fetcher.get_popular_stocks()
        print("✅ Popular stock categories:")
        for category, symbols in popular_stocks.items():
            print(f"   {category}: {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}")
    except Exception as e:
        print(f"❌ Error getting popular stocks: {str(e)}")
    
    # Test 6: Market summary
    print("\n📋 Test 6: Getting market summary...")
    try:
        tech_stocks = ["AAPL", "GOOGL", "MSFT"]
        market_summary = fetcher.get_market_data_summary(tech_stocks)
        if not market_summary.empty:
            print("✅ Market summary:")
            print(market_summary.to_string(index=False))
        else:
            print("❌ No market summary data available")
    except Exception as e:
        print(f"❌ Error getting market summary: {str(e)}")
    
    # Test 7: Crypto data
    print("\n₿ Test 7: Fetching cryptocurrency data...")
    try:
        btc_data = fetcher.fetch_stock_data("BTC-USD", period="1mo", interval="1d")
        if btc_data is not None:
            print(f"✅ Successfully fetched BTC data: {btc_data.shape}")
            print(f"💰 BTC price range: ${btc_data['Close'].min():.2f} - ${btc_data['Close'].max():.2f}")
        else:
            print("❌ Failed to fetch BTC data")
    except Exception as e:
        print(f"❌ Error fetching BTC data: {str(e)}")
    
    print("\n🎉 Financial data testing completed!")
    
    # Save sample datasets
    print("\n💾 Saving sample datasets...")
    try:
        if 'ml_data_classification' in locals() and not ml_data_classification.empty:
            ml_data_classification.to_csv('data/aapl_classification_sample.csv', index=False)
            print("✅ Saved: data/aapl_classification_sample.csv")
        
        if 'ml_data_regression' in locals() and not ml_data_regression.empty:
            ml_data_regression.to_csv('data/aapl_regression_sample.csv', index=False)
            print("✅ Saved: data/aapl_regression_sample.csv")
            
        if 'aapl_data' in locals() and aapl_data is not None:
            aapl_data.to_csv('data/aapl_raw_data.csv', index=False)
            print("✅ Saved: data/aapl_raw_data.csv")
            
    except Exception as e:
        print(f"❌ Error saving datasets: {str(e)}")

if __name__ == "__main__":
    test_financial_data() 