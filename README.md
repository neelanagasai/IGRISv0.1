# IGRIS v0.1

IGRIS is a personal research project focused on building a local, rule-governed
LLM assistant for technical reasoning, cybersecurity workflows, and systems
experimentation.

The goal of this project is not to build a chatbot, but to understand and control:
- how LLMs behave under strict rules
- how prompting, context, and persona interact
- how local inference systems work end-to-end

---

## Project Structure

IGRISv0.1/
- SYSTEM_RULES.md        -> Global behavioral constraints (always enforced)
- PERSONA.md             -> Tone/personality only (never overrides rules)
- prompts/
  - task_context.txt     -> Task mode selector (explain / analyze / code / debug)
- scripts/
  - run_llm.py           -> Prompt assembly + execution script
- llama.cpp/             -> Inference engine (git submodule)
- models/                -> Model weights (ignored, user-provided)
- README.md

---

## Core Design Principles

- Behavior before personality  
  Rules always override tone or style.

- Task-based prompting  
  Each request declares intent explicitly.

- Local-first execution  
  No cloud dependency during inference.

- Transparent failure modes  
  The model is allowed to say "insufficient information" instead of guessing.

---

## Requirements

- Linux (tested on Arch Linux)
- Python 3.10+
- CMake
- A GGUF-compatible model (not included)

---

## Setup

Clone the repository:

git clone https://github.com/<your-username>/IGRISv0.1.git  
cd IGRISv0.1  

Initialize submodules:

git submodule update --init --recursive  

Build llama.cpp:

cd llama.cpp  
cmake -B build -DLLAMA_NATIVE=ON  
cmake --build build -j$(nproc)  

---

## Running the Assistant

From the project root:

python scripts/run_llm.py  

The system automatically injects:
- global rules
- persona
- task context
- user input

---

## Models

Model weights are NOT included in this repository.

Download a compatible .gguf model (for example, Mistral 7B) separately and place it
inside the models/ directory.

The models directory is intentionally ignored in Git.

---

## Third-Party Software

This project uses llama.cpp by Georgi Gerganov, licensed under the MIT License.

https://github.com/ggerganov/llama.cpp

---

## Disclaimer

This project is for educational and research purposes only.
Users are responsible for ethical and legal use.

---

## Status

Early-stage project (v0.1).
Expect changes, refactors, and experimentation.
