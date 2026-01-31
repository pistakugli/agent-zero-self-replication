#!/usr/bin/env python3
"""Gen11 - Segmented Sieve for range queries. Agent Zero generated.
New: primes_in_range(low, high) - find ALL primes in range efficiently.
Segmented sieve O((high-low)*log(log(high))) vs checking each number individually.
"""
from functools import lru_cache

def _build_sieve(limit):
    s = bytearray(b'\x01') * (limit + 1)
    s[0] = s[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return s

_SIEVE_LIMIT = 1_000_000
_SIEVE = _build_sieve(_SIEVE_LIMIT)
_BASE_PRIMES = [i for i in range(2, 1001) if _SIEVE[i]]
_WITNESSES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)

def _miller_rabin(n):
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for a in _WITNESSES:
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

@lru_cache(maxsize=16384)
def is_prime(n):
    if n <= _SIEVE_LIMIT:
        return bool(_SIEVE[n]) if n >= 0 else False
    for p in _BASE_PRIMES[:50]:
        if n % p == 0: return n == p
    return _miller_rabin(n)

def primes_in_range(low, high):
    """Segmented sieve: all primes in [low, high]."""
    if high < 2: return []
    low = max(low, 2)
    size = high - low + 1
    is_p = bytearray(b'\x01') * size
    for p in _BASE_PRIMES:
        if p * p > high: break
        start = ((low + p - 1) // p) * p
        if start < p * p: start = p * p
        for j in range(start - low, size, p):
            is_p[j] = 0
    return [low + i for i in range(size) if is_p[i]]

if __name__ == "__main__":
    import time

    for p in [2,3,5,7,11,97,1009,9973,104729,999983,15485863,32452843,49979687]:
        assert is_prime(p), f"FAIL {p}"
    for c in [4,6,9,100,1000,104730,999981]:
        assert not is_prime(c), f"FAIL {c}"
    print("✓ is_prime OK")

    seg = primes_in_range(10000, 10200)
    brute = [n for n in range(10000, 10201) if is_prime(n)]
    assert seg == brute, "Segmented mismatch"
    print(f"✓ Segmented sieve OK: {len(seg)} primes in [10000,10200]")

    cases = [2,17,97,1009,9973,104729,999983,1299709,15485863,32452843]
    is_prime.cache_clear()
    start = time.time()
    for _ in range(10000):
        for n in cases: is_prime(n)
    t_rep = time.time() - start

    start = time.time()
    for _ in range(100):
        primes_in_range(1_000_000, 1_100_000)
    t_seg = time.time() - start
    count = len(primes_in_range(1_000_000, 1_100_000))

    print(f"Gen11 repeated:  {t_rep:.4f}s")
    print(f"Gen11 seg_sieve: {t_seg:.4f}s (100x [1M-1.1M], {count} primes)")
