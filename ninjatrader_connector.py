"""
NinjaTrader Connector - Reads data from NinjaTrader via file exchange
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime
import time
from data_source_config import DataSourceConfig

class NinjaTraderConnector:
    """Connects to NinjaTrader via file exchange system"""
    
    def __init__(self, exchange_dir: Optional[str] = None):
        self.config = DataSourceConfig()
        self.exchange_dir = exchange_dir or self.config.get_ninja_exchange_dir()
        
        if not os.path.exists(self.exchange_dir):
            raise ValueError(f"NinjaTrader exchange directory not found: {self.exchange_dir}")
    
    def get_available_symbols(self) -> list:
        """Get list of available symbols from NinjaTrader data files"""
        symbols = []
        
        try:
            for filename in os.listdir(self.exchange_dir):
                if filename.startswith('data_') and filename.endswith('.csv'):
                    # Extract symbol from filename: data_SYMBOL_TIMEFRAME.csv
                    parts = filename.replace('data_', '').replace('.csv', '').split('_')
                    if len(parts) >= 2:
                        symbol = parts[0]
                        if symbol not in symbols:
                            symbols.append(symbol)
        except Exception as e:
            print(f"Error reading NinjaTrader symbols: {e}")
        
        return symbols
    
    def read_data_file(self, symbol: str, timeframe: str = "1min") -> Optional[pd.DataFrame]:
        """Read market data from NinjaTrader file"""
        
        # Sanitize symbol (remove special chars that might be in yfinance format)
        safe_symbol = symbol.replace('=F', '').replace('-', '').replace(' ', '')
        
        # Map timeframe
        timeframe_map = {
            '1min': '1min',
            '5min': '5min',
            '15min': '15min',
            '1h': '60min',
            '1d': 'Daily',
            'daily': 'Daily'
        }
        
        ninja_timeframe = timeframe_map.get(timeframe.lower(), timeframe)
        
        filename = os.path.join(self.exchange_dir, f"data_{safe_symbol}_{ninja_timeframe}.csv")
        
        if not os.path.exists(filename):
            raise FileNotFoundError(f"NinjaTrader data file not found: {filename}")
            
        # Check file age - if older than 2 minutes (120s), consider it stale
        # Only for intraday timeframes
        if ninja_timeframe in ['1min', '5min', '15min', '60min']:
            mtime = os.path.getmtime(filename)
            age_seconds = time.time() - mtime
            
            # Umbral de tolerancia: 2 minutos para 1min, un poco más para otros
            max_age = 120 # 2 minutos por defecto
            if ninja_timeframe == '5min': max_age = 350 # ~6 min
            elif ninja_timeframe == '15min': max_age = 1000 # ~16 min
            elif ninja_timeframe == '60min': max_age = 3700 # ~61 min
            
            if age_seconds > max_age:
                raise ValueError(f"NinjaTrader data file is stale (age: {age_seconds:.1f}s > {max_age}s). NinjaTrader might be closed.")
        
        try:
            # Read CSV
            df = pd.read_csv(filename)
            
            # Convert Time column to datetime
            df['Time'] = pd.to_datetime(df['Time'])
            df.set_index('Time', inplace=True)
            
            # Rename columns to match yfinance format
            df.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume'
            }, inplace=True)
            
            return df
        
        except Exception as e:
            raise ValueError(f"Error reading NinjaTrader data file: {e}")
    
    def fetch_data(self, symbol: str, timeframe: str = "1d", bars: int = 200) -> pd.DataFrame:
        """Fetch data from NinjaTrader (mimics yfinance interface)"""
        
        df = self.read_data_file(symbol, timeframe)
        
        if df is None or df.empty:
            raise ValueError(f"No data available for {symbol} from NinjaTrader")
        
        # Return last N bars
        if len(df) > bars:
            df = df.tail(bars)
        
        return df
    
    def get_current_position(self, symbol: str) -> Optional[Dict]:
        """Read current position from NinjaTrader positions file"""
        
        positions_file = os.path.join(self.exchange_dir, "positions.csv")
        
        if not os.path.exists(positions_file):
            return None
        
        try:
            df = pd.read_csv(positions_file)
            
            # Filter by symbol
            safe_symbol = symbol.replace('=F', '').replace('-', '').replace(' ', '')
            position_row = df[df['Symbol'].str.contains(safe_symbol, na=False)]
            
            if position_row.empty:
                return None
            
            position = position_row.iloc[0]
            
            return {
                'symbol': position['Symbol'],
                'market_position': position['MarketPosition'],
                'quantity': position['Quantity'],
                'average_price': position['AveragePrice'],
                'unrealized_pnl': position['UnrealizedPnL'],
                'sl': position.get('SL', 0),
                'tp': position.get('TP', 0)
            }
        
        except Exception as e:
            print(f"Error reading positions: {e}")
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        """Read account information from NinjaTrader"""
        
        account_file = os.path.join(self.exchange_dir, "account.csv")
        
        if not os.path.exists(account_file):
            return None
        
        try:
            df = pd.read_csv(account_file)
            
            if df.empty:
                return None
            
            account = df.iloc[0]
            
            return {
                'account_name': account['AccountName'],
                'cash_value': account['CashValue'],
                'buying_power': account['BuyingPower'],
                'equity': account['Equity'],
                'realized_pnl': account['RealizedPnL'],
                'unrealized_pnl': account['UnrealizedPnL']
            }
        
        except Exception as e:
            print(f"Error reading account info: {e}")
            return None
    
    def send_command(self, action: str, symbol: str, quantity: int = 1, sl: float = 0, tp: float = 0):
        """Send trading command to NinjaTrader"""
        
        commands_file = os.path.join(self.exchange_dir, "commands.txt")
        
        # Sanitize symbol
        safe_symbol = symbol.replace('=F', '').replace('-', '').replace(' ', '')
        
        # Format: ACTION|SYMBOL|QUANTITY|SL|TP
        command = f"{action}|{safe_symbol}|{quantity}|{sl}|{tp}\n"
        
        try:
            with open(commands_file, 'a') as f:
                f.write(command)
            
            print(f"Command sent to NinjaTrader: {command.strip()}")
            return True
        
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
