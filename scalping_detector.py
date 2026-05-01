"""
Sistema de Detección de Señales de Scalping en Tiempo Real
Genera señales BUY/SELL con TP y SL automáticos basados en FFT
"""
import numpy as np
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScalpingSignal:
    """Señal de scalping con todos los parámetros necesarios"""
    timestamp: datetime
    symbol: str
    direction: str  # 'BUY' o 'SELL'
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    cycle_period: float
    reason: str
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'confidence': self.confidence,
            'cycle_period': self.cycle_period,
            'reason': self.reason,
            'risk_reward': abs(self.take_profit - self.entry_price) / abs(self.entry_price - self.stop_loss)
        }

class ScalpingSignalDetector:
    """Detector de señales de scalping en tiempo real"""
    
    def __init__(self, 
                 min_confidence: float = 0.6,
                 scalping_period_min: float = 0.1,
                 scalping_period_max: float = 3.0,
                 tp_multiplier: float = 2.0,
                 sl_atr_multiplier: float = 1.5):
        """
        Args:
            min_confidence: Confianza mínima para generar señal (0-1)
            scalping_period_min: Período mínimo de ciclo para scalping (días)
            scalping_period_max: Período máximo de ciclo para scalping (días)
            tp_multiplier: Multiplicador para Take Profit (Risk:Reward)
            sl_atr_multiplier: Multiplicador ATR para Stop Loss
        """
        self.min_confidence = min_confidence
        self.scalping_period_min = scalping_period_min
        self.scalping_period_max = scalping_period_max
        self.tp_multiplier = tp_multiplier
        self.sl_atr_multiplier = sl_atr_multiplier
        
    def calculate_atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
        """Calcula Average True Range para determinar volatilidad"""
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = np.mean(tr[-period:])
        
        return atr
    
    def detect_signal(self, 
                     symbol: str,
                     close_prices: np.ndarray,
                     high_prices: np.ndarray,
                     low_prices: np.ndarray,
                     fft_analysis: Dict,
                     current_price: float) -> Optional[ScalpingSignal]:
        """
        Detecta señal de scalping basada en análisis FFT
        
        Args:
            symbol: Símbolo del instrumento
            close_prices: Array de precios de cierre históricos
            high_prices: Array de precios máximos
            low_prices: Array de precios mínimos
            fft_analysis: Resultado del análisis FFT completo
            current_price: Precio actual del mercado
            
        Returns:
            ScalpingSignal si se detecta oportunidad, None si no
        """
        
        # Extraer datos del análisis FFT
        dominant_cycle = fft_analysis.get('cycles', {}).get('dominant_cycle')
        trend_direction = fft_analysis.get('trend', {}).get('direction')
        trend_strength = fft_analysis.get('trend', {}).get('strength', 0)
        prediction = fft_analysis.get('prediction', {})
        confidence = prediction.get('confidence', 0)
        
        # Verificar si el ciclo dominante está en rango de scalping
        if not dominant_cycle:
            return None
        
        cycle_period = dominant_cycle.get('period', 0)
        
        if not (self.scalping_period_min <= cycle_period <= self.scalping_period_max):
            return None
        
        # Verificar confianza mínima
        if confidence < self.min_confidence:
            return None
        
        # Calcular ATR para stop loss dinámico
        atr = self.calculate_atr(high_prices, low_prices, close_prices)
        
        # Determinar dirección de la señal
        if trend_direction == 'UP' and trend_strength > 0.3:
            direction = 'BUY'
            stop_loss = current_price - (atr * self.sl_atr_multiplier)
            take_profit = current_price + (atr * self.sl_atr_multiplier * self.tp_multiplier)
            reason = f"Tendencia alcista fuerte ({trend_strength:.2f}), ciclo {cycle_period:.1f}d"
            
        elif trend_direction == 'DOWN' and trend_strength > 0.3:
            direction = 'SELL'
            stop_loss = current_price + (atr * self.sl_atr_multiplier)
            take_profit = current_price - (atr * self.sl_atr_multiplier * self.tp_multiplier)
            reason = f"Tendencia bajista fuerte ({trend_strength:.2f}), ciclo {cycle_period:.1f}d"
            
        else:
            # Tendencia débil o lateral - no generar señal
            return None
        
        # Crear señal
        signal = ScalpingSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            direction=direction,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            cycle_period=cycle_period,
            reason=reason
        )
        
        return signal
    
    def validate_signal(self, signal: ScalpingSignal) -> bool:
        """
        Valida que la señal cumpla con criterios de riesgo
        
        Returns:
            True si la señal es válida, False si no
        """
        # Calcular Risk:Reward ratio
        risk = abs(signal.entry_price - signal.stop_loss)
        reward = abs(signal.take_profit - signal.entry_price)
        
        if risk == 0:
            return False
        
        risk_reward_ratio = reward / risk
        
        # Requerir al menos 1.5:1 de risk:reward
        if risk_reward_ratio < 1.5:
            return False
        
        # Verificar que stop loss no sea demasiado amplio (>5% del precio)
        stop_distance_pct = (risk / signal.entry_price) * 100
        if stop_distance_pct > 5.0:
            return False
        
        return True
    
    def get_signal_strength(self, signal: ScalpingSignal) -> str:
        """
        Determina la fuerza de la señal
        
        Returns:
            'FUERTE', 'MODERADA', o 'DÉBIL'
        """
        if signal.confidence >= 0.8:
            return 'FUERTE'
        elif signal.confidence >= 0.65:
            return 'MODERADA'
        else:
            return 'DÉBIL'

class LiveMonitor:
    """Monitor de mercado en tiempo real para múltiples instrumentos"""
    
    def __init__(self, update_interval: int = 5):
        """
        Args:
            update_interval: Intervalo de actualización en segundos
        """
        self.update_interval = update_interval
        self.signal_detector = ScalpingSignalDetector()
        self.active_signals: List[ScalpingSignal] = []
        self.last_prices: Dict[str, float] = {}
        
    def add_signal(self, signal: ScalpingSignal):
        """Agrega una señal activa al monitor"""
        self.active_signals.append(signal)
    
    def check_signal_status(self, signal: ScalpingSignal, current_price: float) -> str:
        """
        Verifica el estado de una señal activa
        
        Returns:
            'ACTIVE', 'TP_HIT', 'SL_HIT'
        """
        if signal.direction == 'BUY':
            if current_price >= signal.take_profit:
                return 'TP_HIT'
            elif current_price <= signal.stop_loss:
                return 'SL_HIT'
        else:  # SELL
            if current_price <= signal.take_profit:
                return 'TP_HIT'
            elif current_price >= signal.stop_loss:
                return 'SL_HIT'
        
        return 'ACTIVE'
    
    def get_active_signals(self, symbol: str = None) -> List[Dict]:
        """Obtiene señales activas, opcionalmente filtradas por símbolo"""
        if symbol:
            signals = [s for s in self.active_signals if s.symbol == symbol]
        else:
            signals = self.active_signals
        
        return [s.to_dict() for s in signals]
    
    def cleanup_closed_signals(self):
        """Limpia señales que ya alcanzaron TP o SL"""
        # En producción, esto se haría basado en verificación de precio actual
        # Por ahora mantener todas las señales
        pass
