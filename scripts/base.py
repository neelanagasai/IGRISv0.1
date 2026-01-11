import time
import requests
import hashlib
import json
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Generator, Callable
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Simple in-memory cache for responses
_response_cache: Dict[str, dict] = {}
MAX_CACHE_SIZE = 50


@dataclass
class ModelConfig:
    name: str
    url: str
    max_tokens: int = 256
    temperature: float = 0.7
    timeout: int = 60
    stop: List[str] = field(default_factory=list)
    top_p: float = 0.9
    repeat_penalty: float = 1.1


MODELS: Dict[str, ModelConfig] = {
    "qwen": ModelConfig(
        name="qwen",
        url="http://127.0.0.1:8001/completion",
        temperature=0.7,
        max_tokens=256,
        stop=["<|im_end|>", "<|im_start|>", "\n\nUser:", "\n\nHuman:"],
        top_p=0.9,
        repeat_penalty=1.1,
    ),
    "deepseek": ModelConfig(
        name="deepseek",
        url="http://127.0.0.1:8002/completion",
        temperature=0.2,  # Low temp for precise code
        max_tokens=1024,  # Longer for code output
        stop=["\n\nTask:", "\n\nOutput:", "```\n\n"],
        top_p=0.95,
        repeat_penalty=1.0,
    ),
    "mistral": ModelConfig(
        name="mistral",
        url="http://127.0.0.1:8003/completion",
        temperature=0.3,
        max_tokens=256,
        stop=["</s>", "[INST]", "[/INST]"],
    ),
}


def model_health(model_name: str) -> bool:
    cfg = MODELS[model_name]
    health_url = cfg.url.replace("/completion", "/health")
    try:
        r = requests.get(health_url, timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False


def run_model(model_name: str, prompt: str) -> dict:
    cfg = MODELS[model_name]

    if not model_health(model_name):
        return {
            "model": model_name,
            "output": "",
            "latency_ms": None,
            "error": "MODEL_OFFLINE",
        }

    payload = {
        "prompt": prompt,
        "n_predict": cfg.max_tokens,
        "temperature": cfg.temperature,
        "top_p": cfg.top_p,
        "repeat_penalty": cfg.repeat_penalty,
        "stop": cfg.stop,
    }

    start = time.perf_counter()
    r = requests.post(cfg.url, json=payload, timeout=cfg.timeout)
    latency = round((time.perf_counter() - start) * 1000, 2)

    r.raise_for_status()
    data = r.json()

    return {
        "model": model_name,
        "output": data.get("content", "").strip(),
        "latency_ms": latency,
        "error": None,
    }


def _cache_key(model_name: str, prompt: str) -> str:
    """Generate a cache key for a prompt."""
    content = f"{model_name}:{prompt}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cached(model_name: str, prompt: str) -> Optional[dict]:
    """Get cached response if available."""
    key = _cache_key(model_name, prompt)
    return _response_cache.get(key)


def set_cached(model_name: str, prompt: str, response: dict) -> None:
    """Cache a response."""
    global _response_cache
    # Evict oldest entries if cache is full
    if len(_response_cache) >= MAX_CACHE_SIZE:
        # Remove first 10 entries (simple FIFO)
        keys = list(_response_cache.keys())[:10]
        for k in keys:
            del _response_cache[k]
    
    key = _cache_key(model_name, prompt)
    _response_cache[key] = response


def clear_cache() -> int:
    """Clear all cached responses. Returns count of cleared items."""
    global _response_cache
    count = len(_response_cache)
    _response_cache = {}
    return count


def run_model_streaming(
    model_name: str, 
    prompt: str, 
    on_token: Callable[[str], None]
) -> dict:
    """
    Run model with streaming output.
    Calls on_token(text) for each token received.
    """
    cfg = MODELS[model_name]

    if not model_health(model_name):
        return {
            "model": model_name,
            "output": "",
            "latency_ms": None,
            "error": "MODEL_OFFLINE",
        }

    payload = {
        "prompt": prompt,
        "n_predict": cfg.max_tokens,
        "temperature": cfg.temperature,
        "top_p": cfg.top_p,
        "repeat_penalty": cfg.repeat_penalty,
        "stop": cfg.stop,
        "stream": True,
    }

    start = time.perf_counter()
    full_output = []
    
    try:
        with requests.post(cfg.url, json=payload, timeout=cfg.timeout, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            token = chunk.get('content', '')
                            if token:
                                full_output.append(token)
                                on_token(token)
                        except json.JSONDecodeError:
                            continue
    except requests.RequestException as e:
        return {
            "model": model_name,
            "output": "".join(full_output),
            "latency_ms": None,
            "error": str(e),
        }

    latency = round((time.perf_counter() - start) * 1000, 2)
    
    return {
        "model": model_name,
        "output": "".join(full_output).strip(),
        "latency_ms": latency,
        "error": None,
    }


def load_file(path: Path) -> str:
    """Load text content from a file."""
    return path.read_text().strip()
