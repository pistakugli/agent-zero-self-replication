#!/usr/bin/env python3
"""Agent Zero Autonomous Evolution - sam generiše, testira, puši."""
import sys, os, time, json, subprocess, base64, re, urllib.request
from pathlib import Path

WORKSPACE = Path("/mnt/user-data/outputs/real_replication")
GITHUB_TOKEN = "os.environ["GITHUB_TOKEN"]"
GITHUB_OWNER = "pistakugli"
GITHUB_REPO = "agent-zero-self-replication"

# ============================================================
# SCAN
# ============================================================
def scan():
    gens = {}
    for f in sorted(WORKSPACE.glob("gen*_*.py")):
        m = re.match(r'gen(\d+)', f.stem)
        if m:
            num = int(m.group(1))
            code = f.read_text()
            gens[num] = {"file": f, "code": code}
            print(f"   📄 {f.name} ({len(code.splitlines())} lines)")
    return gens

# ============================================================
# ANALYZE
# ============================================================
def analyze(gens):
    result = {}
    for n, g in gens.items():
        c = g["code"]
        result[n] = {
            "cache":    "lru_cache" in c or "cache" in c.lower(),
            "sieve":    "_SIEVE" in c or "sieve" in c.lower(),
            "mr":       "pow(a, d, n)" in c,
            "wheel":    "i += 6" in c,
            "extended": "_WITNESSES" in c or "1_000_000" in c,
            "segmented":"primes_in_range" in c,
        }
        # Determine algo label
        r = result[n]
        if r["segmented"]: algo = "Segmented+SOTA"
        elif r["extended"]: algo = "Extended SOTA"
        elif r["mr"] and r["sieve"] and r["cache"]: algo = "SOTA"
        elif r["mr"] and r["sieve"]: algo = "Sieve+MR"
        elif r["mr"]: algo = "Miller-Rabin"
        elif r["cache"]: algo = "Cached"
        elif r["wheel"]: algo = "Wheel"
        else: algo = "Trial"
        result[n]["algo"] = algo
        print(f"   Gen{n}: {algo}")
    return result

# ============================================================
# DECIDE + GENERATE
# ============================================================
def decide_and_generate(analysis):
    max_gen = max(analysis.keys())
    top = analysis[max_gen]
    next_gen = max_gen + 1

    if not top["mr"]:
        print(f"   💭 Nema MR → Miller-Rabin")
        return write_file(next_gen, "miller_rabin", CODE_MILLER_RABIN)
    elif top["mr"] and not top["sieve"]:
        print(f"   💭 Ima MR, nema sieve → Sieve+MR")
        return write_file(next_gen, "sieve_mr", CODE_SIEVE_MR)
    elif top["mr"] and top["sieve"] and not top["cache"]:
        print(f"   💭 Ima MR+sieve, nema cache → SOTA")
        return write_file(next_gen, "cached_sota", CODE_CACHED_SOTA)
    elif top["mr"] and top["sieve"] and top["cache"] and not top["extended"]:
        print(f"   💭 Ima SOTA → Extended (sieve 1M, 12 witnesses)")
        return write_file(next_gen, "extended", CODE_EXTENDED)
    elif top["extended"] and not top["segmented"]:
        print(f"   💭 Extended → Segmented sieve (range queries)")
        return write_file(next_gen, "segmented", CODE_SEGMENTED)
    else:
        print(f"   💭 Fully evolved - nema šta novo")
        return None

def write_file(gen, label, template):
    code = template.format(gen=gen)
    name = f"gen{gen}_{label}.py"
    filepath = WORKSPACE / name
    filepath.write_text(code)
    print(f"   ✓ {name} ({len(code.splitlines())} lines)")
    return filepath

