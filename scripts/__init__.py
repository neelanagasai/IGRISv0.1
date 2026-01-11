"""
IGRIS Scripts Package - Optimized 2-Model Architecture
"""

from .base import (
    ROOT,
    MODELS,
    ModelConfig,
    load_file,
    run_model,
    run_model_streaming,
    model_health,
    get_cached,
    set_cached,
    clear_cache,
)
from .deepseek import run_deepseek, get_code_output
from .qwen import run_face, get_face_output
from .orchestrator import orchestrate, status, fast_route, clear_history
from .logger import log_request, log_system_event, get_session_stats, clear_today_logs
from .formatting import format_output, print_streaming, print_status

__all__ = [
    "ROOT",
    "MODELS",
    "ModelConfig",
    "load_file",
    "run_model",
    "run_model_streaming",
    "model_health",
    "get_cached",
    "set_cached",
    "clear_cache",
    "run_deepseek",
    "get_code_output",
    "run_face",
    "get_face_output",
    "orchestrate",
    "status",
    "fast_route",
    "clear_history",
    "log_request",
    "log_system_event",
    "get_session_stats",
    "format_output",
    "print_streaming",
    "print_status",
]
