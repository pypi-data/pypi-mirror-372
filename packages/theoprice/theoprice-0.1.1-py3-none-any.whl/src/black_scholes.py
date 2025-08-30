#!/usr/bin/env python3

import math
from scipy.stats import norm
from datetime import datetime, date
from typing import Dict, Optional, Tuple

class BlackScholesCalculator:
    def __init__(self, risk_free_rate: float = 0.066):
        """Initialize Black-Scholes calculator.
        
        Args:
            risk_free_rate: Annual risk-free interest rate (default: 6.60% for India)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_time_to_expiry(self, expiry_date: str) -> float:
        """Calculate time to expiry in years.
        
        Args:
            expiry_date: Expiry date in YYYY-MM-DD format
        
        Returns:
            Time to expiry in years
        """
        try:
            if isinstance(expiry_date, str):
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
            else:
                expiry = expiry_date.date() if hasattr(expiry_date, 'date') else expiry_date
            
            today = date.today()
            days_to_expiry = (expiry - today).days
            
            # Convert to years (using 365 days)
            return max(days_to_expiry / 365.0, 0.0001)  # Minimum 0.0001 to avoid division by zero
        except Exception:
            return 0.0001  # Default to very small time if error
    
    def calculate_d1_d2(self, spot: float, strike: float, time: float, volatility: float) -> Tuple[float, float]:
        """Calculate d1 and d2 parameters for Black-Scholes formula.
        
        Args:
            spot: Current spot price
            strike: Strike price
            time: Time to expiry in years
            volatility: Implied volatility (as decimal, e.g., 0.20 for 20%)
        
        Returns:
            Tuple of (d1, d2)
        """
        if time <= 0 or volatility <= 0:
            return 0, 0
        
        try:
            d1 = (math.log(spot / strike) + (self.risk_free_rate + 0.5 * volatility ** 2) * time) / (volatility * math.sqrt(time))
            d2 = d1 - volatility * math.sqrt(time)
            return d1, d2
        except (ValueError, ZeroDivisionError):
            return 0, 0
    
    def calculate_call_price(self, spot: float, strike: float, time: float, volatility: float) -> float:
        """Calculate theoretical call option price using Black-Scholes formula.
        
        Args:
            spot: Current spot price
            strike: Strike price
            time: Time to expiry in years
            volatility: Implied volatility (as decimal)
        
        Returns:
            Theoretical call option price
        """
        if spot <= 0 or strike <= 0 or time <= 0 or volatility <= 0:
            return 0
        
        d1, d2 = self.calculate_d1_d2(spot, strike, time, volatility)
        
        try:
            call_price = (spot * norm.cdf(d1) - 
                         strike * math.exp(-self.risk_free_rate * time) * norm.cdf(d2))
            return max(call_price, 0)
        except Exception:
            return 0
    
    def calculate_put_price(self, spot: float, strike: float, time: float, volatility: float) -> float:
        """Calculate theoretical put option price using Black-Scholes formula.
        
        Args:
            spot: Current spot price
            strike: Strike price
            time: Time to expiry in years
            volatility: Implied volatility (as decimal)
        
        Returns:
            Theoretical put option price
        """
        if spot <= 0 or strike <= 0 or time <= 0 or volatility <= 0:
            return 0
        
        d1, d2 = self.calculate_d1_d2(spot, strike, time, volatility)
        
        try:
            put_price = (strike * math.exp(-self.risk_free_rate * time) * norm.cdf(-d2) - 
                        spot * norm.cdf(-d1))
            return max(put_price, 0)
        except Exception:
            return 0
    
    def calculate_intrinsic_value(self, spot: float, strike: float, option_type: str) -> float:
        """Calculate intrinsic value of an option.
        
        Args:
            spot: Current spot price
            strike: Strike price
            option_type: 'CALL' or 'PUT'
        
        Returns:
            Intrinsic value
        """
        if option_type.upper() == 'CALL' or option_type.upper() == 'CE':
            return max(spot - strike, 0)
        elif option_type.upper() == 'PUT' or option_type.upper() == 'PE':
            return max(strike - spot, 0)
        return 0
    
    def calculate_time_value(self, option_price: float, intrinsic_value: float) -> float:
        """Calculate time value of an option.
        
        Args:
            option_price: Current market price of option
            intrinsic_value: Intrinsic value of option
        
        Returns:
            Time value
        """
        return max(option_price - intrinsic_value, 0)
    
    def analyze_option(self, spot: float, strike: float, market_price: float, 
                      expiry_date: str, volatility: float, option_type: str) -> Dict:
        """Perform complete Black-Scholes analysis for an option.
        
        Args:
            spot: Current spot price
            strike: Strike price
            market_price: Current market price of option
            expiry_date: Expiry date in YYYY-MM-DD format
            volatility: Implied volatility (as percentage)
            option_type: 'CALL' or 'PUT'
        
        Returns:
            Dictionary with analysis results
        """
        # Convert volatility from percentage to decimal
        vol_decimal = volatility / 100.0 if volatility > 1 else volatility
        
        # Calculate time to expiry
        time_to_expiry = self.calculate_time_to_expiry(expiry_date)
        
        # Calculate theoretical price
        if option_type.upper() in ['CALL', 'CE']:
            theoretical_price = self.calculate_call_price(spot, strike, time_to_expiry, vol_decimal)
            opt_type = 'CALL'
        else:
            theoretical_price = self.calculate_put_price(spot, strike, time_to_expiry, vol_decimal)
            opt_type = 'PUT'
        
        # Calculate intrinsic and time values
        intrinsic_value = self.calculate_intrinsic_value(spot, strike, opt_type)
        time_value_market = self.calculate_time_value(market_price, intrinsic_value)
        time_value_theoretical = self.calculate_time_value(theoretical_price, intrinsic_value)
        
        # Calculate pricing difference
        price_difference = market_price - theoretical_price
        price_difference_pct = (price_difference / theoretical_price * 100) if theoretical_price > 0 else 0
        
        # Determine if option is overpriced or underpriced
        pricing_status = "Fair Value"
        if abs(price_difference_pct) > 5:
            pricing_status = "Overpriced" if price_difference > 0 else "Underpriced"
        
        # Calculate moneyness
        moneyness = "ATM"
        if opt_type == 'CALL':
            if spot > strike * 1.02:
                moneyness = "ITM"
            elif spot < strike * 0.98:
                moneyness = "OTM"
        else:
            if spot < strike * 0.98:
                moneyness = "ITM"
            elif spot > strike * 1.02:
                moneyness = "OTM"
        
        return {
            'theoretical_price': round(theoretical_price, 2),
            'market_price': round(market_price, 2),
            'price_difference': round(price_difference, 2),
            'price_difference_pct': round(price_difference_pct, 2),
            'intrinsic_value': round(intrinsic_value, 2),
            'time_value_market': round(time_value_market, 2),
            'time_value_theoretical': round(time_value_theoretical, 2),
            'pricing_status': pricing_status,
            'moneyness': moneyness,
            'time_to_expiry_days': int(time_to_expiry * 365),
            'volatility_used': round(volatility, 2),
            'risk_free_rate': round(self.risk_free_rate * 100, 2)
        }