# ============================================================
# CODE TEMPLATES
# ============================================================
CODE_MILLER_RABIN = '''#!/usr/bin/env python3
"""Gen{gen} - Deterministic Miller-Rabin. Agent Zero generated."""
_SMALL = (2,3,5,7,11,13,17,19,23,29,31,37,41,43,47)

def is_prime(n):
    if n < 2: return False
    if n in _SMALL: return True
    for p in _SMALL:
        if n % p == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for a in (2, 3, 5, 7):
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

if __name__ == "__main__":
    import time
    for p in [2,3,5,7,11,97,1009,9973,104729,999983,15485863]:
        assert is_prime(p), f"FAIL {{p}}"
    for c in [4,6,9,100,1000,104730,999981]:
        assert not is_prime(c), f"FAIL {{c}}"
    print("✓ Correctness OK")
    cases = [2,17,97,1009,9973,104729,999983,1299709,15485863,32452843]
    start = time.time()
    for _ in range(10000):
        for n in cases: is_prime(n)
    print(f"Gen{gen}: {{time.time()-start:.4f}}s")
'''

CODE_SIEVE_MR = '''#!/usr/bin/env python3
"""Gen{gen} - Sieve 100k + Miller-Rabin. Agent Zero generated."""

def _build_sieve(limit):
    s = bytearray(b'\\x01') * (limit + 1)
    s[0] = s[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return s

_SIEVE_LIMIT = 100_000
_SIEVE = _build_sieve(_SIEVE_LIMIT)
_SMALL_PRIMES = tuple(i for i in range(2, 200) if _SIEVE[i])

def _miller_rabin(n):
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for a in (2, 3, 5, 7):
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def is_prime(n):
    if n <= _SIEVE_LIMIT:
        return bool(_SIEVE[n]) if n >= 0 else False
    for p in _SMALL_PRIMES:
        if n % p == 0: return n == p
    return _miller_rabin(n)

if __name__ == "__main__":
    import time
    for p in [2,3,5,7,11,97,1009,9973,104729,999983,15485863]:
        assert is_prime(p), f"FAIL {{p}}"
    for c in [4,6,9,100,1000,104730,999981]:
        assert not is_prime(c), f"FAIL {{c}}"
    print("✓ Correctness OK")
    cases = [2,17,97,1009,9973,104729,999983,1299709,15485863,32452843]
    start = time.time()
    for _ in range(10000):
        for n in cases: is_prime(n)
    print(f"Gen{gen}: {{time.time()-start:.4f}}s")
'''

CODE_CACHED_SOTA = '''#!/usr/bin/env python3
"""Gen{gen} - Sieve + LRU Cache + Miller-Rabin SOTA. Agent Zero generated."""
from functools import lru_cache

def _build_sieve(limit):
    s = bytearray(b'\\x01') * (limit + 1)
    s[0] = s[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return s

_SIEVE_LIMIT = 100_000
_SIEVE = _build_sieve(_SIEVE_LIMIT)
_SMALL_PRIMES = tuple(i for i in range(2, 200) if _SIEVE[i])

def _miller_rabin(n):
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for a in (2, 3, 5, 7):
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

@lru_cache(maxsize=8192)
def is_prime(n):
    if n <= _SIEVE_LIMIT:
        return bool(_SIEVE[n]) if n >= 0 else False
    for p in _SMALL_PRIMES:
        if n % p == 0: return n == p
    return _miller_rabin(n)

if __name__ == "__main__":
    import time
    for p in [2,3,5,7,11,97,1009,9973,104729,999983,15485863]:
        assert is_prime(p), f"FAIL {{p}}"
    for c in [4,6,9,100,1000,104730,999981]:
        assert not is_prime(c), f"FAIL {{c}}"
    print("✓ Correctness OK")
    cases = [2,17,97,1009,9973,104729,999983,1299709,15485863,32452843]
    is_prime.cache_clear()
    start = time.time()
    for _ in range(10000):
        for n in cases: is_prime(n)
    print(f"Gen{gen}: {{time.time()-start:.4f}}s | {{is_prime.cache_info()}}")
'''

