"""
Main FastAPI application for QuantuM FFT
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
import os
import numpy as np
import asyncio
import time
from typing import List
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fft_recursive import fft_recursive, ifft_recursive
from prediction import Predictor
from market_data import MarketData
from config import Config
from data_source_config import DataSourceConfig
from scalping_detector import ScalpingSignalDetector, LiveMonitor

app = FastAPI(
    title="QuantuM FFT API",
    description="Algoritmo de Predicción de Mercado usando FFT Recursivo",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor and live monitor
predictor = Predictor()
live_monitor = LiveMonitor(update_interval=5)
signal_detector = ScalpingSignalDetector()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "QuantuM FFT API v1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "quantum-fft-api",
        "version": "1.0.0"
    }

@app.get("/api/config/datasources")
async def get_data_sources():
    """Get available data sources and current configuration"""
    ds_config = DataSourceConfig()
    
    return {
        "sources": [
            {"id": "yfinance", "name": "Yahoo Finance", "type": "historical", "realtime": False},
            {"id": "ninjatrader", "name": "NinjaTrader", "type": "both", "realtime": True},
            {"id": "mt5", "name": "MetaTrader 5", "type": "both", "realtime": True}
        ],
        "current": {
            "realtime_source": ds_config.get_realtime_source(),
            "historical_source": ds_config.get_historical_source()
        }
    }

@app.post("/api/config/datasource")
async def set_data_source(request: dict):
    """Configure data source"""
    try:
        ds_config = DataSourceConfig()
        
        source_type = request.get("type")  # 'realtime' or 'historical'
        source = request.get("source")  # 'yfinance', 'ninjatrader', 'mt5'
        
        if source_type == "realtime":
            ds_config.set_realtime_source(source)
        elif source_type == "historical":
            ds_config.set_historical_source(source)
        else:
            return {"error": "Invalid type. Must be 'realtime' or 'historical'", "status": "failed"}
        
        return {
            "status": "success",
            "message": f"{source_type.capitalize()} source set to {source}"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.get("/api/config/symbols/mappings")
async def get_symbol_mappings():
    """Get all symbol mappings"""
    ds_config = DataSourceConfig()
    
    return {
        "mappings": ds_config.get_all_mappings()
    }

@app.post("/api/config/symbols/mapping")
async def add_symbol_mapping(request: dict):
    """Add or update symbol mapping"""
    try:
        ds_config = DataSourceConfig()
        
        internal_symbol = request.get("internal_symbol")
        source = request.get("source")
        external_symbol = request.get("external_symbol")
        
        if not all([internal_symbol, source, external_symbol]):
            return {"error": "Missing required fields", "status": "failed"}
        
        ds_config.add_symbol_mapping(internal_symbol, source, external_symbol)
        
        return {
            "status": "success",
            "message": f"Mapping added: {internal_symbol} -> {external_symbol} ({source})"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.get("/api/config/ninja")
async def get_ninja_config():
    """Get NinjaTrader configuration"""
    ds_config = DataSourceConfig()
    
    return {
        "exchange_dir": ds_config.get_ninja_exchange_dir()
    }

@app.post("/api/config/ninja")
async def set_ninja_config(request: dict):
    """Set NinjaTrader configuration"""
    try:
        ds_config = DataSourceConfig()
        exchange_dir = request.get("exchange_dir")
        
        if not exchange_dir:
            return {"error": "exchange_dir is required", "status": "failed"}
        
        ds_config.set_ninja_exchange_dir(exchange_dir)
        
        return {
            "status": "success",
            "message": f"NinjaTrader exchange directory set to {exchange_dir}"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.get("/api/config/mt5")
async def get_mt5_config():
    """Get MT5 configuration"""
    ds_config = DataSourceConfig()
    
    return ds_config.get_mt5_config()

@app.post("/api/config/mt5")
async def set_mt5_config(request: dict):
    """Set MT5 configuration"""
    try:
        ds_config = DataSourceConfig()
        
        host = request.get("host")
        port = request.get("port")
        
        if not all([host, port]):
            return {"error": "host and port are required", "status": "failed"}
        
        ds_config.set_mt5_config(host, int(port))
        
        return {
            "status": "success",
            "message": f"MT5 configuration set to {host}:{port}"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.get("/api/markets/types")
async def get_market_types():
    """Get all available market types"""
    from market_data import MarketData
    symbols = MarketData.get_available_symbols()
    
    return {
        "types": ["futures", "stocks", "crypto", "etf"],
        "futures": list(Config.FUTURES_SYMBOLS.keys()),
        "stocks": list(Config.STOCK_SYMBOLS.keys()),
        "crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD"],
        "etf": ["SPY", "QQQ", "IWM", "GLD"]
    }

@app.get("/api/markets/symbols/{market_type}")
async def get_symbols_by_type(market_type: str):
    """Get symbols by market type"""
    from market_data import MarketData
    from config import Config
    from data_source_config import DataSourceConfig
    
    market_type = market_type.lower()
    symbols = []
    
    if market_type == "futures":
        # Obtener símbolos configurados dinámicamente
        ds_config = DataSourceConfig()
        mappings = ds_config.get_all_mappings()
        
        # Si hay mapeos configurados, usarlos
        if mappings:
            for internal_symbol, sources in mappings.items():
                # Intentar obtener nombre bonito de Config si existe
                yf_symbol = sources.get('yfinance', '')
                name = f"{internal_symbol} (Futuro)"
                
                # Buscar nombre en Config usando el símbolo de yfinance o el interno
                if yf_symbol in Config.FUTURES_SYMBOLS:
                    name = Config.FUTURES_SYMBOLS[yf_symbol]
                elif internal_symbol in Config.FUTURES_SYMBOLS:
                    name = Config.FUTURES_SYMBOLS[internal_symbol]
                
                # Usar el símbolo de yfinance como ID principal si existe, sino el interno
                # Esto mantiene compatibilidad con el resto del sistema que espera MNQ=F
                symbol_id = yf_symbol if yf_symbol else internal_symbol
                
                symbols.append({
                    "symbol": symbol_id, 
                    "name": name, 
                    "type": "future",
                    "internal": internal_symbol
                })
        else:
            # Fallback a configuración estática si no hay mapeos
            symbols = [{"symbol": sym, "name": Config.FUTURES_SYMBOLS[sym], "type": "future"} 
                      for sym in Config.FUTURES_SYMBOLS.keys()]
                      
    elif market_type == "stocks":
        symbols = [{"symbol": sym, "name": Config.STOCK_SYMBOLS[sym], "type": "stock"} 
                  for sym in Config.STOCK_SYMBOLS.keys()]
    elif market_type == "crypto":
        symbols = [
            {"symbol": "BTC-USD", "name": "Bitcoin", "type": "crypto"},
            {"symbol": "ETH-USD", "name": "Ethereum", "type": "crypto"},
            {"symbol": "SOL-USD", "name": "Solana", "type": "crypto"},
            {"symbol": "ADA-USD", "name": "Cardano", "type": "crypto"}
        ]
    elif market_type == "etf":
        symbols = [
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "type": "etf"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust", "type": "etf"},
            {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "type": "etf"},
            {"symbol": "GLD", "name": "SPDR Gold Shares", "type": "etf"}
        ]
    
    return {"symbols": symbols}

@app.get("/api/markets/data/{symbol}")
async def get_market_data(symbol: str, period: str = "2y", interval: str = "1d"):
    """Get historical market data for a symbol"""
    try:
        # Decode URL-encoded symbol if necessary
        from urllib.parse import unquote
        symbol = unquote(symbol)
        
        market_data = MarketData(symbol)
        data = market_data.get_sample_data()
        
        return {
            "symbol": symbol,
            "data_points": len(data['close']),
            "price_range": {
                "min": float(data['close'].min()),
                "max": float(data['close'].max()),
                "current": float(data['close'][-1])
            },
            "dates": data['dates'].tolist() if len(data['dates']) > 0 else []
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "status": "failed"}

@app.post("/api/analysis/execute")
async def execute_analysis(request: dict):
    """Execute FFT analysis on a symbol"""
    try:
        symbol = request.get("symbol", Config.TICKER)
        
        # Decode URL-encoded symbol if necessary
        from urllib.parse import unquote
        symbol = unquote(symbol)
        
        prediction_days = request.get("prediction_days", Config.PREDICTION_DAYS)
        fft_components = request.get("fft_components", Config.FFT_COMPONENTS)
        data_source = request.get("data_source")  # Optional: override default source
        
        predictor.fft_components = fft_components
        
        market_data = MarketData(symbol, data_source)
        data = market_data.get_sample_data()
        
        analysis = predictor.full_analysis(data['normalized'])
        
        return {
            "status": "success",
            "symbol": symbol,
            "analysis": {
                "symbol_info": market_data.get_symbol_info(),
                "historical": {
                    "dates": [str(d) for d in data['dates']],
                    "prices": data['close'].tolist()
                },
                "trend": {
                    "direction": analysis['trend']['direction'],
                    "strength": float(analysis['trend']['strength']),
                    "low_freq_components": int(analysis['trend']['low_freq_components']),
                    "trend": (np.array(analysis['trend']['trend']) * data['close'].std() + data['close'].mean()).tolist()
                },
                "cycles": {
                    "dominant": analysis['cycles']['dominant_cycle'],
                    "top_10": analysis['cycles']['cycles'][:10]
                },
                "spectral": {
                    "max_magnitude": float(analysis['spectral']['magnitude'].max()),
                    "mean_magnitude": float(analysis['spectral']['magnitude'].mean()),
                    "dominant_frequency": float(analysis['spectral']['top_frequencies'][0]) 
                    if len(analysis['spectral']['top_frequencies']) > 0 else 0,
                    "frequencies": np.array(analysis['spectral']['frequencies']).tolist(),
                    "magnitude": np.array(analysis['spectral']['magnitude']).tolist(),
                    "reconstructed": (np.array(analysis['spectral']['reconstructed']) * data['close'].std() + data['close'].mean()).tolist()
                },
                "prediction": {
                    "confidence": float(analysis['prediction']['confidence']),
                    "days": prediction_days,
                    "initial_price": float(analysis['prediction']['prediction'][0] * data['close'].std() + data['close'].mean()),
                    "final_price": float(analysis['prediction']['prediction'][-1] * data['close'].std() + data['close'].mean()),
                    "predictions": (np.array(analysis['prediction']['prediction']) * data['close'].std() + data['close'].mean()).tolist()
                },
                "data_info": {
                    "data_points": len(data['close']),
                    "price_range": {
                        "min": float(data['close'].min()),
                        "max": float(data['close'].max()),
                        "current": float(data['close'][-1])
                    }
                }
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "status": "failed"}

@app.post("/api/compare/execute")
async def execute_comparison(request: dict):
    """Execute comparison analysis on multiple symbols"""
    try:
        raw_symbols = request.get("symbols", [])
        from urllib.parse import unquote
        symbols = [unquote(s) for s in raw_symbols]
        
        results = {}
        
        for symbol in symbols:
            try:
                market_data = MarketData(symbol)
                data = market_data.get_sample_data()
                analysis = predictor.full_analysis(data['normalized'])
                
                results[symbol] = {
                    "symbol_info": market_data.get_symbol_info(),
                    "trend": analysis['trend'],
                    "prediction": {
                        "confidence": float(analysis['prediction']['confidence']),
                        "initial_price": float(analysis['prediction']['prediction'][0] * data['close'].std() + data['close'].mean()),
                        "final_price": float(analysis['prediction']['prediction'][-1] * data['close'].std() + data['close'].mean())
                    },
                    "cycles": {
                        "dominant": analysis['cycles']['dominant_cycle']
                    }
                }
            except Exception as e:
                results[symbol] = {"error": str(e)}
        
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

# ============================================
# LIVE TRADING ENDPOINTS
# ============================================

@app.websocket("/ws/live/{symbol}")
async def websocket_live_data(websocket: WebSocket, symbol: str):
    """WebSocket para datos en tiempo real y señales de scalping"""
    print(f"\n{'='*60}")
    print(f"[WS CONNECT] Nueva conexion WebSocket iniciada")
    print(f"[WS CONNECT] Symbol recibido: {symbol}")
    print(f"{'='*60}\n")
    
    await manager.connect(websocket)
    
    try:
        # Configuración inicial
        ds_config = DataSourceConfig()
        data_source = ds_config.get_realtime_source()
        
        print(f"[WS INIT] Symbol: {symbol}, Data source: {data_source}")
        
        # Decodificar símbolo si viene URL-encoded
        from urllib.parse import unquote
        symbol = unquote(symbol)
        print(f"[WS INIT] Decoded symbol: {symbol}")
        
        print(f"[WS START] Iniciando loop de datos en tiempo real...")
        
        while True:
            try:
                print(f"\n[LOOP START] Iteracion WebSocket - {symbol}")
                
                # Obtener datos en tiempo real CON OHLC reales
                # IMPORTANTE: Crear nueva instancia para que use la fuente configurada actual
                market_data = MarketData(symbol, data_source)
                print(f"[LOOP] MarketData creado con fuente inicial: {data_source}")
                
                # Para trading en vivo, obtener datos de 1 minuto desde la fuente en tiempo real
                # Si es MT5/NinjaTrader, usar su timeframe; si es yfinance, usar diario
                # NOTA: fetch_data puede cambiar market_data.data_source si hace fallback
                if data_source in [DataSourceConfig.SOURCE_MT5, DataSourceConfig.SOURCE_NINJATRADER]:
                    # Fuentes de trading: obtener MUCHOS datos de 1 minuto (últimas 2 horas = 120 barras)
                    data = market_data.fetch_data(period='2h', interval='1min')
                    ohlc_data = market_data.preprocess_data(data)
                    print(f"[DATA] Using 1min OHLC from {market_data.data_source} - Got {len(ohlc_data['close'])} bars")
                else:
                    # yfinance: usar datos de 5 minutos (mínimo confiable)
                    data = market_data.fetch_data(period='1d', interval='5min')
                    ohlc_data = market_data.preprocess_data(data)
                    print(f"[DATA] Using 5min OHLC from {market_data.data_source} (1min not available)")
                
                # Actualizar data_source con el que realmente se está usando (puede haber cambiado por fallback)
                actual_source = market_data.data_source
                print(f"[DATA SOURCE] Actual source being used: {actual_source}")
                
                # IMPORTANTE: Para análisis FFT, usar SIEMPRE datos históricos de yfinance
                # Crear instancia separada con fuente histórica
                historical_source = ds_config.get_historical_source()
                historical_market_data = MarketData(symbol, historical_source)
                historical_data_daily = historical_market_data.get_sample_data(n_points=200)
                print(f"[FFT DATA] Using daily data from {historical_market_data.data_source} for FFT analysis")
                
                # Obtener precio actual
                realtime_price = market_data.get_realtime_price()
                current_price = ohlc_data['close'][-1]
                
                if realtime_price:
                    # MT5 devuelve dict con 'bid', 'ask', 'last'
                    if 'price' in realtime_price:
                        current_price = realtime_price['price']
                    elif 'last' in realtime_price:
                        current_price = realtime_price['last']
                    elif 'bid' in realtime_price:
                        current_price = (realtime_price['bid'] + realtime_price.get('ask', realtime_price['bid'])) / 2
                
                print(f"[LIVE DATA] Symbol: {symbol}, Price: {current_price}, Source: {actual_source}")
                
                # Ejecutar análisis FFT en datos diarios
                analysis = predictor.full_analysis(historical_data_daily['normalized'])
                
                print(f"[FFT] Cycle period: {analysis['cycles'].get('dominant_cycle', {}).get('period', 'N/A')}, Trend: {analysis['trend']['direction']}, Strength: {analysis['trend']['strength']:.3f}, Confidence: {analysis['prediction']['confidence']:.3f}")
                
                # Detectar señal de scalping (usar datos diarios para FFT)
                signal = signal_detector.detect_signal(
                    symbol=symbol,
                    close_prices=historical_data_daily['close'],
                    high_prices=historical_data_daily['close'],
                    low_prices=historical_data_daily['close'],
                    fft_analysis=analysis,
                    current_price=current_price
                )
                
                if signal:
                    print(f"[SIGNAL DETECTED] {signal.direction} at {signal.entry_price}, TP: {signal.take_profit}, SL: {signal.stop_loss}, Confidence: {signal.confidence:.2%}")
                    is_valid = signal_detector.validate_signal(signal)
                    print(f"[SIGNAL VALIDATION] Valid: {is_valid}, R:R: {abs(signal.take_profit - signal.entry_price) / abs(signal.entry_price - signal.stop_loss):.2f}:1")
                    
                    if is_valid:
                        print(f"[SIGNAL STRENGTH] {signal_detector.get_signal_strength(signal)}")
                else:
                    print(f"[NO SIGNAL] Waiting for scalping opportunity...")
                
                # Preparar respuesta
                response = {
                    'timestamp': time.time(),
                    'symbol': symbol,
                    'data_source': actual_source,  # Usar la fuente real que se está usando
                    'price': float(current_price),
                    'trend': analysis['trend']['direction'],
                    'trend_strength': float(analysis['trend']['strength']),
                    'confidence': float(analysis['prediction']['confidence']),
                    'dominant_cycle': analysis['cycles'].get('dominant_cycle'),
                    'signal': signal.to_dict() if signal else None,
                    'active_signals': live_monitor.get_active_signals(symbol),
                }
                
                # Agregar datos OHLC reales de 1 minuto
                if len(ohlc_data['close']) > 0 and 'dates' in ohlc_data:
                    try:
                        import pandas as pd
                        historical_candles = []
                        
                        # Obtener las últimas 100 velas de 1 minuto con OHLC real
                        start_idx = max(0, len(ohlc_data['close'])-100)
                        
                        for i in range(start_idx, len(ohlc_data['close'])):
                            # Convertir timestamp a Unix
                            date_val = ohlc_data['dates'][i]
                            if hasattr(date_val, 'timestamp'):
                                unix_time = int(date_val.timestamp())
                            elif isinstance(date_val, (int, float)):
                                unix_time = int(date_val / 1000000000) if date_val > 1e15 else int(date_val)
                            else:
                                unix_time = int(pd.Timestamp(date_val).timestamp())
                            
                            # Usar datos OHLC reales desde MT5/NinjaTrader
                            # Ajustar índice porque data puede tener más elementos que ohlc_data
                            data_idx = start_idx + (i - start_idx)
                            
                            if 'Open' in data.columns and 'High' in data.columns and 'Low' in data.columns and data_idx < len(data):
                                open_price = float(data['Open'].iloc[data_idx])
                                high_price = float(data['High'].iloc[data_idx])
                                low_price = float(data['Low'].iloc[data_idx])
                            else:
                                # Fallback: usar precio de cierre con pequeño spread
                                close_val = float(ohlc_data['close'][i])
                                open_price = float(ohlc_data['close'][max(0, i-1)])
                                high_price = close_val * 1.001
                                low_price = close_val * 0.999
                            
                            historical_candles.append({
                                'time': unix_time,
                                'open': open_price,
                                'high': high_price,
                                'low': low_price,
                                'close': float(ohlc_data['close'][i])
                            })
                        
                        response['historical_data'] = historical_candles
                        print(f"[OK] Sending {len(historical_candles)} real OHLC candles (1min)")
                        print(f"[DEBUG] Data shape: {data.shape}, OHLC close length: {len(ohlc_data['close'])}, Start idx: {start_idx}")
                    except Exception as e:
                        print(f"[ERROR] Error preparing historical_data: {e}")
                        import traceback
                        traceback.print_exc()
                        response['historical_data'] = []
                else:
                    response['historical_data'] = []
                
                # Si hay señal válida, agregarla al monitor
                if signal and signal_detector.validate_signal(signal):
                    live_monitor.add_signal(signal)
                    response['new_signal'] = True
                    response['signal_strength'] = signal_detector.get_signal_strength(signal)
                
                await websocket.send_json(response)
                print(f"[SEND] Response sent - Price: {response['price']}, Trend: {response['trend']}, Historical candles: {len(response.get('historical_data', []))}")
                
                # Esperar intervalo de actualización
                await asyncio.sleep(live_monitor.update_interval)
                
            except Exception as e:
                print(f"[ERROR] Exception in WebSocket loop: {e}")
                import traceback
                traceback.print_exc()
                
                # Enviar error informativo al frontend sin cerrar la conexión
                error_message = {
                    'error': str(e),
                    'timestamp': time.time(),
                    'symbol': symbol,
                    'message': f'Error obteniendo datos. Reintentando en 5 segundos...'
                }
                
                try:
                    await websocket.send_json(error_message)
                except:
                    print(f"[ERROR] Could not send error message to client")
                
                await asyncio.sleep(5)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/live/signals/{symbol}")
async def get_live_signals(symbol: str):
    """Obtiene señales activas para un símbolo"""
    try:
        signals = live_monitor.get_active_signals(symbol)
        
        return {
            "status": "success",
            "symbol": symbol,
            "signals": signals,
            "count": len(signals)
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.post("/api/live/execute")
async def execute_trade(request: dict):
    """Ejecuta una orden de trading en MT5 o NinjaTrader"""
    try:
        symbol = request.get("symbol")
        action = request.get("action")  # BUY, SELL, CLOSE
        quantity = request.get("quantity", 1)
        sl = request.get("sl", 0)
        tp = request.get("tp", 0)
        platform = request.get("platform", "ninjatrader")  # 'ninjatrader' o 'mt5'
        
        print(f"[ORDER] Executing {action} order for {symbol} on {platform.upper()}, Qty: {quantity}, SL: {sl}, TP: {tp}")
        
        ds_config = DataSourceConfig()
        
        if platform == "ninjatrader":
            from ninjatrader_connector import NinjaTraderConnector
            connector = NinjaTraderConnector()
            
            success = connector.send_command(action, symbol, quantity, sl, tp)
            
            print(f"[NINJA] Order result: {'SUCCESS' if success else 'FAILED'}")
            
            return {
                "status": "success" if success else "failed",
                "platform": "ninjatrader",
                "message": f"Orden {action} enviada a NinjaTrader"
            }
        
        elif platform == "mt5":
            from mt5_connector import MT5Connector
            connector = MT5Connector()
            
            if action == "CLOSE":
                # Cerrar posición en MT5 requiere ticket
                ticket = request.get("ticket")
                if not ticket:
                    return {"error": "Ticket requerido para cerrar posición", "status": "failed"}
                
                success = connector.close_position(ticket)
                print(f"[MT5] Close position {ticket}: {'SUCCESS' if success else 'FAILED'}")
                return {
                    "status": "success" if success else "failed",
                    "platform": "mt5",
                    "message": f"Posición {ticket} cerrada"
                }
            else:
                result = connector.send_order(symbol, action, quantity, sl, tp)
                print(f"[MT5] Order result: {result}")
                
                return {
                    "status": "success" if result else "failed",
                    "platform": "mt5",
                    "message": f"Orden {action} ejecutada",
                    "result": result
                }
        
        else:
            return {"error": "Plataforma no soportada", "status": "failed"}
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "status": "failed"}

@app.get("/api/live/price/{symbol}")
async def get_realtime_price(symbol: str):
    """Obtiene precio en tiempo real"""
    try:
        ds_config = DataSourceConfig()
        data_source = ds_config.get_realtime_source()
        
        market_data = MarketData(symbol, data_source)
        price_info = market_data.get_realtime_price()
        
        if not price_info:
            # Fallback a último precio histórico
            data = market_data.get_sample_data(n_points=1)
            price_info = {
                'price': float(data['close'][-1]),
                'source': data_source
            }
        
        return {
            "status": "success",
            "symbol": symbol,
            "price": price_info
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)