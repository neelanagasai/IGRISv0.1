import json
from base import ROOT, MODELS, load_file, run_inference
import re, json

SYSTEM_PROMPT = ROOT / "prompts/MISTRAL_SYSTEM.md"
SYSTEM_RULES = ROOT / "SYSTEM_RULES.md"

def extract_json(text: str) -> dict:
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group())


def build_prompt(user_input: str) -> str:
    """Build the Mistral prompt with system context."""
    return f"""
=== GLOBAL RULES ===
{load_file(SYSTEM_RULES)}

=== SYSTEM ROLE ===
{load_file(SYSTEM_PROMPT)}

=== USER INPUT ===
{user_input}

=== OUTPUT (STRICT JSON ONLY) ===
""".strip()


def run_mistral(user_input: str) -> dict:
    """Run Mistral for intent classification. Returns parsed JSON."""
    prompt = build_prompt(user_input)
    result = run_inference(MODELS["mistral"], prompt)
    output = result.stdout.strip()

    try:
        return extract_json(output)
    except json.JSONDecodeError:
        return {
            "intent": "ambiguous",
            "confidence": 0.0,
            "error": "Invalid JSON from Mistral",
            "raw_output": output
        }


if __name__ == "__main__":
    user_input = input("Enter query: ").strip()
    result = run_mistral(user_input)
    print(json.dumps(result, indent=2))
