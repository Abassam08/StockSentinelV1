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
        
        # Calculate individual scores
        financial_score = self.calculate_financial_health_score(metrics)
        valuation_score = self.calculate_valuation_score(metrics)
        technical_score = self.calculate_technical_score(hist_data)
        growth_score = self.calculate_growth_score(metrics)
        momentum_score = self.calculate_momentum_score(hist_data)
        
        # Calculate weighted overall score
        overall_score = (
            financial_score * self.weights['financial_health'] +
            valuation_score * self.weights['valuation'] +
            technical_score * self.weights['technical'] +
            growth_score * self.weights['growth'] +
            momentum_score * self.weights['momentum']
        )
        
        # Determine recommendation
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
        
        # Determine risk level
        risk_level = self.calculate_risk_level(metrics, hist_data)
        
        # Generate reasoning
        reasoning = self.generate_reasoning(
            overall_score, financial_score, valuation_score, 
            technical_score, growth_score, momentum_score
        )
        
        # Generate key factors
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
        """Calculate financial health score (0-100)"""
        score = 0
        factors = 0
        
        # Profitability
        profit_margin = metrics.get('profit_margin')
        if profit_margin is not None:
            if profit_margin > 0.20:
                score += 25
            elif profit_margin > 0.15:
                score += 20
            elif profit_margin > 0.10:
                score += 15
            elif profit_margin > 0.05:
                score += 10
            elif profit_margin > 0:
                score += 5
            factors += 1
        
        # ROE
        roe = metrics.get('roe')
        if roe is not None:
            if roe > 0.20:
                score += 25
            elif roe > 0.15:
                score += 20
            elif roe > 0.10:
                score += 15
            elif roe > 0.05:
                score += 10
            elif roe > 0:
                score += 5
            factors += 1
        
        # Debt management
        debt_to_equity = metrics.get('debt_to_equity')
        if debt_to_equity is not None:
            if debt_to_equity < 0.3:
                score += 25
            elif debt_to_equity < 0.5:
                score += 20
            elif debt_to_equity < 1.0:
                score += 15
            elif debt_to_equity < 2.0:
                score += 10
            else:
                score += 5
            factors += 1
        
        # Current ratio
        current_ratio = metrics.get('current_ratio')
        if current_ratio is not None:
            if current_ratio > 2.0:
                score += 25
            elif current_ratio > 1.5:
                score += 20
            elif current_ratio > 1.2:
                score += 15
            elif current_ratio > 1.0:
                score += 10
            else:
                score += 5
            factors += 1
        
        return score / factors if factors > 0 else 50
    
    def calculate_valuation_score(self, metrics):
        """Calculate valuation score (0-100)"""
        score = 0
        factors = 0
        
        # P/E ratio
        pe_ratio = metrics.get('pe_ratio')
        if pe_ratio is not None and pe_ratio > 0:
            if pe_ratio < 10:
                score += 25
            elif pe_ratio < 15:
                score += 20
            elif pe_ratio < 20:
                score += 15
            elif pe_ratio < 25:
                score += 10
            elif pe_ratio < 35:
                score += 5
            factors += 1
        
        # Price to book
        pb_ratio = metrics.get('price_to_book')
        if pb_ratio is not None and pb_ratio > 0:
            if pb_ratio < 1.0:
                score += 25
            elif pb_ratio < 1.5:
                score += 20
            elif pb_ratio < 2.0:
                score += 15
            elif pb_ratio < 3.0:
                score += 10
            elif pb_ratio < 4.0:
                score += 5
            factors += 1
        
        # Price to sales
        ps_ratio = metrics.get('price_to_sales')
        if ps_ratio is not None and ps_ratio > 0:
            if ps_ratio < 1.0:
                score += 25
            elif ps_ratio < 2.0:
                score += 20
            elif ps_ratio < 3.0:
                score += 15
            elif ps_ratio < 5.0:
                score += 10
            elif ps_ratio < 7.0:
                score += 5
            factors += 1
        
        return score / factors if factors > 0 else 50
    
    def calculate_technical_score(self, hist_data):
        """Calculate technical analysis score (0-100)"""
        if len(hist_data) < 50:
            return 50
        
        score = 0
        factors = 0
        
        # Moving average analysis
        if len(hist_data) >= 20:
            ma_20 = hist_data['Close'].rolling(window=20).mean().iloc[-1]
            current_price = hist_data['Close'].iloc[-1]
            
            if current_price > ma_20:
                score += 25
            else:
                score += 10
            factors += 1
        
        # Price momentum
        if len(hist_data) >= 10:
            price_10_days_ago = hist_data['Close'].iloc[-10]
            current_price = hist_data['Close'].iloc[-1]
            momentum = (current_price - price_10_days_ago) / price_10_days_ago
            
            if momentum > 0.05:
                score += 25
            elif momentum > 0.02:
                score += 20
            elif momentum > 0:
                score += 15
            elif momentum > -0.02:
                score += 10
            else:
                score += 5
            factors += 1
        
        # Volume analysis
        if len(hist_data) >= 20:
            avg_volume = hist_data['Volume'].rolling(window=20).mean().iloc[-1]
            recent_volume = hist_data['Volume'].iloc[-5:].mean()
            
            if recent_volume > avg_volume * 1.2:
                score += 25
            elif recent_volume > avg_volume:
                score += 20
            else:
                score += 15
            factors += 1
        
        return score / factors if factors > 0 else 50
    
    def calculate_growth_score(self, metrics):
        """Calculate growth score (0-100)"""
        score = 0
        factors = 0
        
        # Revenue growth
        revenue_growth = metrics.get('revenue_growth')
        if revenue_growth is not None:
            if revenue_growth > 0.25:
                score += 25
            elif revenue_growth > 0.15:
                score += 20
            elif revenue_growth > 0.10:
                score += 15
            elif revenue_growth > 0.05:
                score += 10
            elif revenue_growth > 0:
                score += 5
            factors += 1
        
        # Earnings growth
        earnings_growth = metrics.get('earnings_growth')
        if earnings_growth is not None:
            if earnings_growth > 0.25:
                score += 25
            elif earnings_growth > 0.15:
                score += 20
            elif earnings_growth > 0.10:
                score += 15
            elif earnings_growth > 0.05:
                score += 10
            elif earnings_growth > 0:
                score += 5
            factors += 1
        
        return score / factors if factors > 0 else 50
    
    def calculate_momentum_score(self, hist_data):
        """Calculate momentum score (0-100)"""
        if len(hist_data) < 30:
            return 50
        
        # Calculate different momentum periods
        periods = [5, 10, 20]
        momentum_scores = []
        
        current_price = hist_data['Close'].iloc[-1]
        
        for period in periods:
            if len(hist_data) >= period:
                past_price = hist_data['Close'].iloc[-period]
                momentum = (current_price - past_price) / past_price
                
                if momentum > 0.10:
                    momentum_scores.append(25)
                elif momentum > 0.05:
                    momentum_scores.append(20)
                elif momentum > 0.02:
                    momentum_scores.append(15)
                elif momentum > 0:
                    momentum_scores.append(10)
                elif momentum > -0.02:
                    momentum_scores.append(8)
                elif momentum > -0.05:
                    momentum_scores.append(5)
                else:
                    momentum_scores.append(0)
        
        return np.mean(momentum_scores) if momentum_scores else 50
    
    def calculate_risk_level(self, metrics, hist_data):
        """Calculate risk level"""
        risk_factors = 0
        
        # Beta risk
        beta = metrics.get('beta')
        if beta is not None:
            if beta > 1.5:
                risk_factors += 2
            elif beta > 1.2:
                risk_factors += 1
        
        # Debt risk
        debt_to_equity = metrics.get('debt_to_equity')
        if debt_to_equity is not None:
            if debt_to_equity > 2.0:
                risk_factors += 2
            elif debt_to_equity > 1.0:
                risk_factors += 1
        
        # Volatility risk
        if len(hist_data) >= 30:
            returns = hist_data['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            if volatility > 0.4:
                risk_factors += 2
            elif volatility > 0.25:
                risk_factors += 1
        
        if risk_factors >= 4:
            return "High Risk"
        elif risk_factors >= 2:
            return "Medium Risk"
        else:
            return "Low Risk"
    
    def generate_reasoning(self, overall_score, financial_score, valuation_score, 
                          technical_score, growth_score, momentum_score):
        """Generate reasoning for recommendation"""
        reasoning = []
        
        if overall_score >= 75:
            reasoning.append("This stock shows strong performance across multiple analysis dimensions.")
        elif overall_score >= 60:
            reasoning.append("This stock demonstrates solid fundamentals with positive indicators.")
        elif overall_score >= 40:
            reasoning.append("This stock shows mixed signals with both positive and negative factors.")
        else:
            reasoning.append("This stock shows concerning indicators across multiple analysis areas.")
        
        # Add specific insights
        if financial_score > 70:
            reasoning.append("The company demonstrates strong financial health with good profitability and manageable debt levels.")
        elif financial_score < 40:
            reasoning.append("The company shows some financial health concerns that warrant attention.")
        
        if valuation_score > 70:
            reasoning.append("The stock appears to be reasonably valued or potentially undervalued based on key metrics.")
        elif valuation_score < 40:
            reasoning.append("The stock may be overvalued based on current price multiples.")
        
        if technical_score > 70:
            reasoning.append("Technical indicators suggest positive price momentum and trading patterns.")
        elif technical_score < 40:
            reasoning.append("Technical indicators suggest weakening price momentum.")
        
        return " ".join(reasoning)
    
    def generate_key_factors(self, stock_info, metrics, financial_score, valuation_score, 
                           technical_score, growth_score, momentum_score):
        """Generate key factors for recommendation"""
        factors = []
        
        # Financial factors
        if financial_score > 70:
            factors.append("Strong financial health with good profitability")
        elif financial_score < 40:
            factors.append("Weak financial metrics requiring attention")
        
        # Valuation factors
        pe_ratio = metrics.get('pe_ratio')
        if pe_ratio and pe_ratio < 15:
            factors.append(f"Attractive P/E ratio of {pe_ratio:.1f}")
        elif pe_ratio and pe_ratio > 25:
            factors.append(f"High P/E ratio of {pe_ratio:.1f} suggests premium valuation")
        
        # Growth factors
        revenue_growth = metrics.get('revenue_growth')
        if revenue_growth and revenue_growth > 0.15:
            factors.append(f"Strong revenue growth of {revenue_growth*100:.1f}%")
        elif revenue_growth and revenue_growth < 0:
            factors.append(f"Declining revenue growth of {revenue_growth*100:.1f}%")
        
        # Dividend factors
        dividend_yield = metrics.get('dividend_yield')
        if dividend_yield and dividend_yield > 0.04:
            factors.append(f"Attractive dividend yield of {dividend_yield*100:.1f}%")
        
        # Risk factors
        beta = metrics.get('beta')
        if beta and beta > 1.5:
            factors.append(f"High volatility with beta of {beta:.1f}")
        elif beta and beta < 0.8:
            factors.append(f"Low volatility with beta of {beta:.1f}")
        
        # Debt factors
        debt_to_equity = metrics.get('debt_to_equity')
        if debt_to_equity and debt_to_equity > 2.0:
            factors.append("High debt levels may pose financial risk")
        elif debt_to_equity and debt_to_equity < 0.5:
            factors.append("Conservative debt management")
        
        return factors[:5]  # Limit to top 5 factors
