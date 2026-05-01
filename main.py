import numpy as np
from config import Config
from market_data import MarketData
from prediction import Predictor
from visualization import Visualizer

def analyze_ticker(ticker: str):
    print("=" * 60)
    print("ALGORITMO FFT RECURSIVO PARA PREDICCION DE MERCADO")
    print("=" * 60)
    
    market_data = MarketData(ticker)
    symbol_info = market_data.get_symbol_info()
    
    print(f"\nSimbolo: {symbol_info['ticker']}")
    print(f"Nombre: {symbol_info['name']}")
    print(f"Tipo: {symbol_info['type']}")
    print(f"Periodo: {Config.PERIOD}")
    print(f"Dias a predecir: {Config.PREDICTION_DAYS}")
    print(f"Intervalo: {Config.INTERVAL}")
    print("\n" + "=" * 60)
    
    print("\n[1/5] Obteniendo datos del mercado...")
    data = market_data.get_sample_data()
    print(f"[OK] Datos obtenidos: {len(data['close'])} puntos")
    print(f"[OK] Rango de precios: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    
    print("\n[2/5] Preparando senal para analisis...")
    signal = data['normalized']
    print(f"[OK] Senal normalizada: media={signal.mean():.4f}, std={signal.std():.4f}")
    
    print("\n[3/5] Ejecutando analisis espectral con FFT recursivo...")
    predictor = Predictor()
    analysis = predictor.full_analysis(signal)
    print("[OK] Analisis completado")
    print(f"[OK] Componentes ciclicos identificados: {len(analysis['cycles']['cycles'])}")
    
    if analysis['cycles']['dominant_cycle']:
        dom_cycle = analysis['cycles']['dominant_cycle']
        print(f"[OK] Ciclo dominante: periodo={dom_cycle['period']:.1f} dias, "
              f"frecuencia={dom_cycle['frequency']:.4f}")
    
    print("\n[4/5] Generando predicciones...")
    print(f"[OK] Tendencia: {analysis['trend']['direction']}")
    print(f"[OK] Fuerza de tendencia: {analysis['trend']['strength']:.2f}")
    print(f"[OK] Confianza del modelo: {analysis['prediction']['confidence']:.2%}")
    
    print("\n[5/5] Creando visualizaciones...")
    visualizer = Visualizer()
    results = visualizer.create_all_visualizations(data['close'], analysis)
    print(f"[OK] {len(results)} visualizaciones creadas")
    
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    pred = analysis['prediction']['prediction']
    print(f"\nPrediccion para los proximos {Config.PREDICTION_DAYS} dias:")
    print(f"  Precio inicial predicho: ${pred[0] * data['close'].std() + data['close'].mean():.2f}")
    print(f"  Precio final predicho: ${pred[-1] * data['close'].std() + data['close'].mean():.2f}")
    
    if pred[-1] > pred[0]:
        print(f"  Cambio esperado: +{((pred[-1] - pred[0]) / pred[0] * 100):.2f}% (ALZA)")
    else:
        print(f"  Cambio esperado: {((pred[-1] - pred[0]) / pred[0] * 100):.2f}% (BAJA)")
    
    print(f"\nAnalisis de ciclos:")
    for i, cycle in enumerate(analysis['cycles']['cycles'][:5], 1):
        if cycle['period'] < 1000:
            print(f"  {i}. Periodo: {cycle['period']:.1f} dias | Magnitud: {cycle['magnitude']:.4f}")
    
    print("\nArchivos generados:")
    for result in results:
        print(f"  - {result}")
    
    print("\n" + "=" * 60)
    print("¡ANALISIS COMPLETADO!")
    print("=" * 60)

def main():
    analyze_ticker(Config.TICKER)

def list_available_symbols():
    print("\nSimbolos disponibles para analisis:")
    print("=" * 60)
    
    symbols = MarketData.get_available_symbols()
    
    print("\nFUTUROS DE INDICES:")
    for ticker, name in Config.FUTURES_SYMBOLS.items():
        print(f"  {ticker:10s} - {name}")
    
    print("\nACCIONES:")
    for ticker, name in Config.STOCK_SYMBOLS.items():
        print(f"  {ticker:10s} - {name}")
    
    print("\n" + "=" * 60)
    print("Para analizar un simbolo, edite Config.TICKER en config.py")
    print("o llame a analyze_ticker('SIMBOLO') en main.py")

if __name__ == "__main__":
    main()