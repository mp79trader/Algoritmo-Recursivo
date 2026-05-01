from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
import time

class TerminalDashboardASCII:
    def __init__(self):
        self.console = Console()
        
    def show_header(self):
        header_text = Text("ALGORITMO FFT RECURSIVO", style="bold cyan")
        sub_text = Text("Para Prediccion de Mercado - Futuros y Acciones", style="italic white")
        
        header = Panel(
            sub_text,
            title=header_text,
            title_align="center",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(header)
    
    def show_main_menu(self):
        self.show_header()
        
        self.console.print("\n[bold cyan]MENU PRINCIPAL[/bold cyan]\n")
        self.console.print("1. Analizar un unico instrumento (Futuro/Accion)")
        self.console.print("2. Analisis comparativo de multiples futuros")
        self.console.print("3. Lista de simbolos disponibles")
        self.console.print("4. Configuracion")
        self.console.print("5. Ver resultados anteriores")
        self.console.print("6. Salir\n")
        
        choice = input("Selecciona una opcion (1-6): ").strip()
        
        menu_map = {
            "1": "Analizar unico",
            "2": "Comparativo",
            "3": "Simbolos",
            "4": "Config",
            "5": "Resultados",
            "6": "Salir"
        }
        
        return menu_map.get(choice, "Salir")
    
    def show_progress(self, steps):
        for i, step in enumerate(steps, 1):
            self.console.print(f"[{i}/{len(steps)}] {step['desc']}")
            if step['action']:
                try:
                    step['action']()
                except Exception as e:
                    self.console.print(f"[red]Error: {str(e)}[/red]")
            time.sleep(0.2)
        
        self.console.print("\n[green]Process completed successfully![/green]\n")
    
    def show_symbol_info_table(self, symbol_info, data):
        table = Table(title="Informacion del Instrumento", show_header=True, header_style="bold magenta")
        table.add_column("Propiedad", style="cyan", width=20)
        table.add_column("Valor", style="white")
        
        table.add_row("Simbolo", symbol_info['ticker'])
        table.add_row("Nombre", symbol_info['name'])
        table.add_row("Tipo", symbol_info['type'])
        table.add_row("Puntos de datos", str(len(data['close'])))
        table.add_row("Precio Minimo", f"${float(data['close'].min()):.2f}")
        table.add_row("Precio Maximo", f"${float(data['close'].max()):.2f}")
        table.add_row("Precio Actual", f"${float(data['close'][-1]):.2f}")
        
        self.console.print(table)
    
    def show_prediction_table(self, prediction, config):
        table = Table(title=f"Predicciones para Proximos {config['prediction_days']} Dias", 
                     show_header=True, header_style="bold green")
        table.add_column("Dia", style="cyan", width=8)
        table.add_column("Precio Predicho", style="yellow", width=15)
        table.add_column("Cambio %", style="white", width=10)
        
        from datetime import datetime, timedelta
        
        today = datetime.now()
        last_price = config['last_price']
        
        for i in range(0, len(prediction), max(1, len(prediction)//15)):
            day_num = i + 1
            pred_price = prediction[i] * config['std'] + config['mean']
            change_pct = ((pred_price - last_price) / last_price * 100)
            change_pct = float(change_pct)
            
            change_style = "green" if change_pct >= 0 else "red"
            
            table.add_row(
                str(day_num),
                f"${pred_price:,.2f}",
                f"[{change_style}]{change_pct:+.2f}%[/]"
            )
        
        self.console.print(table)
    
    def show_trend_analysis(self, analysis):
        trend = analysis['trend']
        trend_style = "bold green" if trend['direction'] == 'UP' else "bold red"
        
        trend_table = Table(title="Analisis de Tendencia", show_header=True, header_style="bold yellow")
        trend_table.add_column("Indicador", style="cyan", width=20)
        trend_table.add_column("Valor", style="white")
        
        trend_table.add_row("Direccion", f"[{trend_style}]{trend['direction']}[/]")
        trend_table.add_row("Fuerza", f"{trend['strength']:.2f}")
        trend_table.add_row("Componentes baja frecuencia", str(trend['low_freq_components']))
        
        self.console.print(trend_table)
    
    def show_cycles_table(self, cycles_data):
        table = Table(title="Analisis de Ciclos Detectados", show_header=True, header_style="bold blue")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Periodo (dias)", style="white", width=15)
        table.add_column("Frecuencia", style="white", width=15)
        table.add_column("Magnitud", style="yellow", width=12)
        
        for i, cycle in enumerate(cycles_data['cycles'][:10], 1):
            if cycle['period'] < 1000:
                table.add_row(
                    str(i),
                    f"{cycle['period']:.2f}",
                    f"{cycle['frequency']:.4f}",
                    f"{cycle['magnitude']:.4f}"
                )
        
        self.console.print(table)
        
        if cycles_data['dominant_cycle']:
            dom = cycles_data['dominant_cycle']
            dom_panel = Panel(
                f"Ciclo Dominante: Periodo = {dom['period']:.2f} dias, Frecuencia = {dom['frequency']:.4f}",
                title="Ciclo Principal",
                border_style="bright_yellow"
            )
            self.console.print(dom_panel)
    
    def show_spectral_summary(self, spectral):
        max_mag = spectral['magnitude'].max()
        mean_mag = spectral['magnitude'].mean()
        top_freq = spectral['top_frequencies'][0] if len(spectral['top_frequencies']) > 0 else 0
        
        table = Table(title="Resumen Espectral", show_header=True, header_style="bold magenta")
        table.add_column("Metrica", style="cyan", width=25)
        table.add_column("Valor", style="white")
        
        table.add_row("Magnitud Maxima", f"{max_mag:.4f}")
        table.add_row("Magnitud Promedio", f"{mean_mag:.4f}")
        table.add_row("Frecuencia Dominante", f"{top_freq:.4f}")
        table.add_row("Componentes Analizados", str(len(spectral['fft'])))
        
        self.console.print(table)
    
    def show_confidence_meter(self, confidence):
        bar_width = 50
        filled = int(confidence * bar_width)
        
        color = "green" if confidence >= 0.7 else "yellow" if confidence >= 0.4 else "red"
        
        bar = "[" + color + "]" + "#" * filled + "[white]" + "-" * (bar_width - filled) + "[/]"
        
        panel = Panel(
            f"{bar}\n\n[color]{confidence:.2%}[/] de confianza en el modelo",
            title="Confianza del Modelo",
            border_style=color
        )
        self.console.print(panel)
    
    def show_summary_dashboard(self, symbol_info, analysis, prediction, data):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main", size=20),
            Layout(name="details", size=15)
        )
        
        header_text = Text(f"Resultados: {symbol_info['ticker']}", style="bold cyan")
        layout["header"].update(Panel(header_text, border_style="bright_blue"))
        
        summary = Table.grid()
        summary.add_column(style="cyan", width=20)
        summary.add_column(style="white")
        
        summary.add_row("Simbolo:", symbol_info['ticker'])
        summary.add_row("Nombre:", symbol_info['name'])
        summary.add_row("Tipo:", symbol_info['type'])
        summary.add_row("Tendencia:", 
                       f"[{'green' if analysis['trend']['direction'] == 'UP' else 'red'}]{analysis['trend']['direction']}[/]")
        summary.add_row("Confianza:", f"{analysis['prediction']['confidence']:.2%}")
        summary.add_row("Ciclo Dominante:", 
                       f"{analysis['cycles']['dominant_cycle']['period']:.1f} dias" if analysis['cycles']['dominant_cycle'] else "N/A")
        
        layout["main"].update(Panel(summary, title="Resumen", border_style="green"))
        
        prediction_summary = Table.grid()
        prediction_summary.add_column(style="cyan", width=25)
        prediction_summary.add_column(style="yellow")
        
        pred_start = prediction[0] * data['close'].std() + data['close'].mean()
        pred_end = prediction[-1] * data['close'].std() + data['close'].mean()
        change_pct = ((pred_end - pred_start) / pred_start * 100)
        
        prediction_summary.add_row("Precio Inicial Predicho:", f"${pred_start:,.2f}")
        prediction_summary.add_row("Precio Final Predicho:", f"${pred_end:,.2f}")
        prediction_summary.add_row("Cambio Esperado:", 
                                   f"[{'green' if change_pct >= 0 else 'red'}]{change_pct:+.2f}%[/]")
        
        layout["details"].update(Panel(prediction_summary, title="Prediccion", border_style="yellow"))
        
        self.console.print(layout)
    
    def show_visualization_menu(self, results_files):
        self.console.print("\n[bold cyan]Visualizaciones Generadas:[/bold cyan]\n")
        
        for i, file_path in enumerate(results_files, 1):
            filename = file_path.split('/')[-1]
            self.console.print(f"  {i}. {filename}")
        
        self.console.print()
        self.console.print("Opciones:")
        self.console.print("1. Ver todas las visualizaciones")
        self.console.print("2. Abrir directorio de resultados")
        self.console.print("3. Volver al menu principal\n")
        
        choice = input("Selecciona una opcion (1-3): ").strip()
        
        choice_map = {
            "1": "Ver todas",
            "2": "Abrir directorio",
            "3": "Volver"
        }
        
        return choice_map.get(choice, "Volver")
    
    def open_visualizations(self, results_files):
        import os
        import platform
        import subprocess
        
        if len(results_files) == 0:
            self.console.print("[yellow]No hay visualizaciones disponibles.[/yellow]")
            return
        
        self.console.print("[cyan]Abriendo visualizaciones...[/cyan]\n")
        
        for file_path in results_files:
            self.console.print(f" {file_path}")
            try:
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':
                    subprocess.call(['open', file_path])
                else:
                    subprocess.call(['xdg-open', file_path])
                time.sleep(0.5)
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
        
        self.console.print("\n[green]Visualizaciones abiertas[/green]")
    
    def show_config_menu(self):
        from config import Config
        
        table = Table(title="Configuracion Actual", show_header=True, header_style="bold magenta")
        table.add_column("Parametro", style="cyan", width=25)
        table.add_column("Valor", style="white", width=15)
        table.add_column("Descripcion", style="dim")
        
        table.add_row("TICKER", Config.TICKER, "Simbolo por defecto")
        table.add_row("PERIOD", Config.PERIOD, "Periodo de datos")
        table.add_row("INTERVAL", Config.INTERVAL, "Intervalo de tiempo")
        table.add_row("PREDICTION_DAYS", str(Config.PREDICTION_DAYS), "Dias a predecir")
        table.add_row("FFT_COMPONENTS", str(Config.FFT_COMPONENTS), "Componentes FFT")
        table.add_row("FREQUENCY_THRESHOLD", str(Config.FREQUENCY_THRESHOLD), "Umbral de frecuencia")
        
        self.console.print(table)
    
    def show_available_symbols(self):
        from market_data import MarketData
        from config import Config
        
        symbols = MarketData.get_available_symbols()
        
        self.console.print("\n[bold cyan]FUTUROS DE INDICES DISPONIBLES:[/bold cyan]\n")
        
        futures_table = Table(show_header=True, header_style="bold green")
        futures_table.add_column("Simbolo", style="cyan", width=10)
        futures_table.add_column("Descripcion", style="white")
        futures_table.add_column("Tipo", style="yellow", width=15)
        
        for sym in symbols['futures']:
            futures_table.add_row(sym, Config.FUTURES_SYMBOLS[sym], "Micro/E-mini")
        
        self.console.print(futures_table)
        
        self.console.print("\n[bold cyan]ACCIONES DISPONIBLES:[/bold cyan]\n")
        
        stocks_table = Table(show_header=True, header_style="bold green")
        stocks_table.add_column("Simbolo", style="cyan", width=10)
        stocks_table.add_column("Descripcion", style="white")
        
        for sym in symbols['stocks']:
            stocks_table.add_row(sym, Config.STOCK_SYMBOLS[sym])
        
        self.console.print(stocks_table)