"""
Data Source Configuration for Real-Time and Historical Data
Supports: yfinance, NinjaTrader, MetaTrader 5
"""
import os
import json
from typing import Dict, List, Optional

class DataSourceConfig:
    """Configuration for data sources and symbol mapping"""
    
    CONFIG_FILE = "data_source_config.json"
    
    # Data source types
    SOURCE_YFINANCE = "yfinance"
    SOURCE_NINJATRADER = "ninjatrader"
    SOURCE_MT5 = "mt5"
    
    # Default settings
    DEFAULT_SOURCE = SOURCE_MT5  # Usar MT5 por defecto para trading en vivo
    
    # NinjaTrader settings
    NINJA_EXCHANGE_DIR = r"C:\QuantumGAN\Exchange"
    
    # MT5 settings (to be configured)
    MT5_HOST = "localhost"
    MT5_PORT = 8002
    
    # Symbol mappings: {internal_symbol: {source: external_symbol}}
    SYMBOL_MAPPINGS = {
        'MNQ': {
            SOURCE_YFINANCE: 'MNQ=F',
            SOURCE_NINJATRADER: 'MNQ',
            SOURCE_MT5: 'NQ-MAR26'
        },
        'MES': {
            SOURCE_YFINANCE: 'MES=F',
            SOURCE_NINJATRADER: 'MES',
            SOURCE_MT5: 'ES-MAR26'
        },
        'NQ': {
            SOURCE_YFINANCE: 'NQ=F',
            SOURCE_NINJATRADER: 'NQ',
            SOURCE_MT5: 'NQ'
        },
        'ES': {
            SOURCE_YFINANCE: 'ES=F',
            SOURCE_NINJATRADER: 'ES',
            SOURCE_MT5: 'ES'
        }
    }
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'realtime_source': self.SOURCE_MT5,  # MT5 para trading en vivo
            'historical_source': self.SOURCE_YFINANCE,  # yfinance para análisis histórico
            'ninja_exchange_dir': self.NINJA_EXCHANGE_DIR,
            'mt5_host': self.MT5_HOST,
            'mt5_port': self.MT5_PORT,
            'symbol_mappings': self.SYMBOL_MAPPINGS,
            'use_realtime_for_analysis': False  # Use realtime only for live signals
        }
    
    def save_config(self):
        """Save configuration to file and sync with frontend"""
        try:
            # Guardar en raíz
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            # Sincronizar con frontend
            frontend_config = os.path.join('frontend', self.CONFIG_FILE)
            if os.path.exists('frontend'):
                try:
                    import shutil
                    shutil.copy2(self.CONFIG_FILE, frontend_config)
                    print(f"✅ Configuración sincronizada: {self.CONFIG_FILE} → {frontend_config}")
                except Exception as e:
                    print(f"⚠️ No se pudo sincronizar con frontend: {e}")
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_realtime_source(self) -> str:
        """Get configured real-time data source"""
        return self.config.get('realtime_source', self.DEFAULT_SOURCE)
    
    def set_realtime_source(self, source: str):
        """Set real-time data source"""
        if source in [self.SOURCE_YFINANCE, self.SOURCE_NINJATRADER, self.SOURCE_MT5]:
            self.config['realtime_source'] = source
            self.save_config()
        else:
            raise ValueError(f"Invalid source: {source}")
    
    def get_historical_source(self) -> str:
        """Get configured historical data source"""
        return self.config.get('historical_source', self.SOURCE_YFINANCE)
    
    def set_historical_source(self, source: str):
        """Set historical data source"""
        if source in [self.SOURCE_YFINANCE, self.SOURCE_NINJATRADER, self.SOURCE_MT5]:
            self.config['historical_source'] = source
            self.save_config()
        else:
            raise ValueError(f"Invalid source: {source}")
    
    def map_symbol(self, internal_symbol: str, source: str) -> str:
        """Map internal symbol to source-specific symbol"""
        mappings = self.config.get('symbol_mappings', self.SYMBOL_MAPPINGS)
        
        if internal_symbol in mappings:
            return mappings[internal_symbol].get(source, internal_symbol)
        
        # If no mapping exists, return as-is
        return internal_symbol
    
    def add_symbol_mapping(self, internal_symbol: str, source: str, external_symbol: str):
        """Add or update symbol mapping"""
        if 'symbol_mappings' not in self.config:
            self.config['symbol_mappings'] = {}
        
        if internal_symbol not in self.config['symbol_mappings']:
            self.config['symbol_mappings'][internal_symbol] = {}
        
        self.config['symbol_mappings'][internal_symbol][source] = external_symbol
        self.save_config()
    
    def get_ninja_exchange_dir(self) -> str:
        """Get NinjaTrader exchange directory"""
        return self.config.get('ninja_exchange_dir', self.NINJA_EXCHANGE_DIR)
    
    def set_ninja_exchange_dir(self, directory: str):
        """Set NinjaTrader exchange directory"""
        self.config['ninja_exchange_dir'] = directory
        self.save_config()
    
    def get_mt5_config(self) -> Dict:
        """Get MT5 connection configuration"""
        return {
            'host': self.config.get('mt5_host', self.MT5_HOST),
            'port': self.config.get('mt5_port', self.MT5_PORT)
        }
    
    def set_mt5_config(self, host: str, port: int):
        """Set MT5 connection configuration"""
        self.config['mt5_host'] = host
        self.config['mt5_port'] = port
        self.save_config()
    
    def get_all_mappings(self) -> Dict:
        """Get all symbol mappings"""
        return self.config.get('symbol_mappings', self.SYMBOL_MAPPINGS)
    
    def use_realtime_for_analysis(self) -> bool:
        """Check if realtime data should be used for analysis"""
        return self.config.get('use_realtime_for_analysis', False)
