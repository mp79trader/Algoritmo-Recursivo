from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.columns import Columns
from questionary import select, confirm
import time

class TerminalDashboard:
    def __init__(self):
        self.console = Console()
        
    def show_header(self):
        header_text = Text("ALGORITMO FFT RECURSIVO", style="bold cyan")
        sub_text = Text("Para Predicción de Mercado - Futuros y Acciones", style="italic white")
        
        header = Panel(
            Align.center(sub_text),
            title=header_text,
            title_align="center",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(header)
    
    def show_main_menu(self):
        self.console.clear()
        self.show_header()
        
        choices = [
            "📊 Analizar un único instrumento (Futuro/Acción)",
            "📈 Análisis comparativo de múltiples futuros",
            "🌐 Abrir interfaz web (GUI)",
            "📋 Lista de símbolos disponibles",
            "⚙️ Configuración",
            "📊 Ver resultados anteriores",
            "🚪 Salir"
        ]
        
        from questionary import select
        choice = select(
            "¿Qué deseas hacer?",
            choices=choices,
            qmark="➤",
            use_indicator=True,
            style=None
        ).ask()
        
        if not choice:
            return "🚪 Salir"
            
        return choice
    
    def show_symbol_selection(self, symbol_type="all"):
        from market_data import MarketData
        from config import Config
        
        symbols = MarketData.get_available_symbols()
        
        if symbol_type == "futures":
            choices = [f"{sym} - {Config.FUTURES_SYMBOLS[sym]}" for sym in symbols['futures']]
        elif symbol_type == "stocks":
            choices = [f"{sym} - {Config.STOCK_SYMBOLS[sym]}" for sym in symbols['stocks']]
        else:
            all_symbols = []
            for sym in symbols['futures']:
                all_symbols.append(f"FUTURO: {sym} - {Config.FUTURES_SYMBOLS[sym]}")
            for sym in symbols['stocks']:
                all_symbols.append(f"ACCION: {sym} - {Config.STOCK_SYMBOLS[sym]}")
            choices = all_symbols
        
        choice = select(
            "Selecciona un símbolo:",
            choices=choices,
            qmark="➤"
        ).ask()
        
        return choice.split(":")[-1].strip().split(" - ")[0]
    
    def show_progress(self, steps):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Procesando...", total=len(steps))
            for step in steps:
                progress.update(task, description=step['desc'])
                time.sleep(0.3)
                if step['action']:
                    step['action']()
                progress.advance(task)
    
    def show_symbol_info_table(self, symbol_info, data):
        table = Table(title="Información del Instrumento", show_header=True, header_style="bold magenta")
        table.add_column("Propiedad", style="cyan", width=20)
        table.add_column("Valor", style="white")
        
        table.add_row("Símbolo", symbol_info['ticker'])
        table.add_row("Nombre", symbol_info['name'])
        table.add_row("Tipo", symbol_info['type'])
        table.add_row("Puntos de datos", str(len(data['close'])))
        table.add_row("Precio Mínimo", f"${data['close'].min():.2f}")
        table.add_row("Precio Máximo", f"${data['close'].max():.2f}")
        table.add_row("Precio Actual", f"${data['close'][-1]:.2f}")
        
        self.console.print(table)
    
    def show_prediction_table(self, prediction, config):
        table = Table(title="Predicciones para Próximos " + str(config['prediction_days']) + " Días", 
                     show_header=True, header_style="bold green")
        table.add_column("Día", style="cyan", width=8)
        table.add_column("Fecha", style="white", width=15)
        table.add_column("Precio Predicho", style="yellow", width=15)
        table.add_column("Cambio %", style="white", width=10)
        
        import numpy as np
        import pandas as pd
        from datetime import datetime, timedelta
        
        today = datetime.now()
        
        for i in range(0, len(prediction), max(1, len(prediction)//15)):
            day_num = i + 1
            pred_date = today + timedelta(days=day_num)
            pred_price = prediction[i] * config['std'] + config['mean']
            change_pct = ((pred_price - config['last_price']) / config['last_price'] * 100)
            
            change_style = "green" if change_pct >= 0 else "red"
            
            table.add_row(
                str(day_num),
                pred_date.strftime("%Y-%m-%d"),
                f"${pred_price:,.2f}",
                f"[{change_style}]{change_pct:+.2f}%[/]"
            )
        
        self.console.print(table)
    
    def show_trend_analysis(self, analysis):
        trend = analysis['trend']
        trend_style = "bold green" if trend['direction'] == 'UP' else "bold red"
        
        trend_table = Table(title="Análisis de Tendencia", show_header=True, header_style="bold yellow")
        trend_table.add_column("Indicador", style="cyan", width=20)
        trend_table.add_column("Valor", style="white")
        
        trend_table.add_row("Dirección", f"[{trend_style}]{trend['direction']}[/]")
        trend_table.add_row("Fuerza", f"{trend['strength']:.2f}")
        trend_table.add_row("Componentes baja frecuencia", str(trend['low_freq_components']))
        
        self.console.print(trend_table)
    
    def show_cycles_table(self, cycles_data):
        table = Table(title="Análisis de Ciclos Detectados", show_header=True, header_style="bold blue")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Período (días)", style="white", width=15)
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
                f"Ciclo Dominante: Período = {dom['period']:.2f} días, Frecuencia = {dom['frequency']:.4f}",
                title="📊 Ciclo Principal",
                border_style="bright_yellow"
            )
            self.console.print(dom_panel)
    
    def show_spectral_summary(self, spectral):
        max_mag = spectral['magnitude'].max()
        mean_mag = spectral['magnitude'].mean()
        top_freq = spectral['top_frequencies'][0] if len(spectral['top_frequencies']) > 0 else 0
        
        table = Table(title="Resumen Espectral", show_header=True, header_style="bold magenta")
        table.add_column("Métrica", style="cyan", width=25)
        table.add_column("Valor", style="white")
        
        table.add_row("Magnitud Máxima", f"{max_mag:.4f}")
        table.add_row("Magnitud Promedio", f"{mean_mag:.4f}")
        table.add_row("Frecuencia Dominante", f"{top_freq:.4f}")
        table.add_row("Componentes Analizados", str(len(spectral['fft'])))
        
        self.console.print(table)
    
    def show_confidence_meter(self, confidence):
        bar_width = 50
        filled = int(confidence * bar_width)
        
        color = "green" if confidence >= 0.7 else "yellow" if confidence >= 0.4 else "red"
        
        bar = "[" + color + "]" + "█" * filled + "[white]" + "░" * (bar_width - filled) + "[/]"
        
        panel = Panel(
            f"{bar}\n\n[color]{confidence:.2%}[/] de confianza en el modelo",
            title="📈 Confianza del Modelo",
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
        
        header_text = Text(f"📊 Resultados: {symbol_info['ticker']}", style="bold cyan")
        layout["header"].update(Panel(header_text, border_style="bright_blue"))
        
        summary = Table.grid()
        summary.add_column(style="cyan", width=20)
        summary.add_column(style="white")
        
        summary.add_row("Símbolo:", symbol_info['ticker'])
        summary.add_row("Nombre:", symbol_info['name'])
        summary.add_row("Tipo:", symbol_info['type'])
        summary.add_row("Tendencia:", 
                       f"[{'green' if analysis['trend']['direction'] == 'UP' else 'red'}]{analysis['trend']['direction']}[/]")
        summary.add_row("Confianza:", f"{analysis['prediction']['confidence']:.2%}")
        summary.add_row("Ciclo Dominante:", 
                       f"{analysis['cycles']['dominant_cycle']['period']:.1f} días" if analysis['cycles']['dominant_cycle'] else "N/A")
        
        layout["main"].update(Panel(summary, title="📋 Resumen", border_style="green"))
        
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
        
        layout["details"].update(Panel(prediction_summary, title="🔮 Predicción", border_style="yellow"))
        
        self.console.print(layout)
    
    def show_visualization_menu(self, results_files):
        self.console.print("\n[bold cyan]📊 Visualizaciones Generadas:[/bold cyan]\n")
        
        for i, file_path in enumerate(results_files, 1):
            filename = file_path.split('/')[-1]
            self.console.print(f"  {i}. 📄 {filename}")
        
        self.console.print()
        
        choice = select(
            "¿Qué deseas hacer?",
            choices=[
                "👀 Ver todas las visualizaciones",
                "🖼️ Seleccionar una visualización específica",
                "💾 Abrir directorio de resultados",
                "⬅️ Volver al menú principal"
            ],
            qmark="➤"
        ).ask()
        
        return choice
    
    def open_visualizations(self, results_files):
        import os
        import platform
        import subprocess
        
        if len(results_files) == 0:
            self.console.print("[yellow]No hay visualizaciones disponibles.[/yellow]")
            return
        
        self.console.print("[cyan]Abriendo visualizaciones...[/cyan]\n")
        
        for file_path in results_files:
            self.console.print(f"📄 {file_path}")
            if platform.system() == 'Windows':
                os.startfile(os.path.abspath(file_path))
            elif platform.system() == 'Darwin':
                subprocess.call(['open', file_path])
            else:
                subprocess.call(['xdg-open', file_path])
            time.sleep(0.5)
        
        self.console.print("\n[green]✓ Visualizaciones abiertas[/green]")
    
    def show_config_menu(self):
        from config import Config
        from data_source_config import DataSourceConfig
        
        ds_config = DataSourceConfig()
        
        table = Table(title="Configuración Actual", show_header=True, header_style="bold magenta")
        table.add_column("Parámetro", style="cyan", width=25)
        table.add_column("Valor", style="white", width=20)
        table.add_column("Descripción", style="dim")
        
        # General settings
        table.add_row("TICKER", Config.TICKER, "Símbolo por defecto")
        table.add_row("PERIOD", Config.PERIOD, "Período de datos")
        table.add_row("INTERVAL", Config.INTERVAL, "Intervalo de tiempo")
        table.add_row("PREDICTION_DAYS", str(Config.PREDICTION_DAYS), "Días a predecir")
        table.add_row("FFT_COMPONENTS", str(Config.FFT_COMPONENTS), "Componentes FFT")
        table.add_row("FREQUENCY_THRESHOLD", str(Config.FREQUENCY_THRESHOLD), "Umbral de frecuencia")
        
        # Data source settings
        table.add_row("", "", "", style="dim")
        table.add_row("REALTIME_SOURCE", ds_config.get_realtime_source(), "Fuente de datos en tiempo real")
        table.add_row("HISTORICAL_SOURCE", ds_config.get_historical_source(), "Fuente de datos históricos")
        
        self.console.print(table)
    
    def show_datasource_config(self):
        """Show data source configuration options"""
        from data_source_config import DataSourceConfig
        
        ds_config = DataSourceConfig()
        
        self.console.print("\n[bold cyan]⚙️ Configuración de Fuentes de Datos:[/bold cyan]\n")
        
        from questionary import select
        choice = select(
            "¿Qué deseas configurar?",
            choices=[
                "🔄 Cambiar fuente de datos en tiempo real",
                "📊 Cambiar fuente de datos históricos",
                "🗺️ Ver mapeo de símbolos",
                "📁 Configurar directorio NinjaTrader",
                "⬅️ Volver"
            ],
            qmark="➤"
        ).ask()
        
        if "tiempo real" in choice:
            source = self.show_datasource_selection("realtime")
            if source:
                ds_config.set_realtime_source(source)
                self.console.print(f"\n[green]✓ Fuente de tiempo real configurada: {source}[/green]")
        
        elif "históricos" in choice:
            source = self.show_datasource_selection("historical")
            if source:
                ds_config.set_historical_source(source)
                self.console.print(f"\n[green]✓ Fuente histórica configurada: {source}[/green]")
        
        elif "mapeo" in choice:
            self.show_symbol_mappings()
        
        elif "NinjaTrader" in choice:
            ninja_dir = self.console.input("\n[cyan]Directorio de intercambio NinjaTrader: [/cyan]")
            if ninja_dir:
                ds_config.set_ninja_exchange_dir(ninja_dir)
                self.console.print(f"\n[green]✓ Directorio NinjaTrader configurado: {ninja_dir}[/green]")
    
    def show_datasource_selection(self, source_type="realtime"):
        from data_source_config import DataSourceConfig
        
        self.console.print(f"\n[bold cyan]Seleccionar fuente de datos {source_type}:[/bold cyan]\n")
        
        from questionary import select
        choice = select(
            f"Fuente para {source_type}:",
            choices=[
                "📡 Yahoo Finance (yfinance) - Datos diferidos ~15min",
                "⚡ NinjaTrader - Datos en tiempo real",
                "🌐 MetaTrader 5 (MT5) - Datos en tiempo real"
            ],
            qmark="➤"
        ).ask()
        
        if "Yahoo Finance" in choice:
            return DataSourceConfig.SOURCE_YFINANCE
        elif "NinjaTrader" in choice:
            return DataSourceConfig.SOURCE_NINJATRADER
        elif "MetaTrader" in choice:
            return DataSourceConfig.SOURCE_MT5
        
        return None
    
    def show_symbol_mappings(self):
        from data_source_config import DataSourceConfig
        
        ds_config = DataSourceConfig()
        mappings = ds_config.get_all_mappings()
        
        self.console.print("\n[bold cyan]🗺️ Mapeo de Símbolos:[/bold cyan]\n")
        
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Símbolo Interno", style="cyan", width=15)
        table.add_column("Yahoo Finance", style="white", width=15)
        table.add_column("NinjaTrader", style="yellow", width=15)
        table.add_column("MetaTrader 5", style="blue", width=15)
        
        for internal_sym, sources in mappings.items():
            table.add_row(
                internal_sym,
                sources.get(DataSourceConfig.SOURCE_YFINANCE, "-"),
                sources.get(DataSourceConfig.SOURCE_NINJATRADER, "-"),
                sources.get(DataSourceConfig.SOURCE_MT5, "-")
            )
        
        self.console.print(table)
    
    def show_available_symbols(self):
        from market_data import MarketData
        from config import Config
        
        symbols = MarketData.get_available_symbols()
        
        self.console.print("\n[bold cyan]📊 FUTUROS DE ÍNDICES DISPONIBLES:[/bold cyan]\n")
        
        futures_table = Table(show_header=True, header_style="bold green")
        futures_table.add_column("Símbolo", style="cyan", width=10)
        futures_table.add_column("Descripción", style="white")
        futures_table.add_column("Tipo", style="yellow", width=15)
        
        for sym in symbols['futures']:
            # Verificar si el símbolo está en Config.FUTURES_SYMBOLS
            if sym in Config.FUTURES_SYMBOLS:
                futures_table.add_row(sym, Config.FUTURES_SYMBOLS[sym], "Micro/E-mini")
            else:
                # Símbolo no mapeado en Config, mostrar con nombre genérico
                futures_table.add_row(sym, f"Futuro ({sym})", "Disponible en Plataforma")
        
        self.console.print(futures_table)
        
        self.console.print("\n[bold cyan]📊 ACCIONES DISPONIBLES:[/bold cyan]\n")
        
        stocks_table = Table(show_header=True, header_style="bold green")
        stocks_table.add_column("Símbolo", style="cyan", width=10)
        stocks_table.add_column("Descripción", style="white")
        
        for sym in symbols['stocks']:
            # Verificar si el símbolo está en Config.STOCK_SYMBOLS
            if sym in Config.STOCK_SYMBOLS:
                stocks_table.add_row(sym, Config.STOCK_SYMBOLS[sym])
            else:
                # Acción no mapeada
                stocks_table.add_row(sym, f"Acción ({sym})")
        
        self.console.print(stocks_table)