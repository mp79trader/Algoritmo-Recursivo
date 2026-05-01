import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app_simple import FFTDashboardApp

if __name__ == "__main__":
    app = FFTDashboardApp()
    
    # Execute demo directly
    print("Executing dashboard demo...\n")
    
    # Analyze MNQ=F
    ticker = "MNQ=F"
    
    print(f"Analyzing {ticker}...\n")
    
    app.perform_analysis(ticker)
    
    print("\n[bold green]Demo completed![/bold green]")