# Market Research App — Principal Engineer Improvement Plan
**Date:** 2026-02-14
**Status:** Mostly Complete (13/16 items done)

## Overview
Comprehensive hardening of the market research app based on Opus 4.6 principal engineer review. Focus areas: error handling, security, UI architecture, observability, and production readiness.

---

## Phase 1: Stop the Bleeding (Critical) — COMPLETE

### 1.1 Add Error Handling & Retry Logic to API Calls ✅
**File:** `src/agents.py`
- Added `_get_api_key()` that fails fast on missing key
- Retry with exponential backoff (3 attempts for 429/500+ errors)
- 120s timeout per API call
- Response validation before accessing `.content[0].text`
- `MODEL` and `MAX_TOKENS` as env-configurable constants

### 1.2 Fix Wave Failure Handling ✅
**File:** `src/orchestrator.py`
- `asyncio.gather(*tasks, return_exceptions=True)`
- Per-agent timeout via `asyncio.wait_for(coro, timeout=180)`
- Log failures but continue with partial results

### 1.3 Add Input Validation to ResearchBrief ✅
**File:** `src/models.py`
- `__post_init__()` validates required fields are non-empty strings
- Validates `depth` is one of `{overview, thorough, deep_dive}`
- Strips whitespace from optional fields
- Validates `known_competitors` is a list

### 1.4 Add Structured Logging ✅
**Files:** All `src/*.py` files
- Python `logging` module added to agents, orchestrator, export
- Logs: API calls, token usage, wave timing, errors

---

## Phase 2: UI Architecture (High) — MOSTLY COMPLETE

### 2.1 Extract CSS to External File ✅
**Files:** `app.py` + `assets/styles.css`
- 494 lines of CSS extracted to `assets/styles.css`
- Loaded via `@st.cache_resource` decorator
- app.py reduced from 1,115 to 706 lines

### 2.2 Fix State Management ✅
**File:** `app.py`
- State machine: `intake` → `confirm` → `running` → `results`
- Intake data preserved in `st.session_state.intake_data`
- "Start New Research" button clears all state
- Results cached in session state (survive reruns)

### 2.3 Componentize the Monolithic app.py ⏳ DEFERRED
**Rationale:** app.py now at 706 lines (was 1,115). The state machine refactor made the code significantly more organized. Further splitting into components/ dir is optional and lower priority.

### 2.4 Add Confirmation Step Before Research ✅
**File:** `app.py`
- `display_confirmation()` shows brief summary, estimated time, depth level
- Confirm/Edit/Cancel buttons before research starts

---

## Phase 3: Hardening (Medium) — MOSTLY COMPLETE

### 3.1 Make Model Configurable ✅
**File:** `src/agents.py`
- `MODEL = os.environ.get("RESEARCH_MODEL", "claude-sonnet-4-20250514")`
- `MAX_TOKENS = int(os.environ.get("RESEARCH_MAX_TOKENS", "8192"))`

### 3.2 Add Token Budget Tracking ✅
**Files:** `src/agents.py`, `src/orchestrator.py`
- `_call_api()` returns `_token_usage` metadata with each result
- Orchestrator accumulates per-agent token counts
- `RESEARCH_TOKEN_BUDGET` env var for budget ceiling (0 = no limit)
- Cost estimate logged at end of run (~$3/M input, ~$15/M output)

### 3.3 Improve DOCX Export ✅
**File:** `src/export.py`
- Inline `**bold**`, `*italic*`, `[text](url)` → proper Word formatting
- Markdown tables → `doc.add_table()` with bold headers
- Nested lists (`  - ` / `    - `) → List Bullet 2/3 styles
- 20 new tests covering all three features

### 3.4 Validate Agent Result Schemas ⏳ NOT STARTED
**File:** `src/orchestrator.py`
- Define expected result structure per agent type
- Validate before passing to synthesizer/verifier

---

## Phase 4: Production Readiness (Lower) — PARTIALLY COMPLETE

### 4.1 Add CI/CD Pipeline ✅
**File:** `.github/workflows/ci.yml`
- Lint (ruff) + test (pytest) jobs on Python 3.12
- Runs on PR + push to main

### 4.2 Add Docker Support ⏳ NOT STARTED
- `Dockerfile` for Streamlit app (includes WeasyPrint system deps)
- `docker-compose.yml` for local dev

### 4.3 Add .env Support ✅
**File:** `.env.example`
- Documents ANTHROPIC_API_KEY (required)
- Documents RESEARCH_MODEL, RESEARCH_MAX_TOKENS, RESEARCH_TOKEN_BUDGET (optional)

### 4.4 Improve Source Verification ⏳ NOT STARTED
**File:** `src/agents.py`
- Add HTTP HEAD requests to verify URLs actually exist
- Flag dead links in verification report

---

## Summary

| Phase | Items | Done | Status |
|-------|-------|------|--------|
| Phase 1: Critical | 4 | 4 | **COMPLETE** |
| Phase 2: UI | 4 | 3 | Componentize deferred |
| Phase 3: Hardening | 4 | 3 | Schema validation pending |
| Phase 4: Production | 4 | 2 | Docker + source verification pending |
| **Total** | **16** | **12** | **75%** |

### Tests
- **68 tests passing** (up from 48 original)
- 20 new tests for DOCX export improvements

### Files Changed
- `src/agents.py` — error handling, retry, config constants, token usage
- `src/orchestrator.py` — wave failure handling, token budget, logging
- `src/models.py` — input validation
- `src/export.py` — logging, inline formatting, tables, nested lists
- `app.py` — CSS extraction, state machine, confirmation step (1,115 → 706 lines)

### Files Created
- `assets/styles.css` — extracted CSS (494 lines)
- `assets/__init__.py` — package init
- `.env.example` — environment variable docs
- `.github/workflows/ci.yml` — CI pipeline
- `docs/plans/2026-02-14-principal-engineer-improvements.md` — this file
