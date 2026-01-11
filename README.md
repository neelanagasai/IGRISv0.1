# IGRIS v1.0

IGRIS is a local, rule-governed LLM assistant for technical reasoning, cybersecurity workflows, and systems experimentation. It uses a **2-model architecture** with intelligent routing for optimal performance.

## Features

- **Smart Routing**: Automatically routes queries to the best model (Qwen for chat, DeepSeek for code)
- **Streaming Output**: Real-time token streaming for responsive interaction
- **Response Caching**: MD5-based caching to avoid redundant inference
- **Syntax Highlighting**: Rich terminal output with code highlighting
- **Session Logging**: JSONL-based logging with statistics tracking
- **Conversation Memory**: Maintains context across turns

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│  Fast Router    │  (Keyword-based heuristic)
│  (No LLM call)  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌─────────┐
│ Qwen  │ │DeepSeek │
│ 2.5 3B│ │Coder 6.7│
│ :8001 │ │  :8002  │
└───────┘ └─────────┘
```

**Models:**
- **Qwen 2.5 3B** (Port 8001): General conversation, explanations, analysis
- **DeepSeek Coder 6.7B** (Port 8002): Code generation, debugging, technical tasks

---

## Project Structure

```
llm-cyber/
├── scripts/
│   ├── orchestrator.py    # Main entry point with REPL
│   ├── base.py            # Model configs, HTTP client, caching
│   ├── qwen.py            # Qwen model interface
│   ├── deepseek.py        # DeepSeek model interface
│   ├── formatting.py      # Rich output formatting
│   ├── logger.py          # JSONL logging system
│   └── start_igris.sh     # Server startup script (tmux)
├── prompts/
│   ├── FACE_SYSTEM.md     # Qwen system prompt
│   └── DEEPSEEK_SYSTEM.md # DeepSeek system prompt
├── models/                # Model weights (git-ignored)
├── logs/                  # Session logs (git-ignored)
├── tests/                 # Test suite
└── llama.cpp/             # Inference engine (submodule)
```

---

## Requirements

- Linux (tested on Arch Linux)
- Python 3.10+
- CMake
- GGUF-compatible models (not included)
- Python packages: `requests`, `rich` (optional, for formatting)

---

## Setup

Clone the repository:

```bash
git clone https://github.com/<your-username>/llm-cyber.git
cd llm-cyber
```

Initialize submodules:

```bash
git submodule update --init --recursive
```

Build llama.cpp:

```bash
cd llama.cpp
cmake -B build -DLLAMA_NATIVE=ON
cmake --build build -j$(nproc)
```

---

## Running IGRIS

### 1. Start the model servers

```bash
./scripts/start_igris.sh
```

This starts both models in a tmux session:
- Qwen on port 8001
- DeepSeek on port 8002

### 2. Run the orchestrator

```bash
python scripts/orchestrator.py
```

---

## Commands

| Command    | Description                              |
|------------|------------------------------------------|
| `/status`  | Check model server health                |
| `/stats`   | Show session statistics                  |
| `/clear`   | Clear conversation history               |
| `/cache`   | Clear response cache                     |
| `/stream`  | Toggle streaming mode on/off             |
| `/history` | Show conversation history                |
| `/reset`   | Reset all (logs, cache, history)         |
| `/help`    | Show help message                        |
| `/quit`    | Exit IGRIS                               |

---

## Models

Model weights are NOT included. Download compatible GGUF models:

- **Qwen 2.5 3B Instruct** (Q4_K_M recommended)
- **DeepSeek Coder 6.7B Instruct** (Q4_K_M recommended)

Place them in the `models/` directory.

---

## Core Design Principles

- **Behavior before personality**: Rules always override tone or style
- **Task-based prompting**: Each request declares intent explicitly
- **Local-first execution**: No cloud dependency during inference
- **Transparent failure modes**: Model can say "insufficient information"
- **Efficiency first**: 2-model architecture eliminates router overhead

---

## Third-Party Software

This project uses [llama.cpp](https://github.com/ggerganov/llama.cpp) by Georgi Gerganov, licensed under the MIT License.

---

## Disclaimer

This project is for educational and research purposes only.
Users are responsible for ethical and legal use.

---

## Contributing

Feel free to contribute through forks and pull requests.

---

## Status

**v1.0** - Stable 2-model architecture with streaming, caching, and syntax highlighting.
