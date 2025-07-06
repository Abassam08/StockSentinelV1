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
        
        # Stock symbol input
        symbol_input = st.text_input(
            "Enter Stock Symbol",
            value=st.session_state.selected_symbol,
            placeholder="e.g., AAPL, SHOP.TO, NVDA",
            help="Enter a stock symbol. Use .TO for TSX stocks, .V for TSX-V stocks"
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
        with st.expander("📚 Help & Examples"):
            st.markdown("""
            **Stock Symbol Examples:**
            - US Stocks: AAPL, GOOGL, MSFT, TSLA
            - Canadian (TSX): SHOP.TO, RY.TO, CNR.TO
            - Canadian (TSX-V): Example.V
            
            **Financial Terms:**
            - **P/E Ratio**: Price-to-Earnings ratio
            - **Market Cap**: Total market value
            - **Dividend Yield**: Annual dividend as % of price
            - **ROE**: Return on Equity
            - **Debt/Equity**: Company's debt relative to equity
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
                    
                    # Company header
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        company_name = stock_info.get('longName', validated_symbol)
                        st.header(f"{company_name}")
                        st.subheader(f"({validated_symbol})")
                    
                    with col2:
                        st.metric("Exchange", exchange)
                        st.metric("Currency", currency)
                    
                    with col3:
                        current_price = stock_info.get('currentPrice', hist_data['Close'].iloc[-1])
                        previous_close = stock_info.get('previousClose', hist_data['Close'].iloc[-2])
                        change = current_price - previous_close
                        change_percent = (change / previous_close) * 100
                        
                        st.metric(
                            "Current Price",
                            format_currency(current_price, currency),
                            f"{change:+.2f} ({change_percent:+.2f}%)"
                        )
                    
                    # Financial metrics
                    st.subheader("📊 Key Financial Metrics")
                    
                    metrics_data = metrics_calc.calculate_metrics(stock_info, hist_data)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        market_cap = stock_info.get('marketCap')
                        st.metric("Market Cap", format_large_number(market_cap))
                        
                        pe_ratio = stock_info.get('trailingPE')
                        st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
                    
                    with col2:
                        dividend_yield = stock_info.get('dividendYield')
                        dividend_display = f"{dividend_yield*100:.2f}%" if dividend_yield else "N/A"
                        st.metric("Dividend Yield", dividend_display)
                        
                        beta = stock_info.get('beta')
                        st.metric("Beta", f"{beta:.2f}" if beta else "N/A")
                    
                    with col3:
                        roe = stock_info.get('returnOnEquity')
                        roe_display = f"{roe*100:.2f}%" if roe else "N/A"
                        st.metric("ROE", roe_display)
                        
                        debt_equity = stock_info.get('debtToEquity')
                        st.metric("Debt/Equity", f"{debt_equity:.2f}" if debt_equity else "N/A")
                    
                    with col4:
                        profit_margin = stock_info.get('profitMargins')
                        profit_display = f"{profit_margin*100:.2f}%" if profit_margin else "N/A"
                        st.metric("Profit Margin", profit_display)
                        
                        revenue_growth = stock_info.get('revenueGrowth')
                        growth_display = f"{revenue_growth*100:.2f}%" if revenue_growth else "N/A"
                        st.metric("Revenue Growth", growth_display)
                    
                    # Buy/Sell Recommendation
                    st.subheader("🎯 Investment Recommendation")
                    
                    recommendation = recommender.get_recommendation(stock_info, hist_data, metrics_data)
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        rec_color = "🟢" if recommendation['action'] == 'BUY' else "🔴" if recommendation['action'] == 'SELL' else "🟡"
                        st.markdown(f"### {rec_color} {recommendation['action']}")
                        st.markdown(f"**Confidence:** {recommendation['confidence']:.1f}%")
                        st.markdown(f"**Risk Level:** {recommendation['risk_level']}")
                    
                    with col2:
                        st.markdown("**Analysis:**")
                        st.write(recommendation['reasoning'])
                        
                        st.markdown("**Key Factors:**")
                        for factor in recommendation['factors']:
                            st.write(f"• {factor}")
                    
                    # Investment disclaimer
                    st.warning("⚠️ **Investment Disclaimer:** This analysis is for educational purposes only and should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions.")
                    
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
                    display_data.index = display_data.index.strftime('%Y-%m-%d')
                    
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
