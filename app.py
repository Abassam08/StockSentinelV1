import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from datetime import datetime, timedelta
import requests
import json
from utils.stock_analyzer import StockAnalyzer
from utils.financial_metrics import FinancialMetrics
from utils.recommendation_engine import RecommendationEngine
from utils.currency_converter import CurrencyConverter
from utils.stock_suggestions import StockSuggestions

# Page configuration
st.set_page_config(
    page_title="North American Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = ""
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = StockSuggestions()

def validate_stock_symbol(symbol):
    """Validate and format stock symbol for North American markets"""
    if not symbol:
        return None, "Please enter a stock symbol"
    
    symbol = symbol.upper().strip()
    
    # Common North American exchanges and their suffixes
    exchanges = {
        'TSX': '.TO',
        'TSX-V': '.V',
        'NYSE': '',
        'NASDAQ': '',
        'AMEX': ''
    }
    
    # Check if symbol already has a suffix
    if '.' in symbol:
        base_symbol, suffix = symbol.split('.', 1)
        if suffix in ['TO', 'V']:
            return symbol, f"Canadian stock ({suffix})"
        else:
            return symbol, "Stock symbol"
    else:
        # Default to US market for symbols without suffix
        return symbol, "US stock"

def get_exchange_info(ticker_info):
    """Get exchange information from ticker data"""
    try:
        exchange = ticker_info.get('exchange', 'Unknown')
        market = ticker_info.get('market', 'Unknown')
        currency = ticker_info.get('currency', 'USD')
        
        exchange_mapping = {
            'TOR': 'TSX',
            'TSE': 'TSX',
            'VEN': 'TSX-V',
            'NYQ': 'NYSE',
            'NMS': 'NASDAQ',
            'ASE': 'AMEX'
        }
        
        display_exchange = exchange_mapping.get(exchange, exchange)
        return display_exchange, currency
    except:
        return 'Unknown', 'USD'

def create_price_chart(df, symbol, timeframe):
    """Create interactive price chart with volume"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(f'{symbol} Stock Price', 'Volume'),
        row_width=[0.2, 0.7]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price',
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff3366'
        ),
        row=1, col=1
    )
    
    # Volume chart
    colors = ['#00ff88' if close >= open else '#ff3366' 
              for close, open in zip(df['Close'], df['Open'])]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title=f'{symbol} - {timeframe} Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        height=600,
        showlegend=False,
        hovermode='x unified'
    )
    
    fig.update_xaxes(rangeslider_visible=False)
    
    return fig

def create_metrics_chart(metrics_data):
    """Create financial metrics visualization"""
    fig = go.Figure()
    
    # Create a radar chart for key metrics
    categories = ['P/E Ratio', 'Debt to Equity', 'ROE', 'Profit Margin', 'Revenue Growth']
    values = [
        min(metrics_data.get('pe_ratio', 0), 50),  # Cap P/E at 50 for visualization
        min(metrics_data.get('debt_to_equity', 0), 2),  # Cap at 2
        metrics_data.get('roe', 0) * 100,  # Convert to percentage
        metrics_data.get('profit_margin', 0) * 100,  # Convert to percentage
        metrics_data.get('revenue_growth', 0) * 100  # Convert to percentage
    ]
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Financial Metrics',
        line_color='#1f77b4'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title="Financial Health Overview",
        template='plotly_dark',
        height=400
    )
    
    return fig

def format_currency(value, currency='USD'):
    """Format currency values"""
    if pd.isna(value) or value is None:
        return 'N/A'
    
    if currency == 'CAD':
        return f'C${value:,.2f}'
    else:
        return f'${value:,.2f}'

def format_large_number(value):
    """Format large numbers with appropriate suffixes"""
    if pd.isna(value) or value is None:
        return 'N/A'
    
    if value >= 1e12:
        return f'{value/1e12:.2f}T'
    elif value >= 1e9:
        return f'{value/1e9:.2f}B'
    elif value >= 1e6:
        return f'{value/1e6:.2f}M'
    elif value >= 1e3:
        return f'{value/1e3:.2f}K'
    else:
        return f'{value:.2f}'

def main():
    st.title("📈 North American Stock Analysis Dashboard")
    st.markdown("### Analyze Canadian and US stocks with real-time data from Yahoo Finance")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Stock Analysis")
        
        # Stock symbol search with autocomplete
        st.markdown("**Search Stock Symbol**")
        search_query = st.text_input(
            "Type to search...",
            value="",
            placeholder="e.g., Shopify, Apple, Royal Bank...",
            help="Start typing a company name or stock symbol",
            key="search_input"
        )
        
        # Show suggestions based on search
        if search_query and len(search_query) >= 2:
            suggestions = st.session_state.suggestions.get_suggestions(search_query, max_results=8)
            
            if suggestions:
                st.markdown("**📍 Suggestions (Canadian stocks prioritized):**")
                
                # Create clickable buttons for suggestions
                cols = st.columns(1)
                for suggestion in suggestions:
                    with cols[0]:
                        # Format display with flag emoji for country
                        flag = "🇨🇦" if suggestion['exchange'] in ['TSX', 'TSX-V'] else "🇺🇸"
                        display_text = f"{flag} {suggestion['symbol']} - {suggestion['name'][:30]}..."
                        
                        if st.button(
                            display_text,
                            key=f"suggest_{suggestion['symbol']}",
                            help=f"Select {suggestion['symbol']} - {suggestion['name']} ({suggestion['exchange']})",
                            use_container_width=True
                        ):
                            st.session_state.selected_symbol = suggestion['symbol']
                            st.rerun()
        
        # Show popular stocks if no search
        elif not search_query:
            st.markdown("**🇨🇦 Popular Canadian Stocks:**")
            popular_canadian = st.session_state.suggestions.get_popular_canadian_stocks(5)
            
            for stock in popular_canadian:
                if st.button(
                    f"🇨🇦 {stock['symbol']} - {stock['name'][:25]}...",
                    key=f"pop_ca_{stock['symbol']}",
                    help=f"{stock['symbol']} - {stock['name']}",
                    use_container_width=True
                ):
                    st.session_state.selected_symbol = stock['symbol']
                    st.rerun()
            
            st.markdown("**🇺🇸 Popular US Stocks:**")
            popular_us = st.session_state.suggestions.get_popular_us_stocks(5)
            
            for stock in popular_us:
                if st.button(
                    f"🇺🇸 {stock['symbol']} - {stock['name'][:25]}...",
                    key=f"pop_us_{stock['symbol']}",
                    help=f"{stock['symbol']} - {stock['name']}",
                    use_container_width=True
                ):
                    st.session_state.selected_symbol = stock['symbol']
                    st.rerun()
        
        # Manual symbol input (fallback)
        st.markdown("---")
        symbol_input = st.text_input(
            "Or enter symbol manually:",
            value=st.session_state.selected_symbol,
            placeholder="e.g., AAPL, SHOP.TO, NVDA",
            help="Enter a stock symbol directly. Use .TO for TSX stocks, .V for TSX-V stocks"
        )
        
        # Timeframe selection
        timeframe = st.selectbox(
            "Select Timeframe",
            options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
            index=2,
            help="Choose the time period for historical data"
        )
        
        # Analysis button
        analyze_button = st.button("🔍 Analyze Stock", type="primary")
        
        # Help section
        with st.expander("📚 Beginner's Guide & Help"):
            st.markdown("""
            **How to Use This App:**
            1. Search for a company name or type a stock symbol
            2. Click on a suggestion or use the "Analyze Stock" button
            3. Review the financial data and buy/sell recommendation
            4. Download the data as CSV if needed
            
            **Stock Symbol Examples:**
            - 🇺🇸 US Stocks: AAPL (Apple), GOOGL (Google), MSFT (Microsoft)
            - 🇨🇦 Canadian TSX: SHOP.TO (Shopify), RY.TO (Royal Bank)
            - 🇨🇦 Canadian TSX-V: Add .V for venture stocks
            
            **Financial Terms Explained:**
            - **P/E Ratio**: How much you pay for each dollar of earnings (lower often better)
            - **Market Cap**: Total company value (Large: >$10B, Small: <$2B)
            - **Dividend Yield**: Yearly cash payments as % of stock price
            - **ROE**: How well the company uses your investment money
            - **Debt/Equity**: Company's debt compared to shareholder money (lower usually better)
            - **Beta**: Stock volatility vs market (>1 = more volatile, <1 = less volatile)
            
            **Investment Recommendation:**
            - 🟢 **BUY/STRONG BUY**: Good investment opportunity
            - 🟡 **HOLD**: Keep if you own it, maybe wait if you don't
            - 🔴 **SELL/STRONG SELL**: Consider selling or avoiding
            
            **Remember**: This is educational information only, not financial advice!
            """)
    
    # Main content area
    if analyze_button and symbol_input:
        st.session_state.selected_symbol = symbol_input
        
        # Validate symbol
        validated_symbol, symbol_info = validate_stock_symbol(symbol_input)
        
        if validated_symbol:
            with st.spinner(f"📊 Analyzing {validated_symbol}..."):
                try:
                    # Initialize analyzers
                    analyzer = StockAnalyzer()
                    metrics_calc = FinancialMetrics()
                    recommender = RecommendationEngine()
                    converter = CurrencyConverter()
                    
                    # Get stock data
                    ticker = yf.Ticker(validated_symbol)
                    stock_info = ticker.info
                    
                    # Get historical data
                    hist_data = ticker.history(period=timeframe)
                    
                    if hist_data.empty:
                        st.error(f"❌ No data found for symbol '{validated_symbol}'. Please check the symbol and try again.")
                        st.info("💡 **Suggestions:**\n- For Canadian stocks, add .TO (TSX) or .V (TSX-V)\n- For US stocks, use the symbol without suffix\n- Check spelling and ensure the company is publicly traded")
                        return
                    
                    # Get exchange and currency info
                    exchange, currency = get_exchange_info(stock_info)
                    
                    # Store data in session state
                    st.session_state.stock_data = {
                        'symbol': validated_symbol,
                        'info': stock_info,
                        'history': hist_data,
                        'exchange': exchange,
                        'currency': currency
                    }
                    
                    # Company header - mobile responsive
                    company_name = stock_info.get('longName', validated_symbol)
                    st.header(f"📊 {company_name}")
                    st.subheader(f"Symbol: {validated_symbol}")
                    
                    # Key metrics in responsive columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Exchange", f"{exchange} 🇨🇦" if exchange in ['TSX', 'TSX-V'] else f"{exchange} 🇺🇸")
                        st.metric("Currency", currency)
                    
                    with col2:
                        current_price = stock_info.get('currentPrice', hist_data['Close'].iloc[-1])
                        previous_close = stock_info.get('previousClose', hist_data['Close'].iloc[-2])
                        change = current_price - previous_close
                        change_percent = (change / previous_close) * 100
                        
                        st.metric(
                            "Current Price",
                            format_currency(current_price, currency),
                            f"{change:+.2f} ({change_percent:+.2f}%)"
                        )
                    
                    # Financial metrics - mobile responsive layout
                    st.subheader("📊 Key Financial Metrics")
                    
                    metrics_data = metrics_calc.calculate_metrics(stock_info, hist_data)
                    
                    # Create tabs for better mobile experience
                    tab1, tab2, tab3 = st.tabs(["💰 Valuation", "📈 Performance", "⚖️ Financial Health"])
                    
                    with tab1:
                        st.markdown("**Company Size & Value**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            market_cap = stock_info.get('marketCap')
                            if market_cap and market_cap > 10e9:
                                cap_desc = "Large Company"
                            elif market_cap and market_cap > 2e9:
                                cap_desc = "Medium Company"
                            else:
                                cap_desc = "Small Company"
                            st.metric("Market Cap", format_large_number(market_cap), help=f"{cap_desc} - Total value of all shares")
                            
                            dividend_yield = stock_info.get('dividendYield')
                            dividend_display = f"{dividend_yield*100:.2f}%" if dividend_yield else "N/A"
                            dividend_help = "Higher = more income, but may mean slower growth"
                            st.metric("Dividend Yield", dividend_display, help=dividend_help)
                        
                        with col2:
                            pe_ratio = stock_info.get('trailingPE')
                            pe_display = f"{pe_ratio:.2f}" if pe_ratio else "N/A"
                            pe_help = "Lower often means better value (under 20 is generally good)"
                            st.metric("P/E Ratio", pe_display, help=pe_help)
                            
                            beta = stock_info.get('beta')
                            beta_display = f"{beta:.2f}" if beta else "N/A"
                            if beta and beta > 1.2:
                                beta_desc = "High Risk"
                            elif beta and beta < 0.8:
                                beta_desc = "Low Risk"
                            else:
                                beta_desc = "Medium Risk"
                            st.metric("Beta (Risk)", beta_display, help=f"{beta_desc} - Compares stock movement to market")
                    
                    with tab2:
                        st.markdown("**Company Performance**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            roe = stock_info.get('returnOnEquity')
                            roe_display = f"{roe*100:.2f}%" if roe else "N/A"
                            roe_help = "Higher is better - shows how well company uses your money"
                            st.metric("ROE (Return on Equity)", roe_display, help=roe_help)
                            
                            profit_margin = stock_info.get('profitMargins')
                            profit_display = f"{profit_margin*100:.2f}%" if profit_margin else "N/A"
                            profit_help = "Higher means company keeps more money from sales"
                            st.metric("Profit Margin", profit_display, help=profit_help)
                        
                        with col2:
                            revenue_growth = stock_info.get('revenueGrowth')
                            growth_display = f"{revenue_growth*100:.2f}%" if revenue_growth else "N/A"
                            growth_help = "Positive growth means company is getting bigger"
                            st.metric("Revenue Growth", growth_display, help=growth_help)
                            
                            # Add 52-week performance
                            current_price = stock_info.get('currentPrice', hist_data['Close'].iloc[-1])
                            week_52_high = stock_info.get('fiftyTwoWeekHigh')
                            if week_52_high and current_price:
                                performance_52w = ((current_price / week_52_high) - 1) * 100
                                st.metric("vs 52-Week High", f"{performance_52w:+.1f}%", help="How close to 1-year high price")
                    
                    with tab3:
                        st.markdown("**Financial Stability**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            debt_equity = stock_info.get('debtToEquity')
                            debt_display = f"{debt_equity:.2f}" if debt_equity else "N/A"
                            if debt_equity and debt_equity < 0.5:
                                debt_desc = "Low Debt"
                            elif debt_equity and debt_equity < 1.0:
                                debt_desc = "Moderate Debt"
                            else:
                                debt_desc = "High Debt"
                            st.metric("Debt/Equity Ratio", debt_display, help=f"{debt_desc} - Lower is usually safer")
                            
                            current_ratio = stock_info.get('currentRatio')
                            current_display = f"{current_ratio:.2f}" if current_ratio else "N/A"
                            current_help = "Above 1.5 is good - can pay short-term bills"
                            st.metric("Current Ratio", current_display, help=current_help)
                        
                        with col2:
                            # Financial health score
                            health_score = metrics_calc.get_financial_health_score(metrics_data)
                            if health_score >= 70:
                                health_color = "🟢 Healthy"
                            elif health_score >= 50:
                                health_color = "🟡 Average"
                            else:
                                health_color = "🔴 Concerning"
                            st.metric("Financial Health Score", f"{health_score:.0f}/100", help=f"{health_color} - Overall financial strength")
                            
                            # Book value
                            book_value = stock_info.get('bookValue')
                            book_display = format_currency(book_value, currency) if book_value else "N/A"
                            st.metric("Book Value per Share", book_display, help="Company's worth if sold today")
                    
                    # Buy/Sell Recommendation - Enhanced for beginners
                    st.subheader("🎯 Investment Recommendation")
                    
                    recommendation = recommender.get_recommendation(stock_info, hist_data, metrics_data)
                    
                    # Main recommendation display
                    rec_color = "🟢" if recommendation['action'] in ['BUY', 'STRONG BUY'] else "🔴" if recommendation['action'] in ['SELL', 'STRONG SELL'] else "🟡"
                    
                    # Create a prominent recommendation box
                    if recommendation['action'] in ['BUY', 'STRONG BUY']:
                        st.success(f"🟢 **{recommendation['action']}** - This looks like a good investment opportunity")
                    elif recommendation['action'] in ['SELL', 'STRONG SELL']:
                        st.error(f"🔴 **{recommendation['action']}** - Consider avoiding or selling this stock")
                    else:
                        st.warning(f"🟡 **{recommendation['action']}** - This stock shows mixed signals")
                    
                    # Detailed analysis in columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📊 Analysis Summary:**")
                        st.markdown(f"**Confidence Level:** {recommendation['confidence']:.0f}%")
                        st.markdown(f"**Risk Assessment:** {recommendation['risk_level']}")
                        
                        # Simplified scoring
                        overall_score = recommendation['overall_score']
                        if overall_score >= 75:
                            score_desc = "Excellent (75+)"
                            score_color = "🟢"
                        elif overall_score >= 60:
                            score_desc = "Good (60-74)"
                            score_color = "🟢"
                        elif overall_score >= 40:
                            score_desc = "Mixed (40-59)"
                            score_color = "🟡"
                        else:
                            score_desc = "Poor (0-39)"
                            score_color = "🔴"
                        
                        st.markdown(f"**Overall Score:** {score_color} {overall_score:.0f}/100 ({score_desc})")
                    
                    with col2:
                        st.markdown("**🔍 Why This Recommendation?**")
                        st.write(recommendation['reasoning'])
                        
                        if recommendation['factors']:
                            st.markdown("**💡 Key Points:**")
                            for factor in recommendation['factors'][:3]:  # Limit to top 3 for mobile
                                st.write(f"• {factor}")
                    
                    # Detailed breakdown in expandable section
                    with st.expander("🔬 Detailed Analysis Breakdown"):
                        scores = recommendation['scores']
                        st.markdown("**Individual Score Components:**")
                        
                        score_cols = st.columns(3)
                        with score_cols[0]:
                            st.metric("Financial Health", f"{scores['financial_health']:.0f}/100")
                            st.metric("Valuation", f"{scores['valuation']:.0f}/100")
                        with score_cols[1]:
                            st.metric("Technical Analysis", f"{scores['technical']:.0f}/100")
                            st.metric("Growth Potential", f"{scores['growth']:.0f}/100")
                        with score_cols[2]:
                            st.metric("Price Momentum", f"{scores['momentum']:.0f}/100")
                            
                            # Risk indicator
                            if recommendation['risk_level'] == "Low Risk":
                                st.success("🟢 Low Risk Investment")
                            elif recommendation['risk_level'] == "Medium Risk":
                                st.warning("🟡 Medium Risk Investment")
                            else:
                                st.error("🔴 High Risk Investment")
                    
                    # Beginner-friendly action suggestions
                    st.markdown("---")
                    st.markdown("**🎯 What Should You Do?**")
                    
                    if recommendation['action'] in ['BUY', 'STRONG BUY']:
                        st.info("""
                        ✅ **For New Investors:**
                        - Start with a small amount you can afford to lose
                        - Consider dollar-cost averaging (buying small amounts regularly)
                        - Do your own research beyond this analysis
                        - Only invest money you won't need for at least 3-5 years
                        """)
                    elif recommendation['action'] == 'HOLD':
                        st.info("""
                        ⏳ **Current Owners:** Keep your shares for now
                        🤔 **New Investors:** Wait for better opportunities or consider other stocks
                        📚 **Learn More:** Research why this stock has mixed signals
                        """)
                    else:
                        st.info("""
                        ⚠️ **Current Owners:** Consider reducing your position
                        🚫 **New Investors:** Look for better investment opportunities
                        📖 **Research:** Understand the risks before making any decisions
                        """)
                    
                    # Investment disclaimer
                    st.error("⚠️ **Important Disclaimer:** This analysis is for educational purposes only and should NOT be considered as financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions. Past performance does not guarantee future results.")
                    
                    # Price chart
                    st.subheader("📈 Price Chart & Volume")
                    
                    chart = create_price_chart(hist_data, validated_symbol, timeframe)
                    st.plotly_chart(chart, use_container_width=True)
                    
                    # Financial metrics visualization
                    if any(metrics_data.values()):
                        st.subheader("🎯 Financial Health Overview")
                        metrics_chart = create_metrics_chart(metrics_data)
                        st.plotly_chart(metrics_chart, use_container_width=True)
                    
                    # Data table
                    st.subheader("📋 Historical Data")
                    
                    # Format historical data for display
                    display_data = hist_data.copy()
                    display_data = display_data.reset_index()
                    display_data['Date'] = pd.to_datetime(display_data['Date']).dt.strftime('%Y-%m-%d')
                    display_data = display_data.set_index('Date')
                    
                    # Round numerical columns
                    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
                        display_data[col] = display_data[col].round(2)
                    
                    display_data['Volume'] = display_data['Volume'].astype(int)
                    
                    st.dataframe(display_data, use_container_width=True)
                    
                    # CSV download
                    csv_buffer = io.StringIO()
                    display_data.to_csv(csv_buffer)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📥 Download Data as CSV",
                        data=csv_data,
                        file_name=f"{validated_symbol}_{timeframe}_data.csv",
                        mime="text/csv",
                        help="Download the historical data as a CSV file"
                    )
                    
                    # Additional company information
                    if stock_info.get('longBusinessSummary'):
                        st.subheader("🏢 Company Overview")
                        st.write(stock_info['longBusinessSummary'])
                    
                    # Currency conversion for Canadian stocks
                    if currency == 'CAD':
                        st.subheader("💱 Currency Information")
                        
                        try:
                            usd_cad_rate = converter.get_exchange_rate('USD', 'CAD')
                            cad_usd_rate = converter.get_exchange_rate('CAD', 'USD')
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("USD to CAD", f"{usd_cad_rate:.4f}")
                                current_price_usd = current_price * cad_usd_rate
                                st.metric("Current Price (USD)", format_currency(current_price_usd, 'USD'))
                            
                            with col2:
                                st.metric("CAD to USD", f"{cad_usd_rate:.4f}")
                                st.info("💡 Currency rates are approximate and may not reflect real-time values")
                        except:
                            st.info("Currency conversion data temporarily unavailable")
                    
                except Exception as e:
                    st.error(f"❌ Error analyzing stock: {str(e)}")
                    st.info("💡 **Troubleshooting:**\n- Check your internet connection\n- Verify the stock symbol is correct\n- Try a different timeframe\n- Some stocks may have limited data availability")
    
    elif not symbol_input and analyze_button:
        st.warning("Please enter a stock symbol to analyze")
    
    # Footer
    st.markdown("---")
    st.markdown("**Data Source:** Yahoo Finance | **Last Updated:** Real-time")
    st.markdown("*This tool is designed for educational purposes and beginners learning about stock analysis*")

if __name__ == "__main__":
    main()
