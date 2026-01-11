try:
    from .base import ROOT, load_file, run_model
except ImportError:
    from base import ROOT, load_file, run_model

SYSTEM_PATH = ROOT / "prompts/DEEPSEEK_SYSTEM.md"


def run_deepseek(task: str) -> dict:
    """Run DeepSeek for code generation tasks. Returns full result dict."""
    system_context = load_file(SYSTEM_PATH)
    prompt = f"{system_context}\n\nTask:\n{task}\n\nOutput:"
    return run_model("deepseek", prompt)


def get_code_output(task: str) -> str:
    """Run DeepSeek and return just the output string."""
    result = run_deepseek(task)
    if result["error"]:
        return f"Error: {result['error']}"
    return result["output"]


if __name__ == "__main__":
    task = input("Enter coding task: ").strip()
    result = run_deepseek(task)
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print(result["output"])