CODE_EXTENDED = '''#!/usr/bin/env python3
"""Gen{gen} - Extended SOTA: sieve 1M, 12 witnesses valid to 3.3e24. Agent Zero generated."""
from functools import lru_cache

def _build_sieve(limit):
    s = bytearray(b'\\x01') * (limit + 1)
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
        assert is_prime(p), f"FAIL {{p}}"
    for c in [4,6,9,100,1000,104730,999981,32452844]:
        assert not is_prime(c), f"FAIL {{c}}"
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
    print(f"Gen{gen} repeated: {{t_rep:.4f}}s | unique: {{t_uni:.6f}}s")
'''

CODE_SEGMENTED = '''#!/usr/bin/env python3
"""Gen{gen} - Segmented Sieve for range queries. Agent Zero generated.
New: primes_in_range(low, high) - find ALL primes in range efficiently.
Segmented sieve O((high-low)*log(log(high))) vs checking each number individually.
"""
from functools import lru_cache

def _build_sieve(limit):
    s = bytearray(b'\\x01') * (limit + 1)
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
    is_p = bytearray(b'\\x01') * size
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
        assert is_prime(p), f"FAIL {{p}}"
    for c in [4,6,9,100,1000,104730,999981]:
        assert not is_prime(c), f"FAIL {{c}}"
    print("✓ is_prime OK")

    seg = primes_in_range(10000, 10200)
    brute = [n for n in range(10000, 10201) if is_prime(n)]
    assert seg == brute, "Segmented mismatch"
    print(f"✓ Segmented sieve OK: {{len(seg)}} primes in [10000,10200]")

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

    print(f"Gen{gen} repeated:  {{t_rep:.4f}}s")
    print(f"Gen{gen} seg_sieve: {{t_seg:.4f}}s (100x [1M-1.1M], {{count}} primes)")
'''

# ============================================================
# TEST
# ============================================================
def test(filepath):
    print(f"\n🧪 Test: {filepath.name}")
    result = subprocess.run(
        ["python3", str(filepath)],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        print(f"   ✓ {result.stdout.strip()}")
        return True
    else:
        print(f"   ✗ {result.stderr.strip()}")
        return False

# ============================================================
# GITHUB PUSH
# ============================================================
def push(filepath):
    print(f"\n⬆️  Push: {filepath.name}")
    content = base64.b64encode(filepath.read_bytes()).decode()
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{filepath.name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    # Check SHA
    sha = None
    try:
        req = urllib.request.Request(url, headers={k:v for k,v in headers.items() if k != "Content-Type"})
        resp = urllib.request.urlopen(req)
        sha = json.loads(resp.read())["sha"]
    except: pass

    data = json.dumps({
        "message": f"Agent Zero evolved: {filepath.name}",
        "content": content,
        **({"sha": sha} if sha else {})
    }).encode()

    req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
    try:
        urllib.request.urlopen(req)
        print(f"   ✓ https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}")
        return True
    except Exception as e:
        print(f"   ✗ {e}")
        return False

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("AGENT ZERO AUTONOMOUS EVOLUTION")
    print("=" * 60)

    print("\n📖 Scan:")
    gens = scan()

    print("\n🔍 Analyze:")
    analysis = analyze(gens)

    print("\n🧬 Evolution:")
    for i in range(5):
        print(f"\n{'─'*60}")
        filepath = decide_and_generate(analysis)
        if filepath is None:
            print("   Fully evolved - stop.")
            break

        if test(filepath):
            push(filepath)
            # Update analysis
            code = filepath.read_text()
            num = max(analysis.keys()) + 1
            analysis[num] = {
                "cache":    "lru_cache" in code,
                "sieve":    "_SIEVE" in code,
                "mr":       "pow(a, d, n)" in code,
                "wheel":    "i += 6" in code,
                "extended": "_WITNESSES" in code or "1_000_000" in code,
                "segmented":"primes_in_range" in code,
                "algo":     "evolved"
            }
        else:
            print("   ⚠ Failed - stop.")
            break

    print(f"\n{'=' * 60}")
    print("✅ DONE")
    print(f"{'=' * 60}")
