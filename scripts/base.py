"""
Shared base module for LLM inference.
Provides common utilities and a unified interface for running models.
"""

import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
LLAMA_CLI = ROOT / "llama.cpp/build/bin/llama-cli"


@dataclass
class ModelConfig:
    """Configuration for a model."""

    name: str
    model_path: Path
    context_size: int = 2048
    threads: int = 8
    temperature: float = 0.7
    top_p: float = 0.95
    repeat_penalty: float = 1.1
    timeout: int = 120
    extra_args: list[str] = field(default_factory=list)


# Pre-defined model configurations
MODELS = {
    "mistral": ModelConfig(
        name="mistral",
        model_path=ROOT / "models/mistral-7b-instruct-v0.2.Q5_K_M.gguf",
        context_size=2048,
        temperature=0.2,
        extra_args=[
            "--reverse-prompt", "}"
        ],
    ),
    "deepseek": ModelConfig(
        name="deepseek",
        model_path=ROOT / "models/deepseek-coder-6.7b-instruct-q4_k_m.gguf",
        context_size=4096,
        temperature=0.2,
        extra_args=[
            "--reverse-prompt", "```"
        ],
    ),
    "qwen": ModelConfig(
        name="qwen",
        model_path=ROOT / "models/qwen2.5-3b-instruct-q4_k_m.gguf",
        context_size=2048,
        temperature=0.7,
    ),
}


@lru_cache(maxsize=8)
def load_file(path: Path) -> str:
    """Load and cache a text file."""
    return path.read_text().strip()


def build_command(config: ModelConfig, prompt: str) -> list[str]:
    """Build the llama-cli command with given config and prompt."""

    if __debug__:
        print(f"[DEBUG] Running model: {config.name} with prompt length {len(prompt)}")

    cmd = [
        str(LLAMA_CLI),
        "-m", str(config.model_path),
        "--prompt", prompt,
        "--no-display-prompt",
        "-c", str(config.context_size),
        "-t", str(config.threads),
        "-n", "256", 
        "--temp", str(config.temperature),
        "--top-p", str(config.top_p),
        "--repeat-penalty", str(config.repeat_penalty),
        *config.extra_args,
    ]
    return cmd


def run_inference(
    config: ModelConfig,
    prompt: str,
    capture_output: bool = True,
    timeout: Optional[int] = None,
) -> subprocess.CompletedProcess:
    """
    Run inference with the given model config and prompt.
    Hardened against timeouts, crashes, and invalid execution.
    """

    if not config.model_path.exists():
        raise FileNotFoundError(f"[{config.name}] Model not found: {config.model_path}")

    if not LLAMA_CLI.exists():
        raise FileNotFoundError(f"llama-cli not found: {LLAMA_CLI}")

    cmd = build_command(config, prompt)

    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=timeout or config.timeout,
            check=False,
        )

        # Non-zero exit - still returning something
        if result.returncode != 0:
            raise RuntimeError(
                f"[{config.name}] Non-zero exit ({result.returncode}). "
                f"stderr: {result.stderr.strip()[:500]}"
            )

        return result

    except subprocess.TimeoutExpired as e:
        raise TimeoutError(
            f"[{config.name}] Inference timed out after {timeout or config.timeout}s"
        ) from e

    except OSError as e:
        # Covers execution errors like permissions, binary failure, etc.
        raise RuntimeError(
            f"[{config.name}] Execution failure: {e}"
        ) from e


def get_output(result: subprocess.CompletedProcess) -> str:
    """
    Extract clean output from a completed inference.
    Prefers stdout, falls back to stderr.
    """
    output = (result.stdout or "").strip()
    if output:
        return output

    return (result.stderr or "").strip()


def run_model(model_name: str, prompt: str) -> str:
    """
    High-level helper to run a model by name and return the output.

    Args:
        model_name: One of 'mistral', 'deepseek', 'qwen'
        prompt: The prompt to send

    Returns:
        The model's text output
    """
    config = MODELS[model_name]
    result = run_inference(config, prompt)
    return get_output(result)
