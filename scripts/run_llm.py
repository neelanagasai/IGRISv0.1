import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load(path):
    return path.read_text().strip()

SYSTEM_RULES = load(ROOT / "SYSTEM_RULES.md")
PERSONA = load(ROOT / "PERSONA.md")
TASK_CONTEXT = load(ROOT / "prompts/task_context.txt")

user_input = input(">> ").strip()

PROMPT = f"""
You must strictly follow the Global Operating Rules.

=== GLOBAL RULES ===
{SYSTEM_RULES}

=== PERSONA (tone only) ===
{PERSONA}

=== TASK CONTEXT ===
{TASK_CONTEXT}

=== USER INPUT ===
{user_input}

=== RESPONSE ===
"""

cmd = [
    str(ROOT / "llama.cpp/build/bin/llama-cli"),
    "-m", str(ROOT / "models/mistral-7b-instruct-v0.2.Q5_K_M.gguf"),
    "--prompt", PROMPT,
    "-t", "8",
    "-c", "2048",
    "-b", "256",
    "--temp", "0.7",
    "--top-p", "0.9",
    "--repeat-penalty", "1.1",
]

subprocess.run(cmd)
