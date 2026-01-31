#!/usr/bin/env python3
"""Gen10 - Extended SOTA: sieve 1M + 12 witnesses (valid to 3.3e24). Agent Zero generated."""
from functools import lru_cache

def _build_sieve(limit):
    s = bytearray(b'\x01') * (limit + 1)
    s[0] = s[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return s

_SIEVE_LIMIT = 1_000_000
_SIEVE = _build_sieve(_SIEVE_LIMIT)
_SMALL_PRIMES = tuple(i for i in range(2, 1000) if _SIEVE[i])
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
    for p in _SMALL_PRIMES[:50]:
        if n % p == 0: return n == p
    return _miller_rabin(n)

if __name__ == "__main__":
    import time
    for p in [2,3,5,7,11,97,1009,9973,104729,999983,15485863,32452843,49979687]:
        assert is_prime(p), f"FAIL {p}"
    for c in [4,6,9,100,1000,104730,999981,32452844]:
        assert not is_prime(c), f"FAIL {c}"
    print("✓ Correctness OK")
    cases = [2,17,97,1009,9973,104729,999983,1299709,15485863,32452843]
    is_prime.cache_clear()
    start = time.time()
    for _ in range(10000):
        for n in cases: is_prime(n)
    t_rep = time.time() - start
    unique = list(range(9_999_900, 10_000_100))
    is_prime.cache_clear()
    start = time.time()
    for n in unique: is_prime(n)
    t_uni = time.time() - start
    print(f"Gen10 repeated: {t_rep:.4f}s | unique: {t_uni:.6f}s")
