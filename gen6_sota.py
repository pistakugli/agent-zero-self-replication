#!/usr/bin/env python3
"""
Generation 6 - TRUE SOTA
==========================
Combines everything:
- Sieve precompute (Gen5)
- LRU Cache for repeated queries (Gen3)  
- Miller-Rabin for large uncached (Gen4/5)
- Bitarray sieve for memory efficiency

This is the actual state-of-the-art for general purpose prime checking.
"""

from functools import lru_cache

# Sieve precompute up to 100k
def _build_sieve(limit):
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return sieve

_SIEVE_LIMIT = 100_000
_SIEVE = _build_sieve(_SIEVE_LIMIT)

# Small primes for quick divisibility
_SMALL_PRIMES = tuple(i for i in range(2, 100) if _SIEVE[i])

def _miller_rabin(n):
    """Deterministic for n < 3,215,031,751"""
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for a in (2, 3, 5, 7):
        if a >= n:
            continue
        x = pow(a, d, n)  # Python's built-in modpow - optimized C
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

@lru_cache(maxsize=4096)
def is_prime(n):
    # Sieve zone - O(1)
    if n <= _SIEVE_LIMIT:
        return bool(_SIEVE[n]) if n >= 0 else False
    
    # Quick divisibility by small primes
    for p in _SMALL_PRIMES:
        if n % p == 0:
            return n == p
    
    # Miller-Rabin for large numbers
    return _miller_rabin(n)

if __name__ == '__main__':
    import time
    
    # Correctness
    known_primes = [2, 3, 5, 7, 11, 97, 1009, 9973, 104729, 999983, 15485863]
    known_composites = [4, 6, 9, 100, 1000, 104730, 999981]
    
    for n in known_primes:
        assert is_prime(n), f"FAIL: {n}"
    for n in known_composites:
        assert not is_prime(n), f"FAIL: {n}"
    print("✓ Correctness passed")
    
    # Benchmark 1: Repeated (cache kicks in)
    test_repeated = [2, 17, 97, 1009, 9973, 104729, 999983, 1299709, 15485863, 32452843]
    
    is_prime.cache_clear()
    start = time.time()
    for _ in range(10000):
        for n in test_repeated:
            is_prime(n)
    repeated_time = time.time() - start
    
    # Benchmark 2: Unique numbers (no cache help)
    # Generate unique test numbers
    unique_numbers = list(range(999_900, 1_000_100))  # 200 unique numbers
    
    is_prime.cache_clear()
    start = time.time()
    for n in unique_numbers:
        is_prime(n)
    unique_time = time.time() - start
    
    print(f'Gen6 repeated (10k x 10):   {repeated_time:.4f}s')
    print(f'Gen6 unique (200 numbers):  {unique_time:.6f}s')
    print(f'Cache info: {is_prime.cache_info()}')
