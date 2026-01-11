"""
IGRIS Logging Infrastructure

Centralized logging for request/response tracking, intent classification,
and performance metrics.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from .base import ROOT
except ImportError:
    ROOT = Path(__file__).parent.parent

LOG_DIR = ROOT / "logs"


def ensure_log_dir():
    """Create logs directory if it doesn't exist."""
    LOG_DIR.mkdir(exist_ok=True)


def get_log_file() -> Path:
    """Get the log file path for today."""
    ensure_log_dir()
    return LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"


def log_request(
    user_input: str,
    intent: str,
    confidence: float,
    model: str,
    latency_ms: Optional[float],
    output: str,
    error: Optional[str] = None
) -> None:
    """
    Log a request/response cycle to the daily log file.
    
    Args:
        user_input: The original user input
        intent: Classified intent (CHAT, CODE, RECON, etc.)
        confidence: Confidence score from router (0.0-1.0)
        model: Model that handled the request
        latency_ms: Response time in milliseconds
        output: Model output (truncated for storage)
        error: Error message if any
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": user_input[:500],  
        "intent": intent,
        "confidence": round(confidence, 3),
        "model": model,
        "latency_ms": latency_ms,
        "output_length": len(output),
        "output_preview": output[:200] if output else "",
        "error": error,
    }
    
    log_file = get_log_file()
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def log_system_event(event: str, details: Optional[dict] = None) -> None:
    """
    Log a system event (startup, shutdown, errors, etc.)
    
    Args:
        event: Event type (STARTUP, SHUTDOWN, MODEL_OFFLINE, etc.)
        details: Additional event details
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "details": details or {},
    }
    
    log_file = get_log_file()
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_recent_logs(n: int = 10) -> list[dict]:
    """
    Get the most recent log entries.
    
    Args:
        n: Number of entries to retrieve
        
    Returns:
        List of log entries (newest first)
    """
    log_file = get_log_file()
    if not log_file.exists():
        return []
    
    entries = []
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    return entries[-n:][::-1]


def get_session_stats() -> dict:
    """
    Get statistics for today's session.
    
    Returns:
        Dict with request counts, avg latency, intent distribution
    """
    log_file = get_log_file()
    if not log_file.exists():
        return {"requests": 0, "errors": 0}
    
    entries = []
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                if "intent" in entry:  # Request entries have intent
                    entries.append(entry)
    
    if not entries:
        return {"requests": 0, "errors": 0}
    
    latencies = [e["latency_ms"] for e in entries if e.get("latency_ms")]
    intents = {}
    models = {}
    errors = 0
    
    for e in entries:
        intent = e.get("intent", "unknown")
        model = e.get("model", "unknown")
        intents[intent] = intents.get(intent, 0) + 1
        models[model] = models.get(model, 0) + 1
        if e.get("error"):
            errors += 1
    
    return {
        "requests": len(entries),
        "errors": errors,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
        "intents": intents,
        "models": models,
    }


def clear_today_logs() -> int:
    """
    Clear today's log file.
    
    Returns:
        Number of entries cleared
    """
    log_file = get_log_file()
    if not log_file.exists():
        return 0
    
    # Count entries before clearing
    count = 0
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                count += 1
    
    # Clear the file
    log_file.unlink()
    return count


if __name__ == "__main__":
    # Test logging
    log_system_event("TEST", {"message": "Logger test"})
    log_request(
        user_input="test input",
        intent="CHAT",
        confidence=0.95,
        model="qwen",
        latency_ms=150.5,
        output="test output"
    )
    print("Recent logs:", get_recent_logs(5))
    print("Session stats:", get_session_stats())
