import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app_simple import FFTDashboardApp

if __name__ == "__main__":
    app = FFTDashboardApp()
    
    # Ejecutar directamente una prueba para demostrar el dashboard
    print("Ejecutando demostraci�n del dashboard...\n")
    
    # Simular análisis de MNQ=F
    ticker = "MNQ=F"
    
    print(f"Analizando {ticker}...\n")
    
    app.perform_analysis(ticker)
    
    print("\n[bold green]Demostraci�n completada![/bold green]")