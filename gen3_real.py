#!/usr/bin/env python3
"""Generation 3 - Feature rich with caching"""

class PrimeChecker:
    def __init__(self):
        self.cache = {}
    
    def is_prime(self, n):
        if n in self.cache:
            return self.cache[n]
        
        if n < 2:
            result = False
        elif n == 2 or n == 3:
            result = True
        elif n % 2 == 0 or n % 3 == 0:
            result = False
        else:
            i = 5
            result = True
            while i * i <= n:
                if n % i == 0 or n % (i + 2) == 0:
                    result = False
                    break
                i += 6
        
        self.cache[n] = result
        return result

if __name__ == '__main__':
    import time
    checker = PrimeChecker()
    start = time.time()
    for _ in range(10000):
        for n in [2, 17, 97, 1009, 9973]:
            checker.is_prime(n)
    print(f'Gen3: {time.time()-start:.4f}s (cached)')
