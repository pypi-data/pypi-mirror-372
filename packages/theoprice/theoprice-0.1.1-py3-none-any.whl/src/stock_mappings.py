"""
Index mappings for NSE indices
F&O stocks are now fetched dynamically via InstrumentManager
"""

# F&O stocks are now fetched dynamically from Upstox API
# This eliminates the need for manual maintenance and ensures
# the list is always up-to-date with NSE F&O additions/removals

# Index mappings for NSE indices (static as they rarely change)
INDEX_MAPPINGS = {
    'NIFTY': 'NSE_INDEX|Nifty 50',
    'NIFTY50': 'NSE_INDEX|Nifty 50',
    'BANKNIFTY': 'NSE_INDEX|Nifty Bank',
    'FINNIFTY': 'NSE_INDEX|Nifty Fin Service',
    'MIDCPNIFTY': 'NSE_INDEX|NIFTY MID SELECT',
    'MIDCAP': 'NSE_INDEX|NIFTY MID SELECT',
}