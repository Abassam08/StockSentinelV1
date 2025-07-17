import pandas as pd
import numpy as np

class RecommendationEngine:
    """Generate buy/sell recommendations based on financial analysis"""

    def __init__(self):
        self.weights = {
            'financial_health': 0.25,
            'valuation': 0.25,
            'technical': 0.25,
            'growth': 0.15,
            'momentum': 0.10
        }
    def get_recommendation(self, stock_info, hist_data, metrics):
        """Generate comprehensive buy/sell recommendation"""

        # Debug raw input
        print("\n📦 Raw Metrics Input:")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
        
        print("\n📉 Raw Historical Data (Head):")
        if hist_data is not None and not hist_data.empty:
            print(hist_data[['Close']].head())
        else:
            print("  No historical data found.")

        # Calculate scores
        financial_score = self.calculate_financial_health_score(metrics)
        valuation_score = self.calculate_valuation_score(metrics)
        technical_score = self.calculate_technical_score(hist_data)
        growth_score = self.calculate_growth_score(metrics)
        momentum_score = self.calculate_momentum_score(hist_data)

        # Debug scoring breakdown
        print("\n📊 Scoring Breakdown:")
        print("  Financial Score:", financial_score)
        print("  Valuation Score:", valuation_score)
        print("  Technical Score:", technical_score)
        print("  Growth Score:", growth_score)
        print("  Momentum Score:", momentum_score)

        # Weighted overall score
        overall_score = (
            financial_score * self.weights['financial_health'] +
            valuation_score * self.weights['valuation'] +
            technical_score * self.weights['technical'] +
            growth_score * self.weights['growth'] +
            momentum_score * self.weights['momentum']
        )

        # Recommendation decision
        if overall_score >= 75:
            action = "STRONG BUY"
            confidence = min(overall_score, 95)
        elif overall_score >= 60:
            action = "BUY"
            confidence = overall_score
        elif overall_score >= 40:
            action = "HOLD"
            confidence = 100 - abs(overall_score - 50) * 2
        elif overall_score >= 25:
            action = "SELL"
            confidence = 100 - overall_score
        else:
            action = "STRONG SELL"
            confidence = min(100 - overall_score, 95)

        risk_level = self.calculate_risk_level(metrics, hist_data)
        reasoning = self.generate_reasoning(
            overall_score, financial_score, valuation_score, 
            technical_score, growth_score, momentum_score
        )
        factors = self.generate_key_factors(
            stock_info, metrics, financial_score, valuation_score, 
            technical_score, growth_score, momentum_score
        )

        return {
            'action': action,
            'confidence': confidence,
            'overall_score': overall_score,
            'risk_level': risk_level,
            'reasoning': reasoning,
            'factors': factors,
            'scores': {
                'financial_health': financial_score,
                'valuation': valuation_score,
                'technical': technical_score,
                'growth': growth_score,
                'momentum': momentum_score
            }
        }

    def calculate_financial_health_score(self, metrics):
        debt_equity = metrics.get("Debt to Equity", 1)
        current_ratio = metrics.get("Current Ratio", 1)

        score = 50
        if debt_equity < 1:
            score += 20
        elif debt_equity > 2:
            score -= 10

        if current_ratio >= 1.5:
            score += 20
        elif current_ratio < 1:
            score -= 10

        return max(0, min(100, score))

    def calculate_valuation_score(self, metrics):
        score = 50
        pe_ratio = metrics.get("PE Ratio (TTM)", None)
        pb_ratio = metrics.get("Price to Book", None)

        if pe_ratio is not None:
            if pe_ratio < 10:
                score += 15
            elif 10 <= pe_ratio <= 20:
                score += 10
            elif 20 < pe_ratio <= 35:
                score += 5
            else:
                score -= 10

        if pb_ratio is not None:
            if pb_ratio < 1:
                score += 15
            elif 1 <= pb_ratio <= 3:
                score += 10
            elif 3 < pb_ratio <= 6:
                score += 5
            else:
                score -= 10

        return max(0, min(100, score))

    def calculate_technical_score(self, hist_data):
        if hist_data is None or hist_data.empty:
            return 50

        ma50 = hist_data['Close'].rolling(window=50).mean()
        ma200 = hist_data['Close'].rolling(window=200).mean()

        if ma50.iloc[-1] > ma200.iloc[-1]:
            return 80
        elif ma50.iloc[-1] < ma200.iloc[-1]:
            return 30
        else:
            return 50

    def calculate_growth_score(self, metrics):
        revenue_growth = metrics.get("Revenue Growth (YoY)", 0)
        earnings_growth = metrics.get("Earnings Growth (YoY)", 0)

        score = 50
        if revenue_growth > 0.1:
            score += 15
        elif revenue_growth < 0:
            score -= 10

        if earnings_growth > 0.1:
            score += 15
        elif earnings_growth < 0:
            score -= 10

        return max(0, min(100, score))

    def calculate_momentum_score(self, hist_data):
        if hist_data is None or hist_data.empty:
            return 50

        recent = hist_data['Close'].iloc[-1]
        past = hist_data['Close'].iloc[-20] if len(hist_data) >= 20 else hist_data['Close'].iloc[0]
        change = (recent - past) / past

        if change > 0.1:
            return 80
        elif change < -0.1:
            return 20
        else:
            return 50

    def calculate_risk_level(self, metrics, hist_data):
        return "Medium"

    def generate_reasoning(self, overall, f, v, t, g, m):
        return "Based on a mix of financial stability, valuation, technical trends, and growth indicators."

    def generate_key_factors(self, stock_info, metrics, f, v, t, g, m):
        return ["P/E ratio", "Debt-to-equity", "Moving averages", "Growth rate", "Momentum trends"]

