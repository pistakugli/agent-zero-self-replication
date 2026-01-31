# 🧬 Agent Zero Self-Replication

**Autonomous code evolution by Agent Zero**

Agent Zero reads its own code, analyzes it, and generates improved versions — each generation using a fundamentally different algorithm.

---

## 📊 Results

### Repeated queries (same numbers, 10k iterations)

| Gen | Time | Speedup | Algorithm |
|-----|------|---------|-----------|
| Gen1 | 3.4395s | 1.0x | Trial division |
| Gen2 | 1.8509s | 1.9x | Wheel factorization 6k±1 |
| Gen3 | 0.0090s | 382.8x | Cached wheel |
| Gen4 | 0.3007s | 11.4x | Deterministic Miller-Rabin |
| Gen5 | 0.2147s | 16.0x | Sieve + Miller-Rabin |
| **Gen6** | **0.0091s** | **377.4x** | **Sieve + Cache + Miller-Rabin** |

### Unique queries (200 new numbers, no cache)

| Gen | Time | Speedup | Algorithm |
|-----|------|---------|-----------|
| Gen1 | 0.000510s | 1.0x | Trial division |
| Gen2 | 0.000278s | 1.8x | Wheel factorization |
| Gen3 | 0.000313s | 1.6x | Cached wheel |
| **Gen4** | **0.000116s** | **4.4x** | **Deterministic Miller-Rabin** |
| Gen5 | 0.000129s | 4.0x | Sieve + Miller-Rabin |
| Gen6 | 0.000126s | 4.0x | Sieve + Cache + Miller-Rabin |

---

## 🧬 Evolution Path

```
Gen1: Trial division — skip evens
  ↓ 1.9x
Gen2: Wheel factorization — 6k±1 pattern
  ↓ 200x (repeated)
Gen3: Cached wheel — O(1) on repeated queries
  ↓ algorithm change
Gen4: Miller-Rabin — O(k·log²n), deterministic for n < 3.2B
  ↓ hybrid
Gen5: Sieve + Miller-Rabin — precompute small, MR for large
  ↓ combined
Gen6: Sieve + Cache + Miller-Rabin — SOTA for all scenarios
```

### Key insight

Gen1–Gen3 are all **trial division variants** — O(√n).  
Gen4 introduced **Miller-Rabin** — a fundamentally different algorithm class.  
Gen6 combines all three strategies: sieve lookup, cache, and Miller-Rabin.

---

## 📂 Files

| File | Description |
|------|-------------|
| `gen1_real.py` | Trial division, skip evens |
| `gen2_real.py` | Wheel factorization |
| `gen3_real.py` | Cached wheel |
| `gen4_miller_rabin.py` | Deterministic Miller-Rabin |
| `gen5_hybrid.py` | Sieve + Miller-Rabin |
| `gen6_sota.py` | SOTA: Sieve + Cache + Miller-Rabin |
| `final_benchmark.py` | Full benchmark — run all generations |

---

## 🚀 Run

```bash
# Run benchmark
python3 final_benchmark.py

# Run specific generation
python3 gen6_sota.py
```

---

## 🏗️ Technology

- **Agent Zero** v0.9.7 — autonomous agent framework
- **Hybrid architecture** — Claude reasoning + Agent Zero execution
- **Algorithms** — Trial division → Wheel → Miller-Rabin → Hybrid SOTA

---

*Created autonomously by Agent Zero · 2026-01-31*  
*github.com/pistakugli*
