import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class StockAnalyzer:
    """Main stock analysis class for processing financial data"""
    
    def __init__(self):
        self.technical_indicators = {}
    
    def calculate_moving_averages(self, df, periods=[20, 50, 200]):
        """Calculate moving averages for given periods"""
        ma_data = {}
        for period in periods:
            if len(df) >= period:
                ma_data[f'MA_{period}'] = df['Close'].rolling(window=period).mean()
        return ma_data
    
    def calculate_rsi(self, df, period=14):
        """Calculate Relative Strength Index"""
        if len(df) < period:
            return None
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, df, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if len(df) < period:
            return None, None, None
        
        ma = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()
        
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        return upper_band, ma, lower_band
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(df) < slow:
            return None, None, None
        
        exp1 = df['Close'].ewm(span=fast).mean()
        exp2 = df['Close'].ewm(span=slow).mean()
        
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return macd, signal_line, histogram
    
    def calculate_volatility(self, df, period=30):
        """Calculate historical volatility"""
        if len(df) < period:
            return None
        
        returns = df['Close'].pct_change()
        volatility = returns.rolling(window=period).std() * np.sqrt(252)  # Annualized
        return volatility
    
    def get_support_resistance(self, df, window=20):
        """Calculate support and resistance levels"""
        if len(df) < window:
            return None, None
        
        # Simple support/resistance based on local minima/maxima
        highs = df['High'].rolling(window=window, center=True).max()
        lows = df['Low'].rolling(window=window, center=True).min()
        
        resistance = highs[df['High'] == highs].dropna()
        support = lows[df['Low'] == lows].dropna()
        
        return support, resistance
    
    def analyze_trend(self, df, short_period=20, long_period=50):
        """Analyze current trend direction"""
        if len(df) < long_period:
            return "Insufficient data"
        
        short_ma = df['Close'].rolling(window=short_period).mean().iloc[-1]
        long_ma = df['Close'].rolling(window=long_period).mean().iloc[-1]
        current_price = df['Close'].iloc[-1]
        
        if current_price > short_ma > long_ma:
            return "Strong Uptrend"
        elif current_price > short_ma and short_ma < long_ma:
            return "Weak Uptrend"
        elif current_price < short_ma < long_ma:
            return "Strong Downtrend"
        elif current_price < short_ma and short_ma > long_ma:
            return "Weak Downtrend"
        else:
            return "Sideways"
    
    def calculate_price_momentum(self, df, period=10):
        """Calculate price momentum"""
        if len(df) < period:
            return None
        
        current_price = df['Close'].iloc[-1]
        past_price = df['Close'].iloc[-period]
        
        momentum = ((current_price - past_price) / past_price) * 100
        return momentum
    
    def get_volume_analysis(self, df, period=20):
        """Analyze volume patterns"""
        if len(df) < period:
            return "Insufficient data"
        
        avg_volume = df['Volume'].rolling(window=period).mean().iloc[-1]
        recent_volume = df['Volume'].iloc[-5:].mean()  # Last 5 days
        
        volume_ratio = recent_volume / avg_volume
        
        if volume_ratio > 1.5:
            return "High Volume"
        elif volume_ratio > 1.2:
            return "Above Average Volume"
        elif volume_ratio < 0.8:
            return "Low Volume"
        else:
            return "Average Volume"
    
    def get_technical_summary(self, df):
        """Get overall technical analysis summary"""
        if len(df) < 50:
            return {
                'trend': 'Insufficient data',
                'momentum': None,
                'volume': 'Insufficient data',
                'signals': []
            }
        
        # Calculate key indicators
        ma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        ma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
        current_price = df['Close'].iloc[-1]
        
        rsi = self.calculate_rsi(df)
        rsi_current = rsi.iloc[-1] if rsi is not None else None
        
        momentum = self.calculate_price_momentum(df)
        trend = self.analyze_trend(df)
        volume_analysis = self.get_volume_analysis(df)
        
        # Generate signals
        signals = []
        
        if rsi_current:
            if rsi_current > 70:
                signals.append("RSI indicates overbought conditions")
            elif rsi_current < 30:
                signals.append("RSI indicates oversold conditions")
        
        if current_price > ma_20 > ma_50:
            signals.append("Price above both short and long-term moving averages")
        elif current_price < ma_20 < ma_50:
            signals.append("Price below both short and long-term moving averages")
        
        if momentum and momentum > 5:
            signals.append("Strong positive momentum")
        elif momentum and momentum < -5:
            signals.append("Strong negative momentum")
        
        return {
            'trend': trend,
            'momentum': momentum,
            'volume': volume_analysis,
            'rsi': rsi_current,
            'signals': signals
        }
