from base import ROOT, MODELS, load_file, run_inference, get_output

SYSTEM_PATH = ROOT / "prompts/DEEPSEEK_SYSTEM.md"


def run_deepseek(task: str) -> str:
    """Run DeepSeek for code generation tasks."""
    system_context = load_file(SYSTEM_PATH)
    prompt = f"{system_context}\n\nTask:\n{task}\n\nOutput:"
    result = run_inference(MODELS["deepseek"], prompt)
    return get_output(result)


if __name__ == "__main__":
    task = input("Enter coding task: ").strip()
    print(run_deepseek(task))
