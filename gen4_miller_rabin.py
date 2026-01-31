#!/usr/bin/env python3
"""
Generation 4 - Deterministic Miller-Rabin
==========================================
SOTA primality test. Ne trial division.

Miller-Rabin: O(k * log^2(n))
Za n < 3,215,031,751 dovoljno je witnesses {2, 3, 5, 7} - 100% tačno.
Za n < 3,474,749,660,383 - witnesses {2, 3, 5, 7, 11, 13}

Fundamentalno drugi algoritam od trial division.
"""

def is_prime(n):
    if n < 2:
        return False
    
    # Mali prosti brojevi - direktno
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
    if n in small_primes:
        return True
    
    # Deljivo sa malim prostim brojevima
    for p in small_primes:
        if n % p == 0:
            return False
    
    # Miller-Rabin:
    # Pišemo n-1 = 2^r * d, gde je d neparan
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Deterministic witnesses za n < 3,215,031,751
    witnesses = (2, 3, 5, 7)
    
    for a in witnesses:
        if a >= n:
            continue
        
        # Računamo a^d mod n
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        # Kvadriramo r-1 puta
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True

if __name__ == '__main__':
    import time
    
    # Correctness check
    known_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 97, 1009, 9973]
    known_composites = [4, 6, 8, 9, 10, 15, 100, 1000]
    
    for n in known_primes:
        assert is_prime(n), f"FAIL: {n} should be prime"
    for n in known_composites:
        assert not is_prime(n), f"FAIL: {n} should be composite"
    
    print("✓ All correctness checks passed")
    
    # Benchmark
    test_cases = [2, 17, 97, 1009, 9973]
    
    start = time.time()
    for _ in range(10000):
        for n in test_cases:
            is_prime(n)
    elapsed = time.time() - start
    
    print(f'Gen4 (Miller-Rabin): {elapsed:.4f}s')
