import numpy as np
from typing import Tuple

def next_power_of_2(n: int) -> int:
    return 1 if n == 0 else 2 ** (n - 1).bit_length()

def fft_recursive(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x).flatten()
    n = len(x)
    
    if n <= 1:
        return x.astype(complex)
    
    target_n = next_power_of_2(n)
    if n != target_n:
        x = np.pad(x, (0, target_n - n), 'constant')
        n = target_n
    
    even = fft_recursive(x[::2])
    odd = fft_recursive(x[1::2])
    
    k = np.arange(n // 2)
    factor = np.exp(-2j * np.pi * k / n)
    T = factor * odd
    
    return np.concatenate([even + T, even - T])

def ifft_recursive(x: np.ndarray) -> np.ndarray:
    n = len(x)
    return fft_recursive(x.conj()).conj() / n

def fft_shift(fft_result: np.ndarray) -> np.ndarray:
    n = len(fft_result)
    return np.concatenate([fft_result[n//2:], fft_result[:n//2]])

def get_frequencies(n: int, sample_rate: float) -> np.ndarray:
    return np.fft.fftfreq(n, d=1/sample_rate)

def filter_frequencies(fft_result: np.ndarray, frequencies: np.ndarray, 
                       threshold: float = 0.05) -> np.ndarray:
    magnitude = np.abs(fft_result)
    max_magnitude = np.max(magnitude)
    filtered = fft_result.copy()
    filtered[magnitude < threshold * max_magnitude] = 0
    return filtered

def extract_top_components(fft_result: np.ndarray, n_components: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    magnitude = np.abs(fft_result)
    indices = np.argsort(magnitude)[-n_components:][::-1]
    return fft_result[indices], indices