import sys

try:
    from .base import ROOT, load_file, run_model
except ImportError:
    from base import ROOT, load_file, run_model

PERSONA_PATH = ROOT / "prompts/PERSONA.md"
TEMPLATE_PATH = ROOT / "prompts/FACE_SYSTEM.md"
PRIMER = "Concise, professional, neutral assistant."


def build_face_prompt(user_input: str) -> str:
    """Build the Face model prompt with persona and system context."""
    template = load_file(TEMPLATE_PATH)
    persona = load_file(PERSONA_PATH)
    return f"""{template}

=== PERSONA ===
{persona}

=== PRIMER ===
{PRIMER}

=== USER INPUT ===
{user_input}

=== RESPONSE ===
""".strip()


def run_face(user_input: str) -> dict:
    """Run Qwen as the face/response model. Returns full result dict."""
    prompt = build_face_prompt(user_input)
    return run_model("qwen", prompt)


def get_face_output(user_input: str) -> str:
    """Run Face model and return just the output string."""
    result = run_face(user_input)
    if result["error"]:
        return f"Error: {result['error']}"
    return result["output"]


if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Enter your prompt: ")
    result = run_face(user_input)
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print(result["output"])
