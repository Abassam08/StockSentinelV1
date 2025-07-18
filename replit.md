# North American Stock Analysis Dashboard

## Overview

This is a comprehensive stock analysis dashboard built with Streamlit that provides detailed financial analysis and recommendations for North American stocks (NYSE, NASDAQ, TSX, TSX-V, AMEX). The application fetches real-time stock data using the yfinance library and provides technical analysis, financial metrics, and investment recommendations.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Visualization**: Plotly for interactive charts and graphs
- **Layout**: Wide layout with expandable sidebar for navigation
- **State Management**: Streamlit session state for maintaining user data across interactions

### Backend Architecture
- **Data Source**: Yahoo Finance API via yfinance library
- **Analysis Engine**: Custom utility classes for different analysis types
- **Modular Design**: Separate utility modules for specific functionality
- **Real-time Processing**: Live data fetching and analysis

### Data Processing Pipeline
1. Stock symbol validation and formatting
2. Historical data retrieval
3. Technical indicator calculations
4. Financial metrics computation
5. Recommendation generation
6. Currency conversion (CAD/USD)

## Key Components

### Core Application (`app.py`)
- Main Streamlit application entry point
- User interface and interaction handling
- Session state management
- Stock symbol validation for North American exchanges

### Stock Analysis Engine (`utils/stock_analyzer.py`)
- Technical indicator calculations (Moving Averages, RSI, Bollinger Bands, MACD)
- Price pattern analysis
- Historical data processing
- Chart data preparation

### Financial Metrics Calculator (`utils/financial_metrics.py`)
- Valuation metrics (P/E, P/B, P/S ratios)
- Profitability analysis (profit margins, ROE, ROA)
- Financial health indicators (debt ratios, liquidity ratios)
- Growth metrics calculation

### Recommendation Engine (`utils/recommendation_engine.py`)
- Multi-factor scoring system with weighted components:
  - Financial Health (25%)
  - Valuation (25%)
  - Technical Analysis (25%)
  - Growth Metrics (15%)
  - Momentum (10%)
- Buy/Sell/Hold recommendations with confidence levels
- Risk assessment integration

### Currency Converter (`utils/currency_converter.py`)
- Real-time CAD/USD exchange rate fetching
- API integration with caching mechanism
- Fallback rates for offline scenarios
- 1-hour cache duration for performance

## Data Flow

1. **User Input**: Stock symbol entry and validation
2. **Data Retrieval**: Yahoo Finance API call for historical and current data
3. **Analysis Pipeline**:
   - Technical indicators calculation
   - Financial metrics computation
   - Currency conversion (if needed)
   - Recommendation scoring
4. **Visualization**: Interactive charts and metrics display
5. **Output**: Comprehensive analysis dashboard with recommendations

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **yfinance**: Yahoo Finance API wrapper
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **plotly**: Interactive visualization

### API Integrations
- **Yahoo Finance**: Stock data, financial information, historical prices
- **Exchange Rate API**: Currency conversion rates (exchangerate-api.com)

### Market Data Sources
- NYSE, NASDAQ, AMEX (US markets)
- TSX, TSX-V (Canadian markets)

## Deployment Strategy

### Development Environment
- Python-based application suitable for local development
- Streamlit's built-in development server
- Modular architecture for easy testing and debugging

### Production Considerations
- Streamlit Cloud or container-based deployment
- Environment variable management for API keys
- Caching strategies for performance optimization
- Rate limiting for external API calls

### Scalability
- Stateless design for horizontal scaling
- API caching to reduce external calls
- Modular components for independent scaling

## Changelog

- July 06, 2025. Initial setup
- July 06, 2025. Added autocomplete stock search functionality with Canadian stock preference
- July 06, 2025. Enhanced mobile responsiveness with tabbed layout for financial metrics
- July 06, 2025. Added beginner-friendly explanations and improved recommendation system
- July 06, 2025. Implemented stock suggestions engine with 500+ North American stocks
- July 06, 2025. Added financial news integration with multiple RSS feeds and fallback sources

## Recent Updates

### Stock Search & Autocomplete (July 06, 2025)
- Added intelligent stock symbol search with autocomplete suggestions
- Prioritizes Canadian stocks (TSX, TSX-V) in search results
- Includes 500+ pre-loaded stock symbols with company names
- Interactive buttons for popular Canadian and US stocks
- Real-time search filtering as user types

### Mobile-Friendly Enhancements (July 06, 2025)
- Reorganized financial metrics into tabs (Valuation, Performance, Financial Health)
- Responsive column layouts for better mobile viewing
- Added contextual help text for all financial terms
- Simplified recommendation display with clear action guidance
- Enhanced error handling and user feedback

### Beginner-Friendly Features (July 06, 2025)
- Added comprehensive help section with investment guidance
- Simplified financial explanations with practical advice
- Color-coded risk indicators and recommendation clarity
- Step-by-step guidance for new investors
- Enhanced disclaimer and educational warnings

### Financial News Integration (July 06, 2025)
- Integrated RSS feeds from Yahoo Finance, Google News, and Reuters
- Stock-specific news fetching with company name matching
- Fallback to general market news when stock-specific news unavailable
- Mobile-friendly expandable news cards with article summaries
- Direct links to full articles for detailed reading
- Graceful error handling for news service unavailability

## User Preferences

Preferred communication style: Simple, everyday language.
Stock focus: Canadian stocks prioritized over US stocks.
Target audience: Beginner and amateur investors.
Mobile compatibility: Essential for user accessibility.