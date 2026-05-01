from dashboard import TerminalDashboard
from market_data import MarketData
from prediction import Predictor
from visualization import Visualizer
from config import Config
import os

class FFTDashboardApp:
    def __init__(self):
        self.dashboard = TerminalDashboard()
        self.visualizer = Visualizer()
        self.predictor = Predictor()
        
    def run(self):
        while True:
            choice = self.dashboard.show_main_menu()
            
            if choice == "🚪 Salir":
                break
            elif "único instrumento" in choice:
                self.analyze_single_instrument()
            elif "múltiples futuros" in choice:
                self.analyze_multiple_futures()
            elif "interfaz web" in choice:
                self.launch_web_interface()
            elif "Lista de símbolos" in choice:
                self.dashboard.show_available_symbols()
                self.wait_for_continue()
            elif "Configuración" in choice:
                self.dashboard.show_config_menu()
                self.dashboard.show_datasource_config()
                self.wait_for_continue()
            elif "resultados anteriores" in choice:
                self.show_previous_results()
    
    def launch_web_interface(self):
        import subprocess
        import time
        import platform
        
        self.dashboard.console.print("\n[bold cyan]🚀 Iniciando aplicación Desktop (Electron)...[/bold cyan]")
        self.dashboard.console.print("[yellow]Ejecutando entorno en segundo plano...[/yellow]")
        
        # Determine paths
        frontend_dir = os.path.join(os.getcwd(), "frontend")
        node_modules = os.path.join(frontend_dir, "node_modules")
        
        # Check dependencies
        if not os.path.exists(node_modules):
            self.dashboard.console.print("[dim]Instalando dependencias... (esto puede tardar un poco)[/dim]")
            subprocess.run("npm install", shell=True, cwd=frontend_dir)
            
        # Log file
        log_file = open("electron_debug.log", "w")
        
        cmd = "npm run electron:dev"
        
        try:
            if platform.system() == "Windows":
                # CREATE_NO_WINDOW = 0x08000000
                creationflags = 0x08000000
                process = subprocess.Popen(
                    cmd, 
                    cwd=frontend_dir, 
                    shell=True, 
                    stdout=log_file, 
                    stderr=log_file,
                    creationflags=creationflags
                )
            else:
                process = subprocess.Popen(
                    cmd, 
                    cwd=frontend_dir, 
                    shell=True, 
                    stdout=log_file, 
                    stderr=log_file
                )
                
            self.dashboard.console.print(f"[green]✅ Aplicación iniciada (PID: {process.pid}).[/green]")
            self.dashboard.console.print("[dim]La ventana de la aplicación debería aparecer en breve.[/dim]")
            
        except Exception as e:
            self.dashboard.console.print(f"[red]Error al iniciar Electron: {e}[/red]")
            
        self.wait_for_continue()

    def analyze_single_instrument(self):
        symbol_type = self.dashboard.console.input("[cyan]¿Tipo de instrumento? (futuro/accion/todos): [/cyan]").strip().lower()
        
        if symbol_type == "futuro":
            selected_symbol = self.dashboard.show_symbol_selection("futures")
        elif symbol_type == "accion":
            selected_symbol = self.dashboard.show_symbol_selection("stocks")
        else:
            selected_symbol = self.dashboard.show_symbol_selection("all")
        
        if not selected_symbol or selected_symbol == "⬅️ Volver al menú principal":
            return
        
        self.perform_analysis(selected_symbol)
    
    def perform_analysis(self, ticker):
        steps = [
            {'desc': "📥 Obteniendo datos del mercado...", 'action': None},
            {'desc': "📊 Preparando señal para análisis...", 'action': None},
            {'desc': "🔬 Ejecutando análisis espectral FFT...", 'action': None},
            {'desc': "📈 Generando predicciones...", 'action': None},
            {'desc': "🎨 Creando visualizaciones...", 'action': None}
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
        self.dashboard.console.print("\n[bold green]✅ ANÁLISIS COMPLETADO EXITOSAMENTE[/bold green]\n")
        
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
        
        while True:
            viz_choice = self.dashboard.show_visualization_menu(
                [f"results/{f}" for f in os.listdir("results") if f.endswith('.png')]
            )
            
            if "Ver todas" in viz_choice:
                results_files = [f"results/{f}" for f in os.listdir("results") if f.endswith('.png')]
                self.dashboard.open_visualizations(results_files)
            elif "seleccionar una visualización" in viz_choice:
                self.show_single_visualization()
            elif "directorio" in viz_choice:
                self.open_results_directory()
            elif "Volver al menú principal" in viz_choice:
                break
    
    def show_single_visualization(self):
        files = [f for f in os.listdir("results") if f.endswith('.png')]
        files.sort()
        
        if not files:
            self.dashboard.console.print("[yellow]No hay visualizaciones disponibles.[/yellow]")
            return
        
        choices = files + ["⬅️ Volver"]
        
        from questionary import select
        choice = select(
            "Selecciona una visualización:",
            choices=choices,
            qmark="➤"
        ).ask()
        
        if choice != "⬅️ Volver":
            self.dashboard.open_visualizations([f"results/{choice}"])
    
    def open_results_directory(self):
        import subprocess
        import platform
        
        results_dir = os.path.join(os.getcwd(), "results")
        
        if platform.system() == 'Windows':
            os.startfile(results_dir)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', results_dir])
        else:
            subprocess.call(['xdg-open', results_dir])
        
        self.dashboard.console.print(f"[green]✓ Directorio abierto: {results_dir}[/green]")
    
    def analyze_multiple_futures(self):
        from market_data import MarketData
        from config import Config
        
        futures_symbols = ['MNQ=F', 'MES=F', 'ES=F', 'NQ=F']
        
        results = {}
        
        for ticker in futures_symbols:
            try:
                market_data = MarketData(ticker)
                data = market_data.get_sample_data()
                analysis = self.predictor.full_analysis(data['normalized'])
                
                results[ticker] = {
                    'symbol_info': market_data.get_symbol_info(),
                    'data': data,
                    'analysis': analysis
                }
            except Exception as e:
                self.dashboard.console.print(f"[red]Error analizando {ticker}: {str(e)}[/red]")
        
        self.display_comparative_results(results)
    
    def display_comparative_results(self, results):
        from rich.table import Table
        
        self.dashboard.console.print("\n[bold green]✅ ANÁLISIS COMPARATIVO COMPLETADO[/bold green]\n")
        
        table = Table(title="Comparativa de Futuros", show_header=True, header_style="bold magenta")
        table.add_column("Símbolo", style="cyan", width=10)
        table.add_column("Nombre", style="white", width=25)
        table.add_column("Tendencia", style="white", width=10)
        table.add_column("Fuerza", style="white", width=8)
        table.add_column("Confianza", style="white", width=10)
        
        for ticker, result in results.items():
            info = result['symbol_info']
            analysis = result['analysis']
            
            trend = analysis['trend']['direction']
            trend_style = "green" if trend == 'UP' else "red"
            
            table.add_row(
                ticker,
                info['name'],
                f"[{trend_style}]{trend}[/]",
                f"{analysis['trend']['strength']:.2f}",
                f"{analysis['prediction']['confidence']:.1%}"
            )
        
        self.dashboard.console.print(table)
        
        if results:
            self.dashboard.console.print("\n[bold cyan]📊 Detalles de Ciclos Dominantes:[/bold cyan]\n")
            
            for ticker, result in results.items():
                info = result['symbol_info']
                analysis = result['analysis']
                
                self.dashboard.console.print(f"[bold yellow]{ticker} - {info['name']}:[/bold yellow]")
                
                dom_cycle = analysis['cycles']['dominant_cycle']
                if dom_cycle:
                    self.dashboard.console.print(f"  Ciclo Dominante: Período = {dom_cycle['period']:.2f} días, "
                                                 f"Frecuencia = {dom_cycle['frequency']:.4f}")
                
                self.dashboard.console.print("  Top 3 Ciclos:")
                for i, cycle in enumerate(analysis['cycles']['cycles'][:3], 1):
                    if cycle['period'] < 1000:
                        self.dashboard.console.print(f"    {i}. Período: {cycle['period']:.2f} días | "
                                                   f"Magnitud: {cycle['magnitude']:.4f}")
                
                self.dashboard.console.print()
    
    def show_previous_results(self):
        results_dir = "results"
        
        if not os.path.exists(results_dir):
            self.dashboard.console.print("[yellow]No hay resultados anteriores.[/yellow]")
            self.wait_for_continue()
            return
        
        files = os.listdir(results_dir)
        
        if not files:
            self.dashboard.console.print("[yellow]No hay archivos de resultados.[/yellow]")
            self.wait_for_continue()
            return
        
        self.dashboard.console.print(f"\n[bold cyan]📁 Archivos en {results_dir}:[/bold cyan]\n")
        
        for file in sorted(files):
            self.dashboard.console.print(f"  📄 {file}")
        
        self.dashboard.console.print()
        
        choice = self.dashboard.console.input("[cyan]¿Deseas abrir el directorio? (s/n): [/cyan]").strip().lower()
        
        if choice == 's':
            self.open_results_directory()
    
    def wait_for_continue(self):
        self.dashboard.console.input("\n[cyan]Presiona Enter para continuar...[/cyan]")

def main():
    app = FFTDashboardApp()
    app.run()

if __name__ == "__main__":
    main()