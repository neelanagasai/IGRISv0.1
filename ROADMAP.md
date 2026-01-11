# IGRIS – Development Roadmap

## Current Architecture (v1.0)

```
User Query → Fast Router (heuristic) → Qwen 2.5 3B (chat) 
                                     → DeepSeek Coder 6.7B (code)
```

**Optimized 2-model system** — No LLM-based routing overhead.

---

## ✅ Phase 1 — Foundation (COMPLETED)

- [x] Repository structure finalized
- [x] System prompts created (FACE_SYSTEM.md, DEEPSEEK_SYSTEM.md)
- [x] llama.cpp integration (HTTP server mode)
- [x] Model configuration system (base.py)
- [x] Basic orchestration working

---

## ✅ Phase 2 — Multi-Model Architecture (COMPLETED)

- [x] Qwen 2.5 3B integration (general chat)
- [x] DeepSeek Coder 6.7B integration (code tasks)
- [x] Fast keyword-based routing (no LLM overhead)
- [x] ChatML prompt formatting
- [x] Conversation history management (4-turn context)
- [x] Model health checks

---

## ✅ Phase 3 — Performance Optimization (COMPLETED)

- [x] Streaming output (SSE-based)
- [x] Response caching (MD5-based, 50 entries)
- [x] Syntax highlighting (Rich library)
- [x] Session logging (JSONL format)
- [x] Statistics tracking
- [x] Reset command (/reset)

---

## ✅ Phase 4 — Code Quality (COMPLETED)

- [x] Test suite (14 tests passing)
- [x] Error handling improvements
- [x] Import fixes (relative/absolute)
- [x] Documentation (README v1.0)
- [x] Architecture consolidation (removed 3-model overhead)

---

## 🔄 Phase 5 — Hardening (IN PROGRESS)

- [ ] Prompt injection testing
- [ ] Rule bypass attempts
- [ ] Context overflow handling
- [ ] Timeout tuning per model
- [ ] Memory usage profiling

---

## 📋 Phase 6 — Advanced Features (PLANNED)

- [ ] Long-term memory (session summaries)
- [ ] Model hot-swap configuration
- [ ] Custom routing rules (user-configurable)
- [ ] Web UI interface
- [ ] API server mode
- [ ] Multi-turn code editing context

---

## 📋 Phase 7 — Deployment (PLANNED)

- [ ] Docker containerization
- [ ] GPU optimization (CUDA/ROCm)
- [ ] Systemd service files
- [ ] Configuration file (YAML/TOML)
- [ ] CLI arguments

---

## 📋 Phase 8 — Extensions (FUTURE)

- [ ] Tool/function calling
- [ ] RAG integration (local docs)
- [ ] Voice input/output
- [ ] Plugin system
- [ ] Fine-tuning pipeline

---

## Architecture Notes

| Component | Model | Port | Purpose |
|-----------|-------|------|---------|
| Chat | Qwen 2.5 3B | 8001 | General conversation, explanations |
| Code | DeepSeek Coder 6.7B | 8002 | Code generation, debugging |

**Design Principles:**
- Personality lives only in Qwen (Face model)
- DeepSeek is task-focused, no persona
- Fast routing eliminates LLM overhead
- All models are replaceable

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | Initial | 3-model architecture (Qwen + DeepSeek + Mistral router) |
| v1.0 | Current | 2-model architecture, streaming, caching, highlighting |
