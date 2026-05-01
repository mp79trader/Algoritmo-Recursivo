import numpy as np
from typing import Dict, Tuple
from fft_recursive import fft_recursive, ifft_recursive, filter_frequencies, extract_top_components, get_frequencies
from config import Config

class Predictor:
    def __init__(self, sample_rate: float = None):
        self.sample_rate = sample_rate or Config.SAMPLE_RATE
        self.fft_components = Config.FFT_COMPONENTS
        self.frequency_threshold = Config.FREQUENCY_THRESHOLD
    
    def analyze_signal(self, signal: np.ndarray) -> Dict:
        n = len(signal)
        
        fft_result = fft_recursive(signal)
        fft_result = fft_result[:n]
        
        frequencies = get_frequencies(n, self.sample_rate)
        magnitude = np.abs(fft_result)
        phase = np.angle(fft_result)
        
        filtered_fft = filter_frequencies(fft_result, frequencies, self.frequency_threshold)
        reconstructed_signal = np.real(ifft_recursive(filtered_fft))[:n]
        
        top_components, top_indices = extract_top_components(fft_result, self.fft_components)
        
        return {
            'fft': fft_result,
            'frequencies': frequencies,
            'magnitude': magnitude,
            'phase': phase,
            'filtered_fft': filtered_fft,
            'reconstructed': reconstructed_signal,
            'top_components': top_components,
            'top_indices': top_indices,
            'top_frequencies': frequencies[top_indices]
        }
    
    def predict_price(self, signal: np.ndarray, prediction_days: int = None) -> Dict:
        prediction_days = prediction_days or Config.PREDICTION_DAYS
        
        n = len(signal)
        fft_result = fft_recursive(signal)[:n]
        frequencies = get_frequencies(n, self.sample_rate)
        
        filtered_fft = filter_frequencies(fft_result, frequencies, self.frequency_threshold)
        
        extended_fft = np.zeros(n + prediction_days, dtype=complex)
        extended_fft[:n] = filtered_fft
        
        for i in range(1, prediction_days + 1):
            extended_fft[n + i - 1] = filtered_fft[-i]
        
        prediction = np.real(ifft_recursive(extended_fft))[:n + prediction_days]
        
        return {
            'prediction': prediction[-prediction_days:],
            'full_prediction': prediction,
            'confidence': self._calculate_confidence(signal, prediction[:n])
        }
    
    def analyze_trend(self, signal: np.ndarray) -> Dict:
        n = len(signal)
        fft_result = fft_recursive(signal)[:n]
        frequencies = get_frequencies(n, self.sample_rate)
        
        low_freq_indices = np.abs(frequencies) < 0.1
        trend_fft = fft_result.copy()
        trend_fft[~low_freq_indices] = 0
        
        trend = np.real(ifft_recursive(trend_fft))[:n]
        
        trend_direction = "UP" if trend[-1] > trend[0] else "DOWN"
        trend_strength = float(np.abs(trend[-1] - trend[0]) / np.std(signal))
        
        return {
            'trend': trend.tolist(),
            'direction': trend_direction,
            'strength': trend_strength,
            'low_freq_components': int(np.sum(low_freq_indices))
        }
    
    def analyze_cycles(self, signal: np.ndarray) -> Dict:
        n = len(signal)
        fft_result = fft_recursive(signal)
        frequencies = get_frequencies(n, self.sample_rate)
        magnitude = np.abs(fft_result)
        
        positive_freqs = frequencies[:n//2]
        positive_magnitude = magnitude[:n//2]
        
        peak_indices = self._find_peaks(positive_magnitude, distance=5)
        
        cycles = []
        for idx in peak_indices:
            freq = float(positive_freqs[idx])
            mag = float(positive_magnitude[idx])
            
            if freq != 0:
                period = 1 / abs(freq)
            else:
                period = 0.0 # Handle infinity/zero freq
                
            cycles.append({
                'frequency': freq,
                'period': float(period),
                'magnitude': mag,
                'index': int(idx)
            })
        
        cycles.sort(key=lambda x: x['magnitude'], reverse=True)
        
        return {
            'cycles': cycles[:10],
            'dominant_cycle': cycles[0] if cycles else None
        }
    
    def full_analysis(self, signal: np.ndarray) -> Dict:
        spectral = self.analyze_signal(signal)
        price_pred = self.predict_price(signal)
        trend = self.analyze_trend(signal)
        cycles = self.analyze_cycles(signal)
        
        return {
            'spectral': spectral,
            'prediction': price_pred,
            'trend': trend,
            'cycles': cycles
        }
    
    def _calculate_confidence(self, original: np.ndarray, reconstructed: np.ndarray) -> float:
        error = np.mean((original[:len(reconstructed)] - reconstructed) ** 2)
        variance = np.var(original)
        r_squared = 1 - error / variance if variance > 0 else 0
        return max(0, r_squared)
    
    def _find_peaks(self, signal: np.ndarray, distance: int = 5) -> np.ndarray:
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(signal, distance=distance)
        return peaks