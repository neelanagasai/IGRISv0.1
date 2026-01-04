# IGRIS – 30-Day Development Roadmap (v0.1)

This roadmap reflects the final architecture:

FACE MODEL → QWEN (intent + confidence) →  
- MISTRAL (recon / intelligence)  
- DEEPSEEK (dirty coding / heavy logic)

A confidence gate is used to prevent misrouting.

---

## WEEK 1 — FOUNDATION (Days 1–7)
**Goal:** Stable base, single responsibility per component.

### Day 1–2
- Finalize repository structure
- Lock:
  - SYSTEM_RULES.md
  - PERSONA.md (IGRIS)
  - task_context.txt

### Day 3
- Select and integrate **Face model**
- Face handles:
  - user interaction
  - formatting
  - personality
- No heavy reasoning here

### Day 4–5
- Integrate **Mistral** as internal model
- Mistral outputs:
  - `intent`
  - `confidence` (0.0 – 1.0)

### Day 6
- Implement **confidence gate**
  - confidence < 0.7 → ask clarification
  - confidence ≥ 0.7 → route

### Day 7
- End-to-end test:
  - Face → Mistral → Face
- No DeepSeek yet

---

## WEEK 2 — ROUTING & CONTROL (Days 8–14)
**Goal:** Correct routing, zero ambiguity.

### Day 8
- Define intent schema:
  - CHAT
  - EXPLAIN
  - RECON
  - INTEL
  - CODE_DIRTY

### Day 9–10
- Routing logic:
  - RECON / INTEL → Mistral
  - CODE_DIRTY → DeepSeek

### Day 11
- Add fallback rules:
  - model failure handling
  - partial responses with warnings

### Day 12
- Logging:
  - intent
  - confidence
  - selected model
  - execution time

### Day 13–14
- Stress-test misclassification
- Tune confidence threshold

---

## WEEK 3 — EXECUTION & SAFETY (Days 15–21)
**Goal:** Heavy work isolated, face remains fast.

### Day 15
- Integrate **DeepSeek-Coder**
- CODE-only context, no persona

### Day 16
- Normalize outputs:
  - strip personality from DeepSeek
  - Face formats final response

### Day 17
- Add execution limits:
  - timeouts
  - memory guards

### Day 18
- Red-team task testing (lab / legal only)
- Script generation, automation, parsing

### Day 19–20
- Memory design:
  - short-term (session context)
  - long-term (summaries / notes)

### Day 21
- Full pipeline test:
  Face → Mistral → DeepSeek → Face

---

## WEEK 4 — HARDENING & POLISH (Days 22–30)
**Goal:** Stable, presentable, extensible system.

### Day 22
- Improve clarification UX (confidence gate)

### Day 23
- Error messaging:
  - clear
  - neutral
  - non-chatty

### Day 24
- Performance tuning:
  - context trimming
  - batch sizing

### Day 25
- Model hot-swap configuration
- Face / Mistral / DeepSeek interchangeable

### Day 26
- Security review:
  - prompt injection attempts
  - rule bypass tests

### Day 27
- Documentation:
  - architecture explanation
  - routing flow

### Day 28
- Tag release: **v0.1**

### Day 29–30
- Buffer days:
  - bug fixes
  - refactors
- Decide next phase:
  - server mode
  - cloud deployment
  - fine-tuning

---

## Notes
- IGRIS is a **system**, not a single model.
- Personality lives only in the Face model.
- All execution models are replaceable.
