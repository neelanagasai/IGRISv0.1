from base import MODELS, run_inference, get_output

SYSTEM_CONTEXT = """
You are a coding-focused assistant.
Respond only with correct, complete, and functional code.
Avoid explanations unless explicitly requested.
Prefer clarity, correctness, and simplicity.
""".strip()


def run_deepseek(task: str) -> str:
    """Run DeepSeek for code generation tasks."""
    prompt = f"{SYSTEM_CONTEXT}\n\nTask:\n{task}\n\nOutput:"
    result = run_inference(MODELS["deepseek"], prompt)
    return get_output(result)


if __name__ == "__main__":
    task = input("Enter coding task: ").strip()
    print(run_deepseek(task))
