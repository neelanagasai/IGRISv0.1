#!/usr/bin/env bash

SESSION="igris"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Kill existing session if running
tmux kill-session -t $SESSION 2>/dev/null

tmux new-session -d -s $SESSION -c "$ROOT"

# QWEN (Face/General) - Port 8001
tmux send-keys -t $SESSION \
"echo '[IGRIS] Starting Qwen on port 8001...' && \
$ROOT/llama.cpp/build/bin/llama-server \
-m $ROOT/models/qwen2.5-3b-instruct-q4_k_m.gguf \
--host 127.0.0.1 --port 8001 \
-c 4096 -t 6" C-m

# DEEPSEEK (Coder) - Port 8002
tmux split-window -h -t $SESSION -c "$ROOT"
tmux send-keys -t $SESSION \
"echo '[IGRIS] Starting DeepSeek on port 8002...' && \
$ROOT/llama.cpp/build/bin/llama-server \
-m $ROOT/models/deepseek-coder-6.7b-instruct-q4_k_m.gguf \
--host 127.0.0.1 --port 8002 \
-c 4096 -t 8" C-m

tmux select-layout even-horizontal
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  IGRIS - Optimized 2-Model Architecture                      ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Qwen (General)  : http://127.0.0.1:8001                     ║"
echo "║  DeepSeek (Code) : http://127.0.0.1:8002                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Run: python scripts/orchestrator.py"
echo "Or:  tmux attach -t $SESSION"
tmux attach -t $SESSION
