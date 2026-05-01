import numpy as np
from config import Config
from market_data import MarketData
from prediction import Predictor

def analyze_multiple_futures():
    futures_symbols = ['MNQ=F', 'MES=F', 'ES=F', 'NQ=F']
    
    print("=" * 80)
    print("ANALISIS COMPARATIVO DE FUTUROS DE INDICES")
    print("=" * 80)
    
    results = {}
    
    for ticker in futures_symbols:
        try:
            print(f"\nAnalizando {ticker} ({Config.get_symbol_name(ticker)})...")
            
            market_data = MarketData(ticker)
            data = market_data.get_sample_data()
            
            predictor = Predictor()
            analysis = predictor.full_analysis(data['normalized'])
            
            results[ticker] = {
                'symbol_info': market_data.get_symbol_info(),
                'data': data,
                'analysis': analysis
            }
            
            print(f"[OK] {ticker} - Tendencia: {analysis['trend']['direction']}")
            
        except Exception as e:
            print(f"[ERROR] {ticker}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("RESUMEN COMPARATIVO")
    print("=" * 80)
    
    print(f"\n{'Simbolo':<12} {'Nombre':<25} {'Tendencia':<8} {'Fuerza':<8} {'Confianza':<10}")
    print("-" * 80)
    
    for ticker, result in results.items():
        info = result['symbol_info']
        analysis = result['analysis']
        
        trend = analysis['trend']['direction']
        strength = f"{analysis['trend']['strength']:.2f}"
        confidence = f"{analysis['prediction']['confidence']:.1%}"
        
        print(f"{ticker:<12} {info['name']:<25} {trend:<8} {strength:<8} {confidence:<10}")
    
    if results:
        print("\n" + "=" * 80)
        print("DETALLES DE CICLOS DOMINANTES")
        print("=" * 80)
        
        for ticker, result in results.items():
            info = result['symbol_info']
            analysis = result['analysis']
            
            print(f"\n{ticker} - {info['name']}:")
            
            dom_cycle = analysis['cycles']['dominant_cycle']
            if dom_cycle:
                print(f"  Ciclo dominante: Periodo = {dom_cycle['period']:.1f} dias, "
                      f"Frecuencia = {dom_cycle['frequency']:.4f}")
            
            print(f"  Top 3 ciclos:")
            for i, cycle in enumerate(analysis['cycles']['cycles'][:3], 1):
                if cycle['period'] < 1000:
                    print(f"    {i}. Periodo: {cycle['period']:.1f} dias | "
                          f"Magnitud: {cycle['magnitude']:.4f}")
    
    print("\n" + "=" * 80)
    print("¡ANALISIS COMPLETADO!")
    print("=" * 80)

if __name__ == "__main__":
    analyze_multiple_futures()