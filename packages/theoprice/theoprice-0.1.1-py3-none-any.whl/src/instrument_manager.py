#!/usr/bin/env python3

"""
Dynamic Instrument Manager for F&O enabled stocks
Fetches and caches instruments data from Upstox API
"""

import json
import gzip
import requests
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import hashlib

class InstrumentManager:
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize instrument manager with caching."""
        # Use user's home directory for cache by default
        if cache_dir is None:
            self.cache_dir = Path.home() / ".upstox_cache"
        else:
            self.cache_dir = Path(cache_dir)
        
        # Try to create cache directory with fallback options
        self._setup_cache_directory()
        
        self.cache_file = self.cache_dir / "instruments_cache.json"
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        
        # Upstox instruments JSON URL (gzipped)
        self.instruments_url = "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"
        
        # Cached data
        self._fo_stocks = {}
        self._cache_timestamp = None
        self._cache_enabled = True  # Flag to disable caching if permissions fail
    
    def _setup_cache_directory(self) -> None:
        """Setup cache directory with fallback options."""
        try:
            # Try to create the cache directory
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            # Fallback to temp directory
            try:
                temp_dir = Path(tempfile.gettempdir()) / "upstox_cache"
                temp_dir.mkdir(parents=True, exist_ok=True)
                self.cache_dir = temp_dir
                print(f"Using temporary directory for cache: {self.cache_dir}")
            except Exception:
                # If even temp dir fails, disable caching
                self.cache_dir = Path("/tmp") / "upstox_cache_fallback"
                print("Warning: Cache directory creation failed. Running without cache.")
        
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self.cache_file.exists():
            return False
            
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                cache_time = datetime.fromisoformat(data.get('timestamp', ''))
                return datetime.now() - cache_time < self.cache_duration
        except (json.JSONDecodeError, ValueError, KeyError):
            return False
    
    def _save_cache(self, fo_stocks: Dict[str, str]) -> None:
        """Save F&O stocks data to cache."""
        if not self._cache_enabled:
            return
            
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'fo_stocks': fo_stocks
        }
        
        try:
            # Ensure cache directory exists
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except (PermissionError, OSError) as e:
            # Silently fail if we can't write cache
            self._cache_enabled = False
            print(f"Warning: Unable to save cache. Running without cache. Error: {e}")
        except Exception as e:
            # Log but don't fail for other cache write errors
            print(f"Warning: Cache save failed: {e}")
    
    def _load_cache(self) -> Dict[str, str]:
        """Load F&O stocks data from cache."""
        if not self._cache_enabled:
            return {}
            
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                return data.get('fo_stocks', {})
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            return {}
    
    def _download_instruments(self) -> List[Dict]:
        """Download and decompress instruments JSON from Upstox."""
        try:
            response = requests.get(self.instruments_url, timeout=30)
            response.raise_for_status()
            
            # Decompress gzipped content
            decompressed_data = gzip.decompress(response.content)
            instruments = json.loads(decompressed_data.decode('utf-8'))
            
            return instruments
        except requests.RequestException as e:
            raise Exception(f"Failed to download instruments: {e}")
        except (gzip.BadGzipFile, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse instruments data: {e}")
    
    def _extract_fo_stocks(self, instruments: List[Dict]) -> Dict[str, str]:
        """Extract F&O enabled stocks from instruments data."""
        fo_stocks = {}
        
        for instrument in instruments:
            # Filter for NSE F&O stocks only
            if (instrument.get('segment') == 'NSE_FO' and 
                instrument.get('instrument_type') in ['FUT', 'CE', 'PE']):
                
                underlying_symbol = instrument.get('underlying_symbol')
                underlying_key = instrument.get('underlying_key')
                
                if underlying_symbol and underlying_key:
                    # Store the mapping from symbol to underlying_key
                    # This gives us the equity instrument key for options
                    fo_stocks[underlying_symbol.upper()] = underlying_key
        
        # Remove duplicates and ensure we have unique symbols
        unique_fo_stocks = {}
        for symbol, key in fo_stocks.items():
            if symbol not in unique_fo_stocks:
                unique_fo_stocks[symbol] = key
        
        return unique_fo_stocks
    
    def _refresh_instruments(self) -> None:
        """Refresh instruments data from Upstox API."""
        print("Fetching latest F&O instruments from Upstox...")
        
        try:
            instruments = self._download_instruments()
            fo_stocks = self._extract_fo_stocks(instruments)
            
            if fo_stocks:
                self._fo_stocks = fo_stocks
                self._cache_timestamp = datetime.now()
                self._save_cache(fo_stocks)
                print(f"Successfully loaded {len(fo_stocks)} F&O enabled stocks")
            else:
                raise Exception("No F&O stocks found in instruments data")
                
        except Exception as e:
            print(f"Error refreshing instruments: {e}")
            # Try to use cached data as fallback
            if self._cache_enabled and self.cache_file.exists():
                print("Falling back to cached data...")
                cached_data = self._load_cache()
                if cached_data:
                    self._fo_stocks = cached_data
                    return
            
            # If no cache available, still try to work without persisting
            print("Warning: Running without cache. Will fetch fresh data each time.")
            try:
                # Try one more time to fetch without saving
                instruments = self._download_instruments()
                fo_stocks = self._extract_fo_stocks(instruments)
                if fo_stocks:
                    self._fo_stocks = fo_stocks
                    print(f"Successfully loaded {len(fo_stocks)} F&O enabled stocks (no cache)")
                else:
                    raise Exception("No F&O stocks found in instruments data")
            except Exception as fetch_error:
                raise Exception(f"Failed to fetch instruments and no cache available: {fetch_error}")
    
    def get_fo_stocks(self) -> Dict[str, str]:
        """Get F&O enabled stocks mapping."""
        # Check if we need to refresh the cache
        if not self._fo_stocks or not self._is_cache_valid():
            self._refresh_instruments()
        
        return self._fo_stocks
    
    def get_instrument_key(self, symbol: str) -> Optional[str]:
        """Get instrument key for a given stock symbol."""
        fo_stocks = self.get_fo_stocks()
        symbol_upper = symbol.upper().strip()
        
        # Direct lookup
        if symbol_upper in fo_stocks:
            return fo_stocks[symbol_upper]
        
        # Try fuzzy matching for common variations
        variations = [
            symbol_upper.replace('&', ''),
            symbol_upper.replace('-', ''),
            symbol_upper.replace('_', ''),
            symbol_upper.replace(' ', ''),
        ]
        
        for variation in variations:
            if variation in fo_stocks:
                return fo_stocks[variation]
        
        # Try partial matching (for cases like BAJAJ-AUTO vs BAJAJAUTO)
        for stock_symbol in fo_stocks.keys():
            if (symbol_upper in stock_symbol or 
                stock_symbol in symbol_upper or
                symbol_upper.replace('-', '') == stock_symbol.replace('-', '')):
                return fo_stocks[stock_symbol]
        
        return None
    
    def is_fo_enabled(self, symbol: str) -> bool:
        """Check if a symbol is F&O enabled."""
        return self.get_instrument_key(symbol) is not None
    
    def search_symbols(self, query: str) -> List[str]:
        """Search for symbols containing the query string."""
        fo_stocks = self.get_fo_stocks()
        query_upper = query.upper().strip()
        
        matches = []
        for symbol in fo_stocks.keys():
            if query_upper in symbol:
                matches.append(symbol)
        
        return sorted(matches)
    
    def get_cache_info(self) -> Dict:
        """Get cache information."""
        if not self._cache_enabled:
            return {'cached': False, 'valid': False, 'cache_enabled': False, 'cache_dir': str(self.cache_dir)}
            
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    timestamp = data.get('timestamp', '')
                    count = len(data.get('fo_stocks', {}))
                    return {
                        'cached': True,
                        'timestamp': timestamp,
                        'count': count,
                        'valid': self._is_cache_valid(),
                        'cache_enabled': self._cache_enabled,
                        'cache_dir': str(self.cache_dir)
                    }
            except:
                pass
        
        return {'cached': False, 'valid': False, 'cache_enabled': self._cache_enabled, 'cache_dir': str(self.cache_dir)}