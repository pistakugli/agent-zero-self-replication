#!/usr/bin/env python3
"""Generation 1 - Agent Zero generated"""

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

if __name__ == '__main__':
    import time
    start = time.time()
    for _ in range(10000):
        for n in [2, 17, 97, 1009, 9973]:
            is_prime(n)
    print(f'Gen1: {time.time()-start:.4f}s')
