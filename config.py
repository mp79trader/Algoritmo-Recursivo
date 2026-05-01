import os

class Config:
    TICKER = "MNQ=F"
    PERIOD = "2y"
    INTERVAL = "1d"
    PREDICTION_DAYS = 30
    SAMPLE_RATE = 252
    
    FFT_COMPONENTS = 10
    FREQUENCY_THRESHOLD = 0.05
    
    OUTPUT_DIR = "results"
    VISUALIZATION_DPI = 150
    
    FUTURES_SYMBOLS = {
        'MNQ=F': 'Micro Nasdaq-100',
        'MES=F': 'Micro E-mini S&P 500',
        'MYM=F': 'Micro Dow Jones',
        'NQ=F': 'E-mini Nasdaq-100',
        'ES=F': 'E-mini S&P 500',
        'YM=F': 'E-mini Dow Jones',
        'RTY=F': 'E-mini Russell 2000',
        'M2K=F': 'Micro Russell 2000'
    }
    
    STOCK_SYMBOLS = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corporation',
        'TSLA': 'Tesla Inc.',
        'AMZN': 'Amazon.com Inc.',
        'META': 'Meta Platforms Inc.',
        'NVDA': 'NVIDIA Corporation'
    }
    
    @classmethod
    def get_symbol_name(cls, ticker: str) -> str:
        if ticker in cls.FUTURES_SYMBOLS:
            return f"{cls.FUTURES_SYMBOLS[ticker]} (Futuro)"
        elif ticker in cls.STOCK_SYMBOLS:
            return cls.STOCK_SYMBOLS[ticker]
        else:
            return ticker
    
    @classmethod
    def is_future(cls, ticker: str) -> bool:
        return ticker in cls.FUTURES_SYMBOLS
    
    @classmethod
    def create_output_dir(cls):
        if not os.path.exists(cls.OUTPUT_DIR):
            os.makedirs(cls.OUTPUT_DIR)