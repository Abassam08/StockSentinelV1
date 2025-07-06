import requests
import json
from datetime import datetime, timedelta

class CurrencyConverter:
    """Handle currency conversion between CAD and USD"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        self.last_update = None
    
    def get_exchange_rate(self, from_currency, to_currency):
        """Get exchange rate between two currencies"""
        if from_currency == to_currency:
            return 1.0
        
        # Check cache first
        cache_key = f"{from_currency}_{to_currency}"
        current_time = datetime.now()
        
        if (cache_key in self.cache and 
            self.last_update and 
            current_time - self.last_update < self.cache_duration):
            return self.cache[cache_key]
        
        try:
            # Try to get rate from a free API
            rate = self._fetch_exchange_rate(from_currency, to_currency)
            
            # Update cache
            self.cache[cache_key] = rate
            self.last_update = current_time
            
            return rate
        except:
            # Fallback to approximate rates if API fails
            return self._get_fallback_rate(from_currency, to_currency)
    
    def _fetch_exchange_rate(self, from_currency, to_currency):
        """Fetch exchange rate from external API"""
        # Using exchangerate-api.com (free tier)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if to_currency in data['rates']:
                return data['rates'][to_currency]
            else:
                raise ValueError(f"Currency {to_currency} not found in rates")
        except:
            # Try alternative API
            return self._fetch_alternative_rate(from_currency, to_currency)
    
    def _fetch_alternative_rate(self, from_currency, to_currency):
        """Fetch from alternative API"""
        # Using fixer.io alternative endpoint
        url = f"https://api.fixer.io/latest?base={from_currency}&symbols={to_currency}"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'rates' in data and to_currency in data['rates']:
                return data['rates'][to_currency]
            else:
                raise ValueError("Rate not found")
        except:
            raise ValueError("Could not fetch exchange rate")
    
    def _get_fallback_rate(self, from_currency, to_currency):
        """Get fallback approximate rates when APIs fail"""
        # Approximate rates as of recent data (these should be updated periodically)
        fallback_rates = {
            'USD_CAD': 1.35,
            'CAD_USD': 0.74,
            'USD_USD': 1.0,
            'CAD_CAD': 1.0
        }
        
        rate_key = f"{from_currency}_{to_currency}"
        return fallback_rates.get(rate_key, 1.0)
    
    def convert_amount(self, amount, from_currency, to_currency):
        """Convert amount from one currency to another"""
        if amount is None or amount == 0:
            return 0
        
        rate = self.get_exchange_rate(from_currency, to_currency)
        return amount * rate
    
    def format_currency_pair(self, from_currency, to_currency):
        """Format currency pair for display"""
        if from_currency == 'CAD' and to_currency == 'USD':
            return "CAD/USD"
        elif from_currency == 'USD' and to_currency == 'CAD':
            return "USD/CAD"
        else:
            return f"{from_currency}/{to_currency}"
    
    def get_currency_symbol(self, currency):
        """Get currency symbol for display"""
        symbols = {
            'USD': '$',
            'CAD': 'C$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥'
        }
        return symbols.get(currency, currency)
    
    def is_cache_valid(self):
        """Check if cache is still valid"""
        if not self.last_update:
            return False
        
        return datetime.now() - self.last_update < self.cache_duration
    
    def clear_cache(self):
        """Clear the exchange rate cache"""
        self.cache.clear()
        self.last_update = None
    
    def get_currency_info(self, currency):
        """Get additional information about currency"""
        currency_info = {
            'USD': {
                'name': 'US Dollar',
                'country': 'United States',
                'symbol': '$',
                'flag': '🇺🇸'
            },
            'CAD': {
                'name': 'Canadian Dollar',
                'country': 'Canada',
                'symbol': 'C$',
                'flag': '🇨🇦'
            },
            'EUR': {
                'name': 'Euro',
                'country': 'European Union',
                'symbol': '€',
                'flag': '🇪🇺'
            },
            'GBP': {
                'name': 'British Pound',
                'country': 'United Kingdom',
                'symbol': '£',
                'flag': '🇬🇧'
            }
        }
        
        return currency_info.get(currency, {
            'name': currency,
            'country': 'Unknown',
            'symbol': currency,
            'flag': '🏳️'
        })
