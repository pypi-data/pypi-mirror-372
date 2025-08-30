#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import upstox_client
from upstox_client.rest import ApiException
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
import inquirer
try:
    from .stock_mappings import INDEX_MAPPINGS
    from .instrument_manager import InstrumentManager
    from .black_scholes import BlackScholesCalculator
    from .token_manager import TokenManager
except ImportError:
    from stock_mappings import INDEX_MAPPINGS
    from instrument_manager import InstrumentManager
    from black_scholes import BlackScholesCalculator
    from token_manager import TokenManager

# Load environment variables
load_dotenv()

# Initialize Rich console for beautiful output
console = Console()

class OptionChainFetcher:
    def __init__(self, token_manager: TokenManager = None):
        """Initialize the Upstox API client with token manager."""
        self.token_manager = token_manager or TokenManager()
        self.configuration = upstox_client.Configuration()
        self.api_client = None
        self.options_api = None
        self.bs_calculator = BlackScholesCalculator(risk_free_rate=0.066)  # 6.60% for India
        self.instrument_manager = InstrumentManager()
        
        # Initialize with token
        self._initialize_api_client()
    
    def _initialize_api_client(self) -> bool:
        """Initialize API client with a valid token."""
        access_token = self.token_manager.get_valid_token()
        if not access_token:
            return False
            
        self.configuration.access_token = access_token
        self.api_client = upstox_client.ApiClient(self.configuration)
        self.options_api = upstox_client.OptionsApi(self.api_client)
        return True
    
    def _retry_with_new_token(self, func, *args, **kwargs):
        """Retry an API call with a new token if the current one fails."""
        try:
            return func(*args, **kwargs)
        except ApiException as e:
            # Check if this is a token-related error and we can get a new token
            if self.token_manager.handle_api_error(e):
                # Token was renewed, reinitialize API client and retry
                if self._initialize_api_client():
                    console.print("[green]Retrying with new token...[/green]")
                    return func(*args, **kwargs)
            # Re-raise the original exception if we can't handle it
            raise
    
    def get_instrument_key(self, symbol: str) -> tuple[str, str]:
        """Convert user symbol to instrument key format.
        Returns: (instrument_key, symbol_type) where symbol_type is 'INDEX', 'STOCK', or 'UNKNOWN'
        """
        symbol_upper = symbol.upper().strip()
        
        # Check if it's an index
        if symbol_upper in INDEX_MAPPINGS:
            return INDEX_MAPPINGS[symbol_upper], 'INDEX'
        
        # Check if it's a stock with F&O using dynamic lookup
        instrument_key = self.instrument_manager.get_instrument_key(symbol_upper)
        if instrument_key:
            return instrument_key, 'STOCK'
        
        # For unknown symbols, return None to indicate not found
        return None, 'UNKNOWN'
    
    def fetch_option_contracts(self, symbol: str) -> Optional[Dict]:
        """Fetch option contracts to get available expiry dates."""
        try:
            instrument_key, symbol_type = self.get_instrument_key(symbol)
            
            if instrument_key is None:
                console.print(f"[red]Symbol '{symbol}' not found in F&O list[/red]")
                console.print("[yellow]Note: Only F&O enabled stocks and indices are supported[/yellow]")
                
                # Show similar symbols if available
                similar_symbols = self.instrument_manager.search_symbols(symbol)
                if similar_symbols:
                    console.print(f"[yellow]Did you mean: {', '.join(similar_symbols[:5])}?[/yellow]")
                else:
                    console.print("[yellow]Try symbols like: NIFTY, BANKNIFTY, or check NSE F&O list[/yellow]")
                return None
            
            # Use retry mechanism for API call
            response = self._retry_with_new_token(
                self.options_api.get_option_contracts, 
                instrument_key
            )
            return response
        except ApiException as e:
            console.print(f"[red]Error fetching option contracts: {e}[/red]")
            return None
    
    def fetch_option_chain(self, symbol: str, expiry_date: str) -> Optional[Dict]:
        """Fetch option chain data for given symbol and expiry."""
        try:
            instrument_key, symbol_type = self.get_instrument_key(symbol)
            
            if instrument_key is None:
                console.print(f"[red]Symbol '{symbol}' not found in F&O list[/red]")
                return None
            
            # Use retry mechanism for API call
            response = self._retry_with_new_token(
                self.options_api.get_put_call_option_chain,
                instrument_key, 
                expiry_date
            )
            return response
        except ApiException as e:
            console.print(f"[red]Error fetching option chain: {e}[/red]")
            return None
    
    def extract_expiry_dates(self, contracts_response: Dict) -> List[str]:
        """Extract unique expiry dates from contracts response."""
        expiry_dates = set()
        if contracts_response and hasattr(contracts_response, 'data') and contracts_response.data:
            for contract in contracts_response.data:
                if hasattr(contract, 'expiry') and contract.expiry:
                    # Convert datetime to string format YYYY-MM-DD
                    if isinstance(contract.expiry, str):
                        expiry_dates.add(contract.expiry)
                    else:
                        # Handle datetime object
                        expiry_dates.add(contract.expiry.strftime('%Y-%m-%d'))
        
        # Sort expiry dates
        return sorted(list(expiry_dates))
    
    def extract_available_strikes(self, option_chain_data: Dict) -> tuple[List[float], Optional[float]]:
        """Extract available strike prices and spot price from option chain data.
        
        Returns:
            tuple: (sorted_strikes_list, spot_price)
        """
        strikes = set()
        spot_price = None
        
        if option_chain_data and hasattr(option_chain_data, 'data') and option_chain_data.data:
            for strike_data in option_chain_data.data:
                if hasattr(strike_data, 'strike_price') and strike_data.strike_price:
                    strikes.add(strike_data.strike_price)
                
                # Extract spot price from the first available record
                if spot_price is None and hasattr(strike_data, 'underlying_spot_price'):
                    spot_price = strike_data.underlying_spot_price
        
        return sorted(list(strikes)), spot_price
    
    def get_nearest_strikes(self, available_strikes: List[float], spot_price: float, count: int = 4) -> List[float]:
        """Find the nearest strikes to the spot price.
        
        Args:
            available_strikes: Sorted list of available strike prices
            spot_price: Current underlying spot price
            count: Number of nearest strikes to return (default 4)
        
        Returns:
            List of nearest strike prices, sorted
        """
        if not available_strikes or spot_price is None:
            return []
        
        # Find strikes above and below spot price
        strikes_below = [strike for strike in available_strikes if strike <= spot_price]
        strikes_above = [strike for strike in available_strikes if strike > spot_price]
        
        # Sort to get closest ones first
        strikes_below.sort(reverse=True)  # Closest to spot first
        strikes_above.sort()              # Closest to spot first
        
        # Get equal number from both sides if possible, otherwise adjust
        half_count = count // 2
        
        # Select strikes
        selected_strikes = []
        
        # Add strikes below (ITM for calls, OTM for puts)
        selected_strikes.extend(strikes_below[:half_count])
        
        # Add strikes above (OTM for calls, ITM for puts)
        selected_strikes.extend(strikes_above[:half_count])
        
        # If we don't have enough strikes, fill from the other side
        remaining_needed = count - len(selected_strikes)
        if remaining_needed > 0:
            if len(strikes_below) > half_count:
                selected_strikes.extend(strikes_below[half_count:half_count + remaining_needed])
            elif len(strikes_above) > half_count:
                selected_strikes.extend(strikes_above[half_count:half_count + remaining_needed])
        
        # Sort the final list
        return sorted(selected_strikes)
    
    def filter_by_strike(self, option_chain_data: Dict, strike_price: float) -> Dict:
        """Filter option chain data for specific strike price."""
        filtered_data = {
            'call': None,
            'put': None,
            'strike_info': {}
        }
        
        if option_chain_data and hasattr(option_chain_data, 'data') and option_chain_data.data:
            for strike_data in option_chain_data.data:
                if hasattr(strike_data, 'strike_price') and strike_data.strike_price == strike_price:
                    filtered_data['strike_info'] = {
                        'strike_price': strike_data.strike_price,
                        'expiry': strike_data.expiry if hasattr(strike_data, 'expiry') else None,
                        'pcr': strike_data.pcr if hasattr(strike_data, 'pcr') else None,
                        'underlying_spot_price': strike_data.underlying_spot_price if hasattr(strike_data, 'underlying_spot_price') else None
                    }
                    
                    if hasattr(strike_data, 'call_options') and strike_data.call_options:
                        filtered_data['call'] = self.extract_option_data(strike_data.call_options, 'CE')
                    
                    if hasattr(strike_data, 'put_options') and strike_data.put_options:
                        filtered_data['put'] = self.extract_option_data(strike_data.put_options, 'PE')
                    
                    break
        
        return filtered_data
    
    def extract_option_data(self, option_data: Any, option_type: str) -> Dict:
        """Extract relevant data from option object."""
        extracted = {
            'type': option_type,
            'instrument_key': option_data.instrument_key if hasattr(option_data, 'instrument_key') else None
        }
        
        # Extract market data
        if hasattr(option_data, 'market_data') and option_data.market_data:
            md = option_data.market_data
            extracted['market_data'] = {
                'ltp': md.ltp if hasattr(md, 'ltp') else None,
                'volume': md.volume if hasattr(md, 'volume') else None,
                'oi': md.oi if hasattr(md, 'oi') else None,
                'bid': md.bid_price if hasattr(md, 'bid_price') else None,
                'ask': md.ask_price if hasattr(md, 'ask_price') else None,
                'ltq': md.ltq if hasattr(md, 'ltq') else None,
                'close': md.close_price if hasattr(md, 'close_price') else None,
                'change': None
            }
            
            # Calculate change if we have ltp and close
            if extracted['market_data']['ltp'] and extracted['market_data']['close']:
                change = extracted['market_data']['ltp'] - extracted['market_data']['close']
                extracted['market_data']['change'] = change
        
        # Extract Greeks
        if hasattr(option_data, 'option_greeks') and option_data.option_greeks:
            greeks = option_data.option_greeks
            extracted['greeks'] = {
                'delta': greeks.delta if hasattr(greeks, 'delta') else None,
                'gamma': greeks.gamma if hasattr(greeks, 'gamma') else None,
                'theta': greeks.theta if hasattr(greeks, 'theta') else None,
                'vega': greeks.vega if hasattr(greeks, 'vega') else None,
                'iv': greeks.iv if hasattr(greeks, 'iv') else None
            }
        
        return extracted
    
    def analyze_with_black_scholes(self, filtered_data: Dict) -> Dict:
        """Add Black-Scholes analysis to filtered option data.
        
        Args:
            filtered_data: Filtered option chain data with call and put info
        
        Returns:
            Enhanced data with Black-Scholes analysis
        """
        strike_info = filtered_data.get('strike_info', {})
        spot_price = strike_info.get('underlying_spot_price')
        strike_price = strike_info.get('strike_price')
        expiry_date = strike_info.get('expiry')
        
        if not spot_price or not strike_price or not expiry_date:
            return filtered_data
        
        # Process Call option
        if filtered_data.get('call'):
            call_data = filtered_data['call']
            market_data = call_data.get('market_data', {})
            greeks = call_data.get('greeks', {})
            
            ltp = market_data.get('ltp')
            iv = greeks.get('iv')
            
            if ltp and iv:
                call_data['black_scholes'] = self.bs_calculator.analyze_option(
                    spot=spot_price,
                    strike=strike_price,
                    market_price=ltp,
                    expiry_date=expiry_date,
                    volatility=iv,
                    option_type='CALL'
                )
        
        # Process Put option
        if filtered_data.get('put'):
            put_data = filtered_data['put']
            market_data = put_data.get('market_data', {})
            greeks = put_data.get('greeks', {})
            
            ltp = market_data.get('ltp')
            iv = greeks.get('iv')
            
            if ltp and iv:
                put_data['black_scholes'] = self.bs_calculator.analyze_option(
                    spot=spot_price,
                    strike=strike_price,
                    market_price=ltp,
                    expiry_date=expiry_date,
                    volatility=iv,
                    option_type='PUT'
                )
        
        return filtered_data

