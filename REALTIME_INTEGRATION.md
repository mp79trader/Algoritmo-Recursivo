# Real-Time Data Integration Guide

## Overview

This project now supports multiple data sources for real-time and historical market data:

- **Yahoo Finance (yfinance)**: Default source, ~15min delayed data
- **NinjaTrader**: Real-time data via file exchange
- **MetaTrader 5 (MT5)**: Real-time data via API (requires MetaTrader5 package)

## Quick Start

### 1. Configure Data Source

**Terminal:**
```bash
python app.py
# Select: ⚙️ Configuración
# Choose your preferred data source
```

**Web GUI:**
- Navigate to Settings page
- Select Real-time and Historical data sources
- Configure platform-specific settings

### 2. Symbol Mapping

Each platform uses different symbol names. Configure mappings in Settings:

| Internal | Yahoo Finance | NinjaTrader | MetaTrader 5 |
|----------|--------------|-------------|--------------|
| MNQ      | MNQ=F        | MNQ         | NQ-MAR26     |
| MES      | MES=F        | MES         | ES-MAR26     |
| NQ       | NQ=F         | NQ          | NQ           |
| ES       | ES=F         | ES          | ES           |

## NinjaTrader Integration

### Setup

1. **Install NinjaTrader Connector:**
   - Copy `Conector_Ninja/ConnectorFFT.cs` to your NinjaTrader strategies folder
   - Compile in NinjaTrader

2. **Configure Exchange Directory:**
   - Default: `C:\QuantumGAN\Exchange`
   - Change in Settings if needed

3. **Start Connector in NinjaTrader:**
   - Apply ConnectorFFT strategy to your chart
   - Connector will export data to exchange directory

### How It Works

The connector exchanges data via CSV files:

**Files Created:**
- `data_SYMBOL_TIMEFRAME.csv` - Market data (OHLCV)
- `positions.csv` - Current positions
- `account.csv` - Account information
- `commands.txt` - Trading commands (read by NT)

**Data Flow:**
```
NinjaTrader → CSV Files → Python Application → Analysis → Commands → NinjaTrader
```

### File Format

**data_MNQ_1min.csv:**
```csv
Time,Open,High,Low,Close,Volume
2026-01-19 09:30:00,21500.25,21505.50,21498.00,21502.00,1250
```

**positions.csv:**
```csv
Symbol,MarketPosition,Quantity,AveragePrice,UnrealizedPnL,SL,TP
MNQ 03-26,Long,1,21500.00,125.50,21450.00,21600.00
```

## MetaTrader 5 Integration

### Setup

1. **Install MT5 Package:**
```bash
pip install MetaTrader5
```

2. **Enable Algo Trading in MT5:**
   - Tools → Options → Expert Advisors
   - Check "Allow automated trading"

3. **Configure Connection:**
   - In Settings, set MT5 host/port if needed
   - Default: localhost:8002

### Usage

```python
from mt5_connector import MT5Connector

# Connect
connector = MT5Connector()
connector.connect()

# Get data
df = connector.fetch_data('NQ', timeframe='1min', bars=200)

# Get current price
price = connector.get_current_price('NQ')
print(price)  # {'bid': 21500.25, 'ask': 21500.50, ...}

# Send order
result = connector.send_order('NQ', 'BUY', volume=0.1, sl=21450, tp=21600)
```

## API Configuration Endpoints

### Get Data Sources
```bash
GET /api/config/datasources
```

### Set Data Source
```bash
POST /api/config/datasource
Content-Type: application/json

{
  "type": "realtime",  # or "historical"
  "source": "ninjatrader"  # or "yfinance", "mt5"
}
```

### Get Symbol Mappings
```bash
GET /api/config/symbols/mappings
```

### Add Symbol Mapping
```bash
POST /api/config/symbols/mapping
Content-Type: application/json

{
  "internal_symbol": "MNQ",
  "source": "ninjatrader",
  "external_symbol": "MNQ"
}
```

### Configure NinjaTrader
```bash
POST /api/config/ninja
Content-Type: application/json

{
  "exchange_dir": "C:\\QuantumGAN\\Exchange"
}
```

## Configuration File

Settings are stored in `data_source_config.json`:

```json
{
  "realtime_source": "ninjatrader",
  "historical_source": "yfinance",
  "ninja_exchange_dir": "C:\\QuantumGAN\\Exchange",
  "mt5_host": "localhost",
  "mt5_port": 8002,
  "symbol_mappings": {
    "MNQ": {
      "yfinance": "MNQ=F",
      "ninjatrader": "MNQ",
      "mt5": "NQ-MAR26"
    }
  }
}
```

## Usage Examples

### Python Script

```python
from market_data import MarketData
from data_source_config import DataSourceConfig

# Use configured source
data = MarketData('MNQ')
market_data = data.fetch_data(period='1d', interval='1min')

# Override source
data_ninja = MarketData('MNQ', data_source='ninjatrader')
realtime_data = data_ninja.fetch_data(interval='1min')

# Get realtime price
price = data.get_realtime_price()
print(f"Current price: {price}")
```

### Terminal

```bash
# Run analysis with configured source
python app.py

# Analyze with specific source
# (Edit market_data instantiation to pass data_source parameter)
```

## Troubleshooting

### NinjaTrader Issues

**No data files found:**
- Verify ConnectorFFT is running on a chart
- Check exchange directory path in Settings
- Ensure chart has enough bars loaded

**Symbol not matching:**
- Update symbol mappings in Settings
- Check NinjaTrader instrument name
- Verify file naming: `data_SYMBOL_TIMEFRAME.csv`

### MT5 Issues

**Cannot connect:**
- Ensure MT5 terminal is running
- Enable algo trading in MT5 options
- Check if MetaTrader5 package is installed

**Symbol not found:**
- Use MT5 symbol format exactly
- Check symbol availability in Market Watch
- Update symbol mappings

### General Issues

**Import errors:**
```bash
# Install missing packages
pip install MetaTrader5  # For MT5 support
```

**Configuration not saving:**
- Check file permissions
- Verify JSON syntax in config file
- Restart application after manual edits

## Best Practices

1. **Use real-time sources for live signals** (NinjaTrader/MT5)
2. **Use historical sources for analysis** (yfinance for large datasets)
3. **Keep symbol mappings updated** for all platforms you use
4. **Test connections** before live trading
5. **Monitor exchange directory** for NinjaTrader integration
6. **Backup configuration file** before making changes

## Next Steps

- Configure your preferred data source in Settings
- Set up symbol mappings for your instruments
- Test connection with a simple analysis
- Monitor data quality and latency
- Adjust settings as needed for your trading style
