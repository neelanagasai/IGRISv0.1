import sys
from base import ROOT, MODELS, load_file, run_inference, get_output

PERSONA_PATH = ROOT / "PERSONA.md"
TEMPLATE_PATH = ROOT / "prompts/face_prompt.txt"
PRIMER = "Concise, professional, neutral assistant."


def run_face(user_input: str) -> str:
    """Run Qwen as the face/response model."""
    prompt = load_file(TEMPLATE_PATH).format(
        persona=load_file(PERSONA_PATH),
        primer=PRIMER,
        user_input=user_input
    )
    result = run_inference(MODELS["qwen"], prompt)
    return get_output(result)


if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Enter your prompt: ")
    print(run_face(user_input))
