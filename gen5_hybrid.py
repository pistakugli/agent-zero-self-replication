#!/usr/bin/env python3
"""
Generation 5 - Hybrid SOTA
============================
Sieve za male + Miller-Rabin za veće.
Pravi benchmark sa raznim veličinama.

Small numbers: O(1) lookup u sieve
Large numbers: O(k * log^2(n)) Miller-Rabin
"""

# Sieve of Eratosthenes - precompute do 10000
def _build_sieve(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    return sieve

_SIEVE_LIMIT = 10000
_SIEVE = _build_sieve(_SIEVE_LIMIT)

def _miller_rabin(n):
    """Deterministic Miller-Rabin za n < 3,215,031,751"""
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for a in (2, 3, 5, 7):
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def is_prime(n):
    if n <= _SIEVE_LIMIT:
        return _SIEVE[n] if n >= 0 else False
    
    # Quick divisibility check
    if n % 2 == 0 or n % 3 == 0 or n % 5 == 0:
        return False
    
    return _miller_rabin(n)

if __name__ == '__main__':
    import time
    
    # Correctness
    known_primes = [2, 3, 5, 7, 11, 97, 1009, 9973, 104729, 999983]
    known_composites = [4, 6, 9, 100, 1000, 104730, 999981]
    
    for n in known_primes:
        assert is_prime(n), f"FAIL: {n} should be prime"
    for n in known_composites:
        assert not is_prime(n), f"FAIL: {n} should NOT be prime"
    
    print("✓ Correctness passed")
    
    # Benchmark - male + veće
    small = [2, 17, 97, 1009, 9973]
    large = [104729, 999983, 1299709, 15485863, 32452843]
    
    # Small benchmark
    start = time.time()
    for _ in range(10000):
        for n in small:
            is_prime(n)
    small_time = time.time() - start
    
    # Large benchmark
    start = time.time()
    for _ in range(10000):
        for n in large:
            is_prime(n)
    large_time = time.time() - start
    
    print(f'Gen5 small numbers: {small_time:.4f}s')
    print(f'Gen5 large numbers: {large_time:.4f}s')
    print(f'Gen5 total:         {small_time + large_time:.4f}s')
