# Phase 4 — AI Runtime Layer

**Status:** 🔜 Planned

## Goal
Embed the tiered AI intelligence system into the OS.

## Components
| Component | Purpose | Tier |
|---|---|---|
| llama.cpp | Local LLM runtime | 1 + 2 |
| Phi-3 mini (3.8B) | Default Tier 1 model | 1 |
| LLaMA 3 8B | Enhanced model | 2 |
| Claude API client | Cloud intelligence | 3 |
| Intelligence router | Detects connectivity, routes to correct tier | All |

## Intelligence Router Logic
```python
if internet_available and api_key_valid:
    use_tier_3()  # Claude API
elif gpu_available and large_model_loaded:
    use_tier_2()  # Large local model
else:
    use_tier_1()  # Small local model — always works
```
