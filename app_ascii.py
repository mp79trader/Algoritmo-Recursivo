from dashboard_ascii import TerminalDashboardASCII
from market_data import MarketData
from prediction import Predictor
from visualization import Visualizer
from config import Config
import os

class FFTDashboardAppASCII:
    def __init__(self):
        self.dashboard = TerminalDashboardASCII()
        self.visualizer = Visualizer()
        self.predictor = Predictor()
        
    def perform_analysis(self, ticker):
        steps = [
            {'desc': "Obteniendo datos del mercado...", 'action': None},
            {'desc': "Preparando senal para analisis...", 'action': None},
            {'desc': "Ejecutando analisis espectral FFT...", 'action': None},
            {'desc': "Generando predicciones...", 'action': None},
            {'desc': "Creando visualizaciones...", 'action': None}
        ]
        
        market_data = MarketData(ticker)
        data = None
        analysis = None
        prediction = None
        
        def step1():
            nonlocal data
            data = market_data.get_sample_data()
        
        def step2():
            pass
        
        def step3():
            nonlocal analysis
            analysis = self.predictor.full_analysis(data['normalized'])
        
        def step4():
            nonlocal prediction
            prediction = analysis['prediction']['prediction']
        
        def step5():
            results = self.visualizer.create_all_visualizations(data['close'], analysis)
            return results
        
        steps[0]['action'] = step1
        steps[2]['action'] = step3
        steps[3]['action'] = step4
        steps[4]['action'] = step5
        
        self.dashboard.show_progress(steps)
        
        self.display_results(market_data, data, analysis, prediction)
    
    def display_results(self, market_data, data, analysis, prediction):
        self.dashboard.console.print("\n[bold green]ANALISIS COMPLETADO EXITOSAMENTE[/bold green]\n")
        
        symbol_info = market_data.get_symbol_info()
        
        self.dashboard.show_symbol_info_table(symbol_info, data)
        self.dashboard.console.print()
        
        self.dashboard.show_summary_dashboard(symbol_info, analysis, prediction, data)
        self.dashboard.console.print()
        
        self.dashboard.show_trend_analysis(analysis)
        self.dashboard.console.print()
        
        self.dashboard.show_cycles_table(analysis['cycles'])
        self.dashboard.console.print()
        
        self.dashboard.show_spectral_summary(analysis['spectral'])
        self.dashboard.console.print()
        
        self.dashboard.show_confidence_meter(analysis['prediction']['confidence'])
        self.dashboard.console.print()
        
        config = {
            'prediction_days': Config.PREDICTION_DAYS,
            'std': data['close'].std(),
            'mean': data['close'].mean(),
            'last_price': data['close'][-1]
        }
        self.dashboard.show_prediction_table(prediction, config)
        self.dashboard.console.print()
        
        self.dashboard.console.print("[bold cyan]VISUALIZACIONES GENERADAS:[/bold cyan]\n")
        
        results_files = [f"results/{f}" for f in os.listdir("results") if f.endswith('.png')]
        for file_path in results_files[-5:]:
            filename = file_path.split('/')[-1]
            self.dashboard.console.print(f"  {filename}")
        
        self.dashboard.console.print("\n[yellow]Las visualizaciones estan disponibles en el directorio results/[/yellow]")

if __name__ == "__main__":
    import sys
    
    app = FFTDashboardAppASCII()
    
    ticker = "MNQ=F" if len(sys.argv) < 2 else sys.argv[1]
    
    print(f"Executing dashboard demo for {ticker}...\n")
    
    app.perform_analysis(ticker)
    
    print("\n[bold green]Demo completed![/bold green]")