class OptionChainUI:
    def __init__(self):
        self.console = Console()
    
    def display_header(self):
        """Display application header."""
        header_text = Text("Option Chain Data Fetcher", style="bold cyan")
        header_text.append("\nPowered by Upstox API", style="dim")
        self.console.print(Panel(header_text, border_style="cyan"))
        self.console.print()
    
    def get_symbol_input(self) -> str:
        """Get symbol input from user."""
        self.console.print("[cyan]Enter Asset Symbol[/cyan]", style="bold")
        self.console.print("Examples: TCS, SBIN, RELIANCE, INFY, NIFTY, BANKNIFTY", style="dim")
        self.console.print("Type 'LIST' to see all supported F&O symbols", style="dim")
        
        symbol = input("Symbol: ").strip().upper()
        
        # If user wants to see the list
        if symbol == 'LIST':
            self.show_supported_symbols()
            return self.get_symbol_input()  # Recursive call to get symbol after showing list
        
        return symbol
    
    def show_supported_symbols(self):
        """Display all supported F&O symbols."""
        self.console.print("\n[bold cyan]Supported F&O Symbols:[/bold cyan]\n")
        
        # Indices
        self.console.print("[yellow]Indices:[/yellow]")
        index_list = sorted(INDEX_MAPPINGS.keys())
        self.console.print(", ".join(index_list))
        
        # Stocks by sector
        stocks_by_sector = {
            "Banking": ['SBIN', 'HDFCBANK', 'ICICIBANK', 'AXISBANK', 'KOTAKBANK'],
            "IT": ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM'],
            "Oil & Gas": ['RELIANCE', 'ONGC', 'IOC', 'BPCL'],
            "Auto": ['TATAMOTORS', 'MARUTI', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO'],
            "Pharma": ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BIOCON'],
            "FMCG": ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR'],
            "Metals": ['TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'VEDL', 'COALINDIA']
        }
        
        self.console.print("\n[yellow]Stocks (Sample by Sector):[/yellow]")
        for sector, stocks in stocks_by_sector.items():
            self.console.print(f"[dim]{sector}:[/dim] {', '.join(stocks)}")
        
        # Get dynamic count of F&O stocks
        instrument_manager = InstrumentManager()
        fo_stocks = instrument_manager.get_fo_stocks()
        self.console.print(f"\n[dim]Total {len(fo_stocks)} F&O stocks supported[/dim]\n")
    
    def select_expiry_date(self, expiry_dates: List[str]) -> str:
        """Interactive expiry date selection."""
        if not expiry_dates:
            self.console.print("[red]No expiry dates available[/red]")
            return None
        
        # Format dates for display
        formatted_dates = []
        date_mapping = {}  # Map formatted string to actual date
        
        for date in expiry_dates:
            try:
                # date should already be a string in YYYY-MM-DD format
                if isinstance(date, str):
                    dt = datetime.strptime(date, "%Y-%m-%d")
                else:
                    dt = date  # If it's already a datetime object
                    date = dt.strftime("%Y-%m-%d")
                
                formatted = dt.strftime("%d %b %Y (%a)")
                display_text = f"{date} - {formatted}"
                formatted_dates.append(display_text)
                date_mapping[display_text] = date
            except Exception as e:
                # Fallback: just use the date as-is
                formatted_dates.append(str(date))
                date_mapping[str(date)] = str(date)
        
        questions = [
            inquirer.List('expiry',
                         message="Select Expiry Date",
                         choices=formatted_dates,
                         carousel=True)
        ]
        
        answers = inquirer.prompt(questions)
        if answers:
            # Return the actual date using our mapping
            selected = answers['expiry']
            return date_mapping.get(selected, selected.split(' - ')[0])
        return None
    
    def get_strike_price(self, nearest_strikes: List[float] = None, spot_price: float = None) -> float:
        """Get strike price input from user with smart suggestions."""
        if nearest_strikes and spot_price:
            self.console.print(f"\n[cyan]Strike Price Selection[/cyan] (Spot Price: [yellow]{spot_price:.2f}[/yellow])", style="bold")
            
            # Create choices with smart suggestions
            choices = []
            for strike in nearest_strikes:
                # Determine ITM/OTM/ATM status
                if strike < spot_price:
                    status = "ITM" if strike < spot_price else "ATM"
                    status_color = "green"
                elif strike > spot_price:
                    status = "OTM"
                    status_color = "red"
                else:
                    status = "ATM"
                    status_color = "yellow"
                
                diff = abs(strike - spot_price)
                choice_text = f"{strike:.2f} (±{diff:.2f} - {status})"
                choices.append(choice_text)
            
            # Add manual entry option
            choices.append("Enter manually")
            
            questions = [
                inquirer.List('strike_choice',
                             message="Select Strike Price",
                             choices=choices,
                             carousel=True)
            ]
            
            answers = inquirer.prompt(questions)
            if answers and answers['strike_choice'] != "Enter manually":
                # Extract strike price from the selected choice
                selected_text = answers['strike_choice']
                strike_str = selected_text.split()[0]  # Get the first part (strike price)
                return float(strike_str)
        
        # Fallback to manual entry
        self.console.print("\n[cyan]Enter Strike Price[/cyan]", style="bold")
        while True:
            try:
                strike = float(input("Strike Price: ").strip())
                return strike
            except ValueError:
                self.console.print("[red]Invalid input. Please enter a valid number.[/red]")
    
    def display_option_data(self, data: Dict, symbol: str):
        """Display option chain data in a beautiful format."""
        if not data or (not data.get('call') and not data.get('put')):
            self.console.print("[red]No data available for this strike price[/red]")
            return
        
        # Header with strike info
        strike_info = data.get('strike_info', {})
        self.console.print()
        
        info_text = Text(f"Option Chain for {symbol}", style="bold yellow")
        info_text.append(f"\nStrike: {strike_info.get('strike_price', 'N/A')}", style="white")
        info_text.append(f" | Spot: {strike_info.get('underlying_spot_price', 'N/A')}", style="white")
        info_text.append(f" | PCR: {strike_info.get('pcr', 'N/A'):.2f}" if strike_info.get('pcr') else " | PCR: N/A", style="white")
        
        self.console.print(Panel(info_text, border_style="yellow"))
        self.console.print()
        
        # Create tables for Call and Put
        tables = []
        
        for option_type in ['call', 'put']:
            option_data = data.get(option_type)
            if option_data:
                table = self.create_option_table(option_data, option_type.upper())
                tables.append(table)
        
        # Display tables side by side if both exist
        if len(tables) == 2:
            self.console.print(Columns(tables, equal=True, expand=True))
        elif len(tables) == 1:
            self.console.print(tables[0])
        
        # Display Black-Scholes Analysis
        self.display_black_scholes_analysis(data)
    
    def create_option_table(self, option_data: Dict, option_type: str) -> Table:
        """Create a beautiful table for option data."""
        # Determine color based on option type
        color = "green" if option_type == "CALL" else "red"
        
        table = Table(title=f"{option_type} Option", border_style=color, show_header=True, header_style="bold")
        
        # Add columns
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right")
        
        # Market Data
        market_data = option_data.get('market_data', {})
        
        # LTP with change
        ltp = market_data.get('ltp', 'N/A')
        change = market_data.get('change')
        if ltp != 'N/A' and change is not None:
            change_color = "green" if change >= 0 else "red"
            ltp_text = f"{ltp:.2f} [{change_color}]{change:+.2f}[/{change_color}]"
        else:
            ltp_text = str(ltp)
        
        table.add_row("Last Price", ltp_text)
        table.add_row("Volume", f"{market_data.get('volume', 'N/A'):,}" if market_data.get('volume') else 'N/A')
        table.add_row("Open Interest", f"{market_data.get('oi', 'N/A'):,}" if market_data.get('oi') else 'N/A')
        table.add_row("Bid", f"{market_data.get('bid', 'N/A'):.2f}" if market_data.get('bid') else 'N/A')
        table.add_row("Ask", f"{market_data.get('ask', 'N/A'):.2f}" if market_data.get('ask') else 'N/A')
        
        # Greeks
        greeks = option_data.get('greeks', {})
        if greeks:
            table.add_row("", "")  # Empty row for separation
            table.add_row("[bold]Greeks[/bold]", "")
            table.add_row("Delta", f"{greeks.get('delta', 'N/A'):.4f}" if greeks.get('delta') is not None else 'N/A')
            table.add_row("Gamma", f"{greeks.get('gamma', 'N/A'):.4f}" if greeks.get('gamma') is not None else 'N/A')
            table.add_row("Theta", f"{greeks.get('theta', 'N/A'):.4f}" if greeks.get('theta') is not None else 'N/A')
            table.add_row("Vega", f"{greeks.get('vega', 'N/A'):.4f}" if greeks.get('vega') is not None else 'N/A')
            table.add_row("IV", f"{greeks.get('iv', 'N/A'):.2f}%" if greeks.get('iv') is not None else 'N/A')
        
        return table
    
    def display_black_scholes_analysis(self, data: Dict):
        """Display Black-Scholes theoretical pricing analysis."""
        self.console.print("\n")
        
        # Create header for Black-Scholes section
        bs_header = Text("Theoretical Price Analysis", style="bold magenta")
        bs_header.append("\nRisk-Free Rate: 6.60% (India)", style="dim")
        self.console.print(Panel(bs_header, border_style="magenta"))
        self.console.print()
        
        # Create tables for Call and Put Black-Scholes analysis
        bs_tables = []
        
        for option_type in ['call', 'put']:
            option_data = data.get(option_type)
            if option_data and 'black_scholes' in option_data:
                bs_data = option_data['black_scholes']
                table = self.create_black_scholes_table(bs_data, option_type.upper())
                bs_tables.append(table)
        
        # Display Black-Scholes tables
        if len(bs_tables) == 2:
            self.console.print(Columns(bs_tables, equal=True, expand=True))
        elif len(bs_tables) == 1:
            self.console.print(bs_tables[0])
        elif len(bs_tables) == 0:
            self.console.print("[yellow]Black-Scholes analysis not available (missing IV data)[/yellow]")
    
    def create_black_scholes_table(self, bs_data: Dict, option_type: str) -> Table:
        """Create a table for Black-Scholes analysis results."""
        # Determine color based on option type
        color = "green" if option_type == "CALL" else "red"
        
        table = Table(title=f"{option_type} - Price Model", border_style=color, show_header=True)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right")
        
        # Pricing comparison
        table.add_row("[bold]Price Comparison[/bold]", "")
        table.add_row("Market Price", f"₹{bs_data['market_price']:.2f}")
        table.add_row("Theoretical Price", f"₹{bs_data['theoretical_price']:.2f}")
        
        # Price difference with color coding
        diff = bs_data['price_difference']
        diff_pct = bs_data['price_difference_pct']
        diff_color = "green" if diff < 0 else "red" if diff > 0 else "white"
        table.add_row("Difference", f"[{diff_color}]₹{diff:+.2f} ({diff_pct:+.2f}%)[/{diff_color}]")
        
        # Pricing status with color
        status = bs_data['pricing_status']
        status_color = "green" if status == "Underpriced" else "red" if status == "Overpriced" else "yellow"
        table.add_row("Status", f"[{status_color}]{status}[/{status_color}]")
        
        # Value breakdown
        table.add_row("", "")  # Empty row
        table.add_row("[bold]Value Breakdown[/bold]", "")
        table.add_row("Intrinsic Value", f"₹{bs_data['intrinsic_value']:.2f}")
        table.add_row("Time Value (Market)", f"₹{bs_data['time_value_market']:.2f}")
        table.add_row("Time Value (Theoretical)", f"₹{bs_data['time_value_theoretical']:.2f}")
        
        # Additional info
        table.add_row("", "")  # Empty row
        table.add_row("[bold]Parameters[/bold]", "")
        table.add_row("Moneyness", bs_data['moneyness'])
        table.add_row("Days to Expiry", str(bs_data['time_to_expiry_days']))
        table.add_row("IV Used", f"{bs_data['volatility_used']:.2f}%")
        
        return table
    
    def ask_continue(self) -> bool:
        """Ask user if they want to continue with another query."""
        self.console.print("\n")
        
        questions = [
            inquirer.List('continue_choice',
                         message="What would you like to do?",
                         choices=[
                             'Query another option chain',
                             'Exit application'
                         ],
                         carousel=True)
        ]
        
        answers = inquirer.prompt(questions)
        if answers:
            return answers['continue_choice'] == 'Query another option chain'
        return False

def main():
    """Main application flow with continue/exit loop."""
    # Initialize UI
    ui = OptionChainUI()
    ui.display_header()
    
    # Initialize token manager and fetcher
    token_manager = TokenManager()
    fetcher = OptionChainFetcher(token_manager)
    
    # Check if we have a valid token
    if not fetcher.api_client:
        console.print("[red]Could not get a valid access token. Exiting.[/red]")
        console.print("Please ensure you have a valid Upstox API token.")
        return
    
    # Main application loop
    while True:
        try:
            # Get symbol from user
            symbol = ui.get_symbol_input()
            if not symbol:
                console.print("[red]Invalid symbol[/red]")
                continue
            
            # Fetch option contracts
            console.print(f"\n[dim]Fetching available expiry dates for {symbol}...[/dim]")
            contracts = fetcher.fetch_option_contracts(symbol)
            
            if not contracts:
                console.print("[red]Failed to fetch option contracts[/red]")
                continue
            
            # Extract expiry dates
            expiry_dates = fetcher.extract_expiry_dates(contracts)
            
            if not expiry_dates:
                console.print("[red]No expiry dates found for this symbol[/red]")
                continue
            
            console.print(f"[green]Found {len(expiry_dates)} expiry dates[/green]\n")
            
            # Let user select expiry date
            selected_expiry = ui.select_expiry_date(expiry_dates)
            
            if not selected_expiry:
                console.print("[red]No expiry date selected[/red]")
                continue
            
            # Fetch option chain to get available strikes and spot price
            console.print(f"\n[dim]Fetching option chain data to get available strikes...[/dim]")
            option_chain = fetcher.fetch_option_chain(symbol, selected_expiry)
            
            if not option_chain:
                console.print("[red]Failed to fetch option chain[/red]")
                continue
            
            # Extract available strikes and spot price
            available_strikes, spot_price = fetcher.extract_available_strikes(option_chain)
            
            if not available_strikes:
                console.print("[red]No strike prices found for this expiry[/red]")
                continue
            
            # Get nearest strikes for smart selection
            nearest_strikes = fetcher.get_nearest_strikes(available_strikes, spot_price)
            
            console.print(f"[green]Found {len(available_strikes)} available strikes[/green]")
            
            # Get strike price from user with smart suggestions
            strike_price = ui.get_strike_price(nearest_strikes, spot_price)
            
            # Filter for specific strike
            filtered_data = fetcher.filter_by_strike(option_chain, strike_price)
            
            # Add Black-Scholes analysis
            filtered_data = fetcher.analyze_with_black_scholes(filtered_data)
            
            # Display the data
            ui.display_option_data(filtered_data, symbol)
            
            # Ask user if they want to continue
            continue_choice = ui.ask_continue()
            if not continue_choice:
                console.print("\n[cyan]Thanks for using Option Chain Fetcher! Goodbye! 👋[/cyan]")
                break
            
            # Add visual separator for next query
            console.print("\n" + "="*80)
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]An error occurred: {e}[/red]")
            # Ask if they want to continue even after error
            continue_choice = ui.ask_continue()
            if not continue_choice:
                console.print("\n[cyan]Thanks for using Option Chain Fetcher! Goodbye! 👋[/cyan]")
                break
            console.print("\n" + "="*80)
            console.print()

if __name__ == "__main__":
    main()