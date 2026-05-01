import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
from config import Config

class Visualizer:
    def __init__(self):
        Config.create_output_dir()
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        self.dpi = Config.VISUALIZATION_DPI
    
    def plot_price_vs_prediction(self, original: np.ndarray, prediction: np.ndarray, 
                                  dates: np.ndarray = None, title: str = "Predicción de Precio") -> str:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        n_original = len(original)
        n_pred = len(prediction)
        
        x_original = np.arange(n_original)
        x_pred = np.arange(n_original - 1, n_original + n_pred - 1)
        
        ax.plot(x_original, original, label='Histórico', linewidth=2, color='blue')
        ax.plot(x_pred, prediction, label='Predicción', linewidth=2, color='red', linestyle='--')
        ax.axvline(x=n_original, color='black', linestyle=':', label='Inicio predicción')
        
        ax.set_xlabel('Días', fontsize=12)
        ax.set_ylabel('Precio', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        filename = f"{Config.OUTPUT_DIR}/price_prediction.png"
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def plot_spectrum(self, frequencies: np.ndarray, magnitude: np.ndarray, 
                      title: str = "Espectro de Frecuencias") -> str:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        n = len(frequencies)
        positive_indices = frequencies >= 0
        
        ax.plot(frequencies[positive_indices], magnitude[positive_indices], 
                linewidth=1.5, color='darkblue')
        ax.fill_between(frequencies[positive_indices], magnitude[positive_indices], 
                        alpha=0.3, color='darkblue')
        
        ax.set_xlabel('Frecuencia (ciclos/día)', fontsize=12)
        ax.set_ylabel('Magnitud', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        filename = f"{Config.OUTPUT_DIR}/spectrum.png"
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def plot_cycles(self, cycles: list, signal: np.ndarray, 
                    title: str = "Componentes Cíclicos Identificados") -> str:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        if cycles:
            periods = [c['period'] for c in cycles if c['period'] < 1000]
            magnitudes = [c['magnitude'] for c in cycles if c['period'] < 1000]
            
            ax1.bar(range(len(periods)), magnitudes, color='steelblue', alpha=0.7)
            ax1.set_xlabel('Ranking de Ciclos', fontsize=12)
            ax1.set_ylabel('Magnitud', fontsize=12)
            ax1.set_title('Magnitud de Componentes Cíclicos', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            for i, (period, mag) in enumerate(zip(periods, magnitudes)):
                ax1.text(i, mag, f'{period:.1f}d', ha='center', va='bottom', fontsize=8)
        
        ax2.plot(signal, linewidth=2, color='darkgreen')
        ax2.set_xlabel('Días', fontsize=12)
        ax2.set_ylabel('Precio Normalizado', fontsize=12)
        ax2.set_title('Señal Original', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = f"{Config.OUTPUT_DIR}/cycles.png"
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def plot_decomposition(self, original: np.ndarray, reconstructed: np.ndarray,
                           trend: np.ndarray, title: str = "Descomposición de Señal") -> str:
        fig, axes = plt.subplots(4, 1, figsize=(14, 12))
        
        axes[0].plot(original, linewidth=2, color='black')
        axes[0].set_title('Señal Original', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        axes[1].plot(reconstructed, linewidth=2, color='blue')
        axes[1].set_title('Señal Reconstruida (FFT Filtrada)', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        axes[2].plot(trend, linewidth=2, color='darkgreen')
        axes[2].set_title('Tendencia (Componentes de Baja Frecuencia)', fontsize=12, fontweight='bold')
        axes[2].grid(True, alpha=0.3)
        
        residual = original - reconstructed
        axes[3].plot(residual, linewidth=1, color='red')
        axes[3].set_title('Residuo (Ruido/Alta Frecuencia)', fontsize=12, fontweight='bold')
        axes[3].grid(True, alpha=0.3)
        
        for ax in axes:
            ax.set_xlabel('Días', fontsize=10)
        
        plt.tight_layout()
        filename = f"{Config.OUTPUT_DIR}/decomposition.png"
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def plot_trend_prediction(self, original: np.ndarray, trend: np.ndarray,
                              direction: str, strength: float, confidence: float,
                              title: str = "Predicción de Tendencia") -> str:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        n = len(original)
        
        color = 'green' if direction == 'UP' else 'red'
        
        ax.plot(original, label='Precio Histórico', linewidth=2, color='blue')
        ax.plot(trend, label='Tendencia', linewidth=2.5, color=color, linestyle='--')
        
        trend_slope = (trend[-1] - trend[0]) / n
        future_trend = trend[-1] + trend_slope * np.arange(1, 31)
        
        future_x = np.arange(n, n + 30)
        ax.plot(future_x, future_trend, color=color, linewidth=2, linestyle=':', 
                label='Proyección de Tendencia')
        
        ax.set_xlabel('Días', fontsize=12)
        ax.set_ylabel('Precio', fontsize=12)
        ax.set_title(f"{title} | Dirección: {direction} | Fuerza: {strength:.2f} | Confianza: {confidence:.2%}", 
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        filename = f"{Config.OUTPUT_DIR}/trend_prediction.png"
        plt.savefig(filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_all_visualizations(self, original: np.ndarray, analysis: Dict) -> list:
        results = []
        
        results.append(self.plot_price_vs_prediction(
            original,
            analysis['prediction']['prediction'],
            title=f"Predicción de Precio - {Config.TICKER}"
        ))
        
        results.append(self.plot_spectrum(
            analysis['spectral']['frequencies'],
            analysis['spectral']['magnitude'],
            title=f"Espectro de Frecuencias - {Config.TICKER}"
        ))
        
        results.append(self.plot_cycles(
            analysis['cycles']['cycles'],
            original,
            title=f"Componentes Cíclicos - {Config.TICKER}"
        ))
        
        results.append(self.plot_decomposition(
            original,
            analysis['spectral']['reconstructed'],
            analysis['trend']['trend'],
            title=f"Descomposición de Señal - {Config.TICKER}"
        ))
        
        results.append(self.plot_trend_prediction(
            original,
            analysis['trend']['trend'],
            analysis['trend']['direction'],
            analysis['trend']['strength'],
            analysis['prediction']['confidence'],
            title=f"Predicción de Tendencia - {Config.TICKER}"
        ))
        
        return results