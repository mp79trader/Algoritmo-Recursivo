import numpy as np
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from config import Config
from data_source_config import DataSourceConfig
from ninjatrader_connector import NinjaTraderConnector

# MT5 is optional
try:
    from mt5_connector import MT5Connector
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

class MarketData:
    def __init__(self, ticker: str = None, data_source: str = None):
        self.ticker = ticker or Config.TICKER
        self.is_future = Config.is_future(self.ticker)
        
        # Initialize data source configuration
        self.ds_config = DataSourceConfig()
        self.data_source = data_source or self.ds_config.get_historical_source()
        
        # Initialize connectors as needed
        self.ninja_connector = None
        self.mt5_connector = None
        
    def _get_connector(self):
        """Get the appropriate data connector based on source"""
        if self.data_source == DataSourceConfig.SOURCE_NINJATRADER:
            if self.ninja_connector is None:
                self.ninja_connector = NinjaTraderConnector()
            return self.ninja_connector
        
        elif self.data_source == DataSourceConfig.SOURCE_MT5:
            if not MT5_AVAILABLE:
                raise ImportError("MT5 connector not available. Install MetaTrader5 package.")
            if self.mt5_connector is None:
                self.mt5_connector = MT5Connector()
            return self.mt5_connector
        
        # Default to yfinance (no connector needed)
        return None
    
    def _map_symbol(self, ticker: str) -> str:
        """Map ticker to source-specific symbol"""
        # Extract internal symbol (remove =F suffix for futures)
        internal_symbol = ticker.replace('=F', '')
        
        # Map to source-specific format
        mapped_symbol = self.ds_config.map_symbol(internal_symbol, self.data_source)
        
        return mapped_symbol
        
    def _try_fetch_with_fallback(self, period: str, interval: str) -> pd.DataFrame:
        """Try to fetch data from configured source, fallback to yfinance if it fails"""
        original_source = self.data_source
        source_symbol = self._map_symbol(self.ticker)
        
        print(f"[FETCH] Ticker: {self.ticker}, Source: {self.data_source}, Mapped: {source_symbol}, Interval: {interval}")
        
        try:
            # Try configured source first
            if self.data_source == DataSourceConfig.SOURCE_YFINANCE:
                data = yf.download(source_symbol, period=period, interval=interval, progress=False)
                
                if data.empty:
                    raise ValueError(f"No data found for ticker {source_symbol}")
                
                print(f"[FETCH SUCCESS] Using yfinance for {self.ticker}")
                return data
            
            elif self.data_source == DataSourceConfig.SOURCE_NINJATRADER:
                connector = self._get_connector()
                
                # Map period to bar count (para 1min bars)
                period_map = {
                    '1h': 60, '2h': 120, '4h': 240, '1d': 390,
                    '5d': 1950, '1mo': 11700, '3mo': 35100,
                    '6mo': 70200, '1y': 252, '2y': 504, '5y': 1260
                }
                bars = period_map.get(period, 200)
                
                data = connector.fetch_data(source_symbol, interval, bars)
                
                if data.empty:
                    raise ValueError(f"No data found for ticker {source_symbol} from NinjaTrader")
                
                print(f"[FETCH SUCCESS] Using NinjaTrader for {self.ticker}")
                return data
            
            elif self.data_source == DataSourceConfig.SOURCE_MT5:
                connector = self._get_connector()
                
                # Map period to bar count
                period_map = {
                    '1h': 60, '2h': 120, '4h': 240, '1d': 390,
                    '5d': 1950, '1mo': 11700, '3mo': 35100,
                    '6mo': 70200, '1y': 252, '2y': 504, '5y': 1260
                }
                bars = period_map.get(period, 200)
                
                data = connector.fetch_data(source_symbol, interval, bars)
                
                if data.empty:
                    raise ValueError(f"No data found for ticker {source_symbol} from MT5")
                
                print(f"[FETCH SUCCESS] Using MT5 for {self.ticker}")
                return data
            
            else:
                raise ValueError(f"Unknown data source: {self.data_source}")
        
        except Exception as e:
            # Fallback to yfinance if configured source fails
            if original_source != DataSourceConfig.SOURCE_YFINANCE:
                print(f"[FETCH FALLBACK] {original_source} failed for {self.ticker}: {str(e)}")
                print(f"[FETCH FALLBACK] Trying yfinance as fallback...")
                
                try:
                    # Map to yfinance symbol format
                    yf_symbol = self._map_symbol_for_yfinance(self.ticker)
                    
                    # yfinance no soporta 1min para futuros, usar intervalos compatibles
                    fallback_interval = interval
                    fallback_period = period
                    
                    if interval == '1min':
                        # Para 1min, usar 5min (mínimo confiable en yfinance)
                        fallback_interval = '5m'
                        fallback_period = '1d'  # Último día de datos
                        print(f"[FETCH FALLBACK] yfinance no soporta 1min, usando 5min")
                    elif interval == '5min':
                        fallback_interval = '5m'
                    elif interval == '15min':
                        fallback_interval = '15m'
                    elif interval == '1h':
                        fallback_interval = '1h'
                    elif interval == '1d':
                        fallback_interval = '1d'
                    
                    print(f"[FETCH FALLBACK] Fetching {yf_symbol} with interval={fallback_interval}, period={fallback_period}")
                    data = yf.download(yf_symbol, period=fallback_period, interval=fallback_interval, progress=False)
                    
                    if data.empty:
                        raise ValueError(f"No data found for ticker {yf_symbol} from yfinance")
                    
                    print(f"[FETCH SUCCESS] Fallback to yfinance successful for {self.ticker} ({len(data)} bars)")
                    # Update data source to reflect what we're actually using
                    self.data_source = DataSourceConfig.SOURCE_YFINANCE
                    return data
                
                except Exception as yf_error:
                    print(f"[FETCH ERROR] Fallback to yfinance also failed: {str(yf_error)}")
                    raise ValueError(f"Error fetching data for {self.ticker}: {str(e)} (yfinance fallback: {str(yf_error)})")
            else:
                raise ValueError(f"Error fetching data for {self.ticker}: {str(e)}")

    
    def _map_symbol_for_yfinance(self, ticker: str) -> str:
        """Map internal symbol to yfinance format"""
        # Extract internal symbol (remove =F suffix for futures)
        internal_symbol = ticker.replace('=F', '')
        
        # Map to yfinance format (add =F back for futures)
        if internal_symbol in ['MNQ', 'MES', 'NQ', 'ES', 'YM']:
            return f"{internal_symbol}=F"
        
        return ticker
    
    def fetch_data(self, period: str = None, interval: str = None) -> pd.DataFrame:
        period = period or Config.PERIOD
        interval = interval or Config.INTERVAL
        
        return self._try_fetch_with_fallback(period, interval)
    
    def preprocess_data(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        df = df.copy()
        df.dropna(inplace=True)
        
        if len(df) == 0:
            raise ValueError("No valid data after preprocessing")
        
        if isinstance(df["Close"], pd.DataFrame):
            close_price = df["Close"].iloc[:, 0].values
        else:
            close_price = df["Close"].values
        
        # No multiplicar por 10 - los precios ya están correctos
        # if self.is_future:
        #     close_price = close_price * 10
        
        normalized_price = (close_price - close_price.mean()) / close_price.std()
        returns = np.diff(np.log(close_price))
        
        volume = None
        if 'Volume' in df:
            if isinstance(df['Volume'], pd.DataFrame):
                volume = df['Volume'].iloc[:, 0].values
            else:
                volume = df['Volume'].values

        return {
            'close': close_price,
            'normalized': normalized_price,
            'returns': returns,
            'dates': df.index.values,
            'volume': volume
        }
    
    def get_sample_data(self, n_points: Optional[int] = None) -> Dict[str, np.ndarray]:
        data = self.fetch_data()
        result = self.preprocess_data(data)
        
        if n_points and len(result['close']) > n_points:
            for key in result.keys():
                if result[key] is not None and isinstance(result[key], np.ndarray):
                    result[key] = result[key][-n_points:]
        
        return result
    
    def get_symbol_info(self) -> Dict:
        symbol_name = Config.get_symbol_name(self.ticker)
        return {
            'ticker': self.ticker,
            'name': symbol_name,
            'type': 'Future' if self.is_future else 'Stock',
            'is_future': self.is_future,
            'data_source': self.data_source
        }
    
    def get_realtime_price(self) -> Optional[Dict]:
        """Get real-time price from configured source with automatic fallback"""
        original_source = self.data_source
        
        try:
            source_symbol = self._map_symbol(self.ticker)
            
            if self.data_source == DataSourceConfig.SOURCE_NINJATRADER:
                try:
                    connector = self._get_connector()
                    position = connector.get_current_position(source_symbol)
                    
                    if position:
                        print(f"[PRICE] Using NinjaTrader for {self.ticker}")
                        return {
                            'price': position['average_price'],
                            'source': 'ninjatrader'
                        }
                except Exception as e:
                    print(f"[PRICE FALLBACK] NinjaTrader failed: {str(e)}")
            
            elif self.data_source == DataSourceConfig.SOURCE_MT5:
                try:
                    connector = self._get_connector()
                    price_info = connector.get_current_price(source_symbol)
                    
                    if price_info:
                        print(f"[PRICE] Using MT5 for {self.ticker}")
                        return {
                            'bid': price_info['bid'],
                            'ask': price_info['ask'],
                            'last': price_info['last'],
                            'source': 'mt5'
                        }
                except Exception as e:
                    print(f"[PRICE FALLBACK] MT5 failed: {str(e)}")
            
            # Fallback to yfinance (delayed)
            print(f"[PRICE] Using yfinance fallback for {self.ticker}")
            yf_symbol = self._map_symbol_for_yfinance(self.ticker)
            ticker_obj = yf.Ticker(yf_symbol)
            info = ticker_obj.info
            
            return {
                'price': info.get('regularMarketPrice', info.get('previousClose')),
                'source': 'yfinance'
            }
        
        except Exception as e:
            print(f"[PRICE ERROR] All sources failed for {self.ticker}: {e}")
            return None
    
    @staticmethod
    def fetch_multiple_tickers(tickers: List[str], period: str = None, interval: str = None, data_source: str = None) -> Dict[str, pd.DataFrame]:
        period = period or Config.PERIOD
        interval = interval or Config.INTERVAL
        
        results = {}
        for ticker in tickers:
            try:
                data = MarketData(ticker, data_source).fetch_data(period, interval)
                results[ticker] = data
            except Exception as e:
                print(f"Warning: Could not fetch data for {ticker}: {str(e)}")
        
        return results
    
    @staticmethod
    def get_available_symbols(data_source: str = None) -> Dict[str, List[str]]:
        """Get available symbols from configured source"""
        ds_config = DataSourceConfig()
        source = data_source or ds_config.get_historical_source()
        
        if source == DataSourceConfig.SOURCE_NINJATRADER:
            try:
                connector = NinjaTraderConnector()
                ninja_symbols = connector.get_available_symbols()
                
                return {
                    'futures': ninja_symbols,
                    'stocks': []
                }
            except Exception as e:
                print(f"Error getting NinjaTrader symbols: {e}")
        
        elif source == DataSourceConfig.SOURCE_MT5:
            if MT5_AVAILABLE:
                try:
                    connector = MT5Connector()
                    mt5_symbols = connector.get_available_symbols()
                    
                    return {
                        'futures': [s for s in mt5_symbols if any(x in s for x in ['NQ', 'ES', 'YM'])],
                        'stocks': [s for s in mt5_symbols if not any(x in s for x in ['NQ', 'ES', 'YM'])]
                    }
                except Exception as e:
                    print(f"Error getting MT5 symbols: {e}")
        
        # Default: return configured symbols
        return {
            'futures': list(Config.FUTURES_SYMBOLS.keys()),
            'stocks': list(Config.STOCK_SYMBOLS.keys())
        }
