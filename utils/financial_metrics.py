import pandas as pd
import numpy as np

class FinancialMetrics:
    """Calculate and analyze financial metrics for stocks"""
    
    def __init__(self):
        self.metrics = {}
    
    def calculate_metrics(self, stock_info, hist_data):
        """Calculate comprehensive financial metrics"""
        metrics = {}
        
        # Basic valuation metrics
        metrics['pe_ratio'] = stock_info.get('trailingPE')
        metrics['forward_pe'] = stock_info.get('forwardPE')
        metrics['price_to_book'] = stock_info.get('priceToBook')
        metrics['price_to_sales'] = stock_info.get('priceToSalesTrailing12Months')
        
        # Profitability metrics
        metrics['profit_margin'] = stock_info.get('profitMargins')
        metrics['operating_margin'] = stock_info.get('operatingMargins')
        metrics['gross_margin'] = stock_info.get('grossMargins')
        metrics['roe'] = stock_info.get('returnOnEquity')
        metrics['roa'] = stock_info.get('returnOnAssets')
        
        # Financial health
        metrics['debt_to_equity'] = stock_info.get('debtToEquity')
        metrics['current_ratio'] = stock_info.get('currentRatio')
        metrics['quick_ratio'] = stock_info.get('quickRatio')
        
        # Growth metrics
        metrics['revenue_growth'] = stock_info.get('revenueGrowth')
        metrics['earnings_growth'] = stock_info.get('earningsGrowth')
        
        # Dividend metrics
        metrics['dividend_yield'] = stock_info.get('dividendYield')
        metrics['payout_ratio'] = stock_info.get('payoutRatio')
        
        # Market metrics
        metrics['beta'] = stock_info.get('beta')
        metrics['market_cap'] = stock_info.get('marketCap')
        
        # Calculate additional metrics from historical data
        if not hist_data.empty:
            metrics.update(self.calculate_price_metrics(hist_data))
        
        return metrics
    
    def calculate_price_metrics(self, hist_data):
        """Calculate price-based metrics from historical data"""
        price_metrics = {}
        
        if len(hist_data) < 252:  # Need at least 1 year of data
            return price_metrics
        
        # Calculate returns
        returns = hist_data['Close'].pct_change().dropna()
        
        # Volatility (annualized)
        price_metrics['volatility'] = returns.std() * np.sqrt(252)
        
        # Sharpe ratio (assuming risk-free rate of 2%)
        risk_free_rate = 0.02
        excess_returns = returns.mean() * 252 - risk_free_rate
        price_metrics['sharpe_ratio'] = excess_returns / price_metrics['volatility']
        
        # Maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        price_metrics['max_drawdown'] = drawdown.min()
        
        # 52-week high/low
        current_price = hist_data['Close'].iloc[-1]
        week_52_high = hist_data['High'].tail(252).max()
        week_52_low = hist_data['Low'].tail(252).min()
        
        price_metrics['52_week_high'] = week_52_high
        price_metrics['52_week_low'] = week_52_low
        price_metrics['price_vs_52w_high'] = (current_price / week_52_high) - 1
        price_metrics['price_vs_52w_low'] = (current_price / week_52_low) - 1
        
        return price_metrics
    
    def get_financial_health_score(self, metrics):
        """Calculate overall financial health score (0-100)"""
        score = 0
        factors = 0
        
        # Profitability scoring
        if metrics.get('profit_margin') is not None:
            profit_margin = metrics['profit_margin']
            if profit_margin > 0.15:
                score += 20
            elif profit_margin > 0.10:
                score += 15
            elif profit_margin > 0.05:
                score += 10
            elif profit_margin > 0:
                score += 5
            factors += 1
        
        # ROE scoring
        if metrics.get('roe') is not None:
            roe = metrics['roe']
            if roe > 0.20:
                score += 20
            elif roe > 0.15:
                score += 15
            elif roe > 0.10:
                score += 10
            elif roe > 0:
                score += 5
            factors += 1
        
        # Debt management scoring
        if metrics.get('debt_to_equity') is not None:
            debt_to_equity = metrics['debt_to_equity']
            if debt_to_equity < 0.3:
                score += 20
            elif debt_to_equity < 0.5:
                score += 15
            elif debt_to_equity < 1.0:
                score += 10
            elif debt_to_equity < 2.0:
                score += 5
            factors += 1
        
        # Current ratio scoring
        if metrics.get('current_ratio') is not None:
            current_ratio = metrics['current_ratio']
            if current_ratio > 2.0:
                score += 20
            elif current_ratio > 1.5:
                score += 15
            elif current_ratio > 1.2:
                score += 10
            elif current_ratio > 1.0:
                score += 5
            factors += 1
        
        # Growth scoring
        if metrics.get('revenue_growth') is not None:
            revenue_growth = metrics['revenue_growth']
            if revenue_growth > 0.20:
                score += 20
            elif revenue_growth > 0.10:
                score += 15
            elif revenue_growth > 0.05:
                score += 10
            elif revenue_growth > 0:
                score += 5
            factors += 1
        
        # Calculate average score
        if factors > 0:
            return min(score / factors, 100)
        else:
            return 50  # Neutral score if no data
    
    def get_valuation_assessment(self, metrics):
        """Assess if stock is undervalued, fairly valued, or overvalued"""
        assessments = []
        
        # P/E ratio assessment
        pe_ratio = metrics.get('pe_ratio')
        if pe_ratio is not None:
            if pe_ratio < 15:
                assessments.append("Low P/E suggests potential undervaluation")
            elif pe_ratio > 25:
                assessments.append("High P/E suggests potential overvaluation")
            else:
                assessments.append("P/E ratio in reasonable range")
        
        # Price to book assessment
        pb_ratio = metrics.get('price_to_book')
        if pb_ratio is not None:
            if pb_ratio < 1.0:
                assessments.append("Trading below book value")
            elif pb_ratio > 3.0:
                assessments.append("Trading at premium to book value")
        
        # Price to sales assessment
        ps_ratio = metrics.get('price_to_sales')
        if ps_ratio is not None:
            if ps_ratio < 1.0:
                assessments.append("Low price-to-sales ratio")
            elif ps_ratio > 5.0:
                assessments.append("High price-to-sales ratio")
        
        return assessments
    
    def explain_metric(self, metric_name):
        """Provide beginner-friendly explanations of financial metrics"""
        explanations = {
            'pe_ratio': "Price-to-Earnings ratio: How much investors pay for each dollar of earnings. Lower values may indicate better value.",
            'market_cap': "Market Capitalization: Total value of all company shares. Large cap (>$10B), Mid cap ($2-10B), Small cap (<$2B).",
            'dividend_yield': "Dividend Yield: Annual dividend payment as percentage of stock price. Higher yields provide more income.",
            'beta': "Beta: Measures stock volatility vs. market. Beta > 1 means more volatile, Beta < 1 means less volatile than market.",
            'roe': "Return on Equity: How efficiently company uses shareholders' money to generate profits. Higher is generally better.",
            'debt_to_equity': "Debt-to-Equity: Company's debt relative to shareholders' equity. Lower ratios generally indicate financial stability.",
            'profit_margin': "Profit Margin: Percentage of revenue that becomes profit. Higher margins indicate better efficiency.",
            'revenue_growth': "Revenue Growth: Rate at which company's sales are increasing. Positive growth is generally good sign."
        }
        
        return explanations.get(metric_name, "Financial metric used for stock analysis")
