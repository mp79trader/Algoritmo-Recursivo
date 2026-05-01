"""
MetaTrader 5 Connector - Connects to MT5 via socket or API
Note: This is a basic implementation. For full functionality, install MetaTrader5 package
pip install MetaTrader5
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime
from data_source_config import DataSourceConfig

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("MetaTrader5 package not installed. Install with: pip install MetaTrader5")

class MT5Connector:
    """Connects to MetaTrader 5"""
    
    def __init__(self):
        self.config = DataSourceConfig()
        self.initialized = False
        
        if not MT5_AVAILABLE:
            raise ImportError("MetaTrader5 package is not installed")
    
    def connect(self) -> bool:
        """Initialize connection to MT5"""
        if not MT5_AVAILABLE:
            return False
        
        if not mt5.initialize():
            print(f"MT5 initialize() failed, error code: {mt5.last_error()}")
            return False
        
        self.initialized = True
        print("Connected to MetaTrader 5")
        print(f"MT5 version: {mt5.version()}")
        
        return True
    
    def disconnect(self):
        """Close MT5 connection"""
        if self.initialized and MT5_AVAILABLE:
            mt5.shutdown()
            self.initialized = False
            print("Disconnected from MetaTrader 5")
    
    def get_available_symbols(self) -> list:
        """Get list of available symbols from MT5"""
        if not self.initialized:
            if not self.connect():
                return []
        
        symbols = mt5.symbols_get()
        
        if symbols is None:
            print(f"Error getting symbols: {mt5.last_error()}")
            return []
        
        return [symbol.name for symbol in symbols]
    
    def fetch_data(self, symbol: str, timeframe: str = "1d", bars: int = 200) -> pd.DataFrame:
        """Fetch historical data from MT5"""
        if not self.initialized:
            if not self.connect():
                raise ConnectionError("Cannot connect to MT5")
        
        # Map timeframe to MT5 constants
        timeframe_map = {
            '1min': mt5.TIMEFRAME_M1,
            '5min': mt5.TIMEFRAME_M5,
            '15min': mt5.TIMEFRAME_M15,
            '30min': mt5.TIMEFRAME_M30,
            '1h': mt5.TIMEFRAME_H1,
            '4h': mt5.TIMEFRAME_H4,
            '1d': mt5.TIMEFRAME_D1,
            'daily': mt5.TIMEFRAME_D1,
            '1w': mt5.TIMEFRAME_W1,
            '1mo': mt5.TIMEFRAME_MN1
        }
        
        mt5_timeframe = timeframe_map.get(timeframe.lower(), mt5.TIMEFRAME_D1)
        
        # Get data
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars)
        
        if rates is None or len(rates) == 0:
            raise ValueError(f"No data available for {symbol} from MT5. Error: {mt5.last_error()}")
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        
        # Convert time to datetime
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        # Rename columns to match yfinance format
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume'
        }, inplace=True)
        
        # Keep only required columns
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        return df
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if not self.initialized:
            if not self.connect():
                return None
        
        info = mt5.symbol_info(symbol)
        
        if info is None:
            print(f"Symbol info not found: {symbol}")
            return None
        
        return {
            'name': info.name,
            'description': info.description,
            'point': info.point,
            'digits': info.digits,
            'trade_contract_size': info.trade_contract_size,
            'min_volume': info.volume_min,
            'max_volume': info.volume_max,
            'volume_step': info.volume_step
        }
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get current price (tick)"""
        if not self.initialized:
            if not self.connect():
                return None
        
        tick = mt5.symbol_info_tick(symbol)
        
        if tick is None:
            print(f"Tick info not found: {symbol}")
            return None
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'last': tick.last,
            'volume': tick.volume,
            'time': datetime.fromtimestamp(tick.time)
        }
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        if not self.initialized:
            if not self.connect():
                return None
        
        account = mt5.account_info()
        
        if account is None:
            print(f"Account info not available: {mt5.last_error()}")
            return None
        
        return {
            'login': account.login,
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'margin_free': account.margin_free,
            'profit': account.profit,
            'leverage': account.leverage,
            'currency': account.currency
        }
    
    def get_positions(self) -> list:
        """Get open positions"""
        if not self.initialized:
            if not self.connect():
                return []
        
        positions = mt5.positions_get()
        
        if positions is None or len(positions) == 0:
            return []
        
        result = []
        for pos in positions:
            result.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'sl': pos.sl,
                'tp': pos.tp,
                'profit': pos.profit,
                'comment': pos.comment
            })
        
        return result
    
    def send_order(self, symbol: str, action: str, volume: float, sl: float = 0, tp: float = 0) -> Optional[Dict]:
        """Send trading order to MT5"""
        if not self.initialized:
            if not self.connect():
                return None
        
        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"Symbol not found: {symbol}")
            return None
        
        # Prepare order request
        order_type = mt5.ORDER_TYPE_BUY if action.upper() == 'BUY' else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).ask if action.upper() == 'BUY' else mt5.symbol_info_tick(symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": "QuantumFFT",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result is None:
            print(f"Order send failed: {mt5.last_error()}")
            return None
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed: {result.retcode} - {result.comment}")
            return None
        
        print(f"Order executed: {result.order}, volume: {result.volume}, price: {result.price}")
        
        return {
            'order': result.order,
            'volume': result.volume,
            'price': result.price,
            'retcode': result.retcode,
            'comment': result.comment
        }
    
    def close_position(self, ticket: int) -> bool:
        """Close position by ticket"""
        if not self.initialized:
            if not self.connect():
                return False
        
        position = mt5.positions_get(ticket=ticket)
        
        if position is None or len(position) == 0:
            print(f"Position {ticket} not found")
            return False
        
        pos = position[0]
        
        # Determine close order type (opposite of position type)
        order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(pos.symbol).bid if pos.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(pos.symbol).ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "Close by QuantumFFT",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to close position: {mt5.last_error()}")
            return False
        
        print(f"Position {ticket} closed successfully")
        return True
