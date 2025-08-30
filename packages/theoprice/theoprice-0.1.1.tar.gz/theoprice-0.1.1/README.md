# Option Chain Data Fetcher

A clean, interactive CLI app for fetching option chain data from Upstox API with Black-Scholes Greeks calculation.

## Features

- ✨ Interactive symbol selection with smart recognition
- 📊 Support for 180+ F&O enabled stocks
- 📈 Support for all major indices (NIFTY, BANKNIFTY, etc.)
- 📅 Automatic expiry date fetching
- 🎯 Strike price specific data filtering
- 🎨 Beautiful terminal UI with no clutter
- 📉 Displays both Call (CE) and Put (PE) options
- 📐 Shows comprehensive data: LTP, Volume, OI, Bid/Ask
- 🔬 Option Greeks: Delta, Gamma, Theta, Vega, IV
- 🔍 Built-in symbol search (type 'LIST' to see all supported symbols)

## Project Structure

```
bsholes_up/
├── src/                        # Main application code
│   ├── __init__.py
│   ├── option_chain_app.py    # Main application logic
│   ├── black_scholes.py       # Black-Scholes calculator
│   ├── stock_mappings.py      # Stock ISIN mappings
│   ├── instrument_manager.py  # F&O instrument management
│   └── token_manager.py       # OAuth & token management
├── web_app/                    # Web application
│   ├── app.py                  # FastAPI backend with OAuth
│   ├── templates/
│   │   └── index.html          # Frontend UI
│   └── static/
│       ├── app.js              # Frontend logic
│       └── styles.css          # UI styles
├── tests/                      # Test files
│   ├── test_api_connection.py
│   ├── test_stock_validation.py
│   ├── test_option_chain_flow.py
│   ├── test_integration.py
│   ├── test_black_scholes.py
│   └── test_integration_bs.py
├── scripts/                    # Debug and utility scripts
│   ├── debug_stock_options.py
│   ├── check_underlying.py
│   └── get_isin.py
├── run.py                      # CLI entry point
├── run_web.py                  # Web app entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md                   # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Upstox authentication:

   **Option A: OAuth Login (Recommended for Web App)**
   - Copy `.env.example` to `.env`
   - Add your Upstox API credentials:
     ```
     UPSTOX_CLIENT_ID=your_api_key
     UPSTOX_CLIENT_SECRET=your_api_secret
     UPSTOX_REDIRECT_URI=http://localhost:8000/auth/callback
     ```
   - Get these from your Upstox Developer Console app settings
   
   **Option B: Manual Token (CLI usage)**
   - Copy `.env.example` to `.env`
   - Add your access token to `.env`:
     ```
     UPSTOX_ACCESS_TOKEN=your_access_token
     ```

## Usage

### CLI Application
Run the CLI app:
```bash
python run.py
```

### Web Application (with OAuth)
Run the web app:
```bash
python run_web.py
```
Then open http://localhost:8000 in your browser.

**OAuth Flow:**
1. Click "Login with Upstox" button
2. You'll be redirected to Upstox login page
3. After successful login, you'll be redirected back
4. Token is automatically managed (expires at 3:30 AM IST daily)
5. No manual token entry needed!

Follow the prompts:
1. Enter asset symbol (e.g., TCS, SBIN, NIFTY, BANKNIFTY)
   - Type 'LIST' to see all supported F&O symbols
2. Select expiry date from the list
3. Enter strike price
4. View the option chain data with Greeks

## Testing

Run tests to verify everything works:
```bash
# Test API connection
python tests/test_api_connection.py

# Test stock validation
python tests/test_stock_validation.py

# Test option chain flow
python tests/test_option_chain_flow.py

# Integration tests
python tests/test_integration.py

# Test Black-Scholes calculations
python tests/test_black_scholes.py

# Test Black-Scholes integration
python tests/test_integration_bs.py
```

### Debug Scripts
```bash
# Debug stock options
python scripts/debug_stock_options.py

# Check underlying assets
python scripts/check_underlying.py

# Get ISIN for symbols
python scripts/get_isin.py
```

## Supported Symbols

### Indices
- NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY

### Stocks (180+ F&O enabled)
**Banking:** SBIN, HDFCBANK, ICICIBANK, AXISBANK, KOTAKBANK, and more  
**IT:** TCS, INFY, WIPRO, HCLTECH, TECHM, and more  
**Oil & Gas:** RELIANCE, ONGC, IOC, BPCL, and more  
**Auto:** TATAMOTORS, MARUTI, M&M, BAJAJ-AUTO, and more  
**Pharma:** SUNPHARMA, DRREDDY, CIPLA, DIVISLAB, and more  
**FMCG:** HINDUNILVR, ITC, NESTLEIND, BRITANNIA, and more  

Type 'LIST' in the app to see all supported symbols.

## Requirements

- Python 3.7+
- Upstox API access token
- Terminal with Unicode support for best display

## How It Works

The app uses ISIN (International Securities Identification Number) mappings to correctly identify F&O enabled stocks. For indices, it uses the standard index identifiers. This ensures accurate option chain data retrieval for all supported instruments.

## Deploying to Railway

1. Ensure your repository contains:
   - `Procfile` with: `web: uvicorn web_app.app:app --host 0.0.0.0 --port ${PORT:-8000}`
   - `.env.example` with `UPSTOX_ACCESS_TOKEN=`
   - `requirements.txt` including `fastapi`, `uvicorn`, and `Jinja2`

2. On Railway:
   - Create a new project and connect this repo.
   - In Settings → Variables, add `UPSTOX_ACCESS_TOKEN` with your token.
   - Deploy. The service will listen on `$PORT` automatically.

3. Health check: `GET /healthz` should return `{ "status": "ok" }`.