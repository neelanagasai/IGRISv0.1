"""
IGRIS Orchestrator - Optimized Two-Model Architecture

Uses fast heuristic routing with two specialized models:
- Qwen: General queries, conversation, explanations
- DeepSeek: Code generation, debugging, technical tasks

Features:
- Streaming output (see responses as they generate)
- Response caching (instant for repeated queries)
- Syntax highlighting for code blocks
- Conversation history for multi-turn context
"""

from datetime import datetime
import requests

try:
    from .base import (
        run_model, run_model_streaming, model_health, MODELS, ROOT, load_file,
        get_cached, set_cached, clear_cache
    )
    from .logger import log_request, log_system_event, get_session_stats, clear_today_logs
    from .formatting import (
        format_output, print_streaming, print_status, print_error,
        print_latency, print_success, RICH_AVAILABLE
    )
except ImportError:
    from base import (
        run_model, run_model_streaming, model_health, MODELS, ROOT, load_file,
        get_cached, set_cached, clear_cache
    )
    from logger import log_request, log_system_event, get_session_stats, clear_today_logs
    from formatting import (
        format_output, print_streaming, print_status, print_error,
        print_latency, print_success, RICH_AVAILABLE
    )


# System prompts
FACE_SYSTEM = ROOT / "prompts/FACE_SYSTEM.md"
DEEPSEEK_SYSTEM = ROOT / "prompts/DEEPSEEK_SYSTEM.md"

# Enable streaming by default
STREAMING_ENABLED = True

# Code-related keywords for fast heuristic routing
CODE_KEYWORDS = {
    "code", "script", "function", "program", "debug", "fix", "implement",
    "write a", "create a", "build a", "def ", "class ", "import ", "return",
    "compile", "error", "bug", "exception", "traceback", "syntax",
    "python", "javascript", "rust", "bash", "sql", "html", "css",
    "algorithm", "data structure", "api", "endpoint", "database", "optimize"
}

# Non-code indicators (overrides code keywords if present)
NON_CODE_INDICATORS = {
    "explain", "what is", "how does", "why", "describe", "summarize",
    "tell me about", "difference between", "compare", "help me understand",
}
# Conversation history for context
MAX_HISTORY = 4  
conversation_history: list[tuple[str, str]] = []


def build_prompt(user_input: str, model: str, include_history: bool = True) -> str:
    """Build a properly formatted prompt for the target model."""
    if model == "qwen":
        system = load_file(FACE_SYSTEM)
        
        # Build conversation with history
        prompt = f"<|im_start|>system\n{system}\n<|im_end|>\n"
        
        # Add recent history for context
        if include_history and conversation_history:
            for user_msg, assistant_msg in conversation_history[-MAX_HISTORY:]:
                prompt += f"<|im_start|>user\n{user_msg}\n<|im_end|>\n"
                prompt += f"<|im_start|>assistant\n{assistant_msg}\n<|im_end|>\n"
        
        # Add current message
        prompt += f"<|im_start|>user\n{user_input}\n<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"
        return prompt
        
    elif model == "deepseek":
        system = load_file(DEEPSEEK_SYSTEM)
        return f"""{system}

Task:
{user_input}

Output:
"""
    else:
        return user_input


def add_to_history(user_input: str, response: str) -> None:
    """Add a conversation turn to history."""
    # Don't add very short exchanges or errors
    if len(response) > 10 and not response.startswith("Error"):
        conversation_history.append((user_input, response))
        # Trim to max size
        while len(conversation_history) > MAX_HISTORY:
            conversation_history.pop(0)


def clear_history() -> None:
    """Clear conversation history."""
    conversation_history.clear()


def fast_route(user_input: str) -> str:
    """
    Fast heuristic routing without model inference.
    Returns: 'code', 'general', or 'ambiguous'
    """
    lower = user_input.lower()
    
    # Check for explicit non-code requests first
    for indicator in NON_CODE_INDICATORS:
        if indicator in lower:
            return "general"
    
    # Check for code keywords
    code_score = sum(1 for kw in CODE_KEYWORDS if kw in lower)
    
    if code_score >= 2:
        return "code"
    elif code_score == 1:
        return "ambiguous"  # Could go either way
    else:
        return "general"


def status() -> str:
    """Check health of model endpoints."""
    lines = ["[IGRIS STATUS]"]
    
    # Only check the 2 models we actually use
    active_models = ["qwen", "deepseek"]
    for name in active_models:
        if name in MODELS:
            state = "ONLINE" if model_health(name) else "OFFLINE"
            lines.append(f"  {name}: {state}")
    
    stats = get_session_stats()
    if stats["requests"] > 0:
        lines.append(f"\n[SESSION STATS]")
        lines.append(f"  Requests: {stats['requests']}")
        lines.append(f"  Errors: {stats['errors']}")
        if stats.get("avg_latency_ms"):
            lines.append(f"  Avg Latency: {stats['avg_latency_ms']}ms")
    
    return "\n".join(lines)


def orchestrate(user_input: str) -> str:
    """
    Optimized orchestration with fast routing.
    
    Flow:
    1. Fast heuristic check (no model call)
    2. Route to appropriate model
    3. Log and return response
    """
    # Step 1: Fast route
    route = fast_route(user_input)
    print(f"[IGRIS] Route: {route}")
    
    # Step 2: Select model based on route
    if route == "code":
        target_model = "deepseek"
        intent = "CODE"
    else:
        # Both 'general' and 'ambiguous' go to Qwen
        target_model = "qwen"
        intent = "GENERAL" if route == "general" else "AMBIGUOUS"
    
    # Step 3: Build proper prompt
    prompt = build_prompt(user_input, target_model)
    
    # Step 4: Check cache first
    cached = get_cached(target_model, prompt)
    if cached:
        print_status(f"[CACHE HIT] {target_model}", "dim green")
        output = cached["output"]
        log_request(
            user_input=user_input,
            intent=intent,
            confidence=1.0,
            model=target_model,
            latency_ms=0,
            output=output
        )
        # Add to history for context
        if target_model == "qwen":
            add_to_history(user_input, output)
        return output
    
    print_status(f"[IGRIS] Using {target_model}...", "dim blue")
    
    # Step 5: Call the model (streaming or regular)
    try:
        if STREAMING_ENABLED:
            # Streaming mode - print tokens as they arrive
            response = run_model_streaming(target_model, prompt, print_streaming)
            print()  # Newline after streaming
        else:
            response = run_model(target_model, prompt)
    except requests.exceptions.Timeout:
        print_error(f"{target_model.capitalize()} timed out.")
        log_request(
            user_input=user_input,
            intent=intent,
            confidence=1.0,
            model=target_model,
            latency_ms=None,
            output="",
            error="TIMEOUT"
        )
        return ""
    except requests.RequestException as e:
        print_error(f"{target_model.capitalize()} error: {e}")
        log_request(
            user_input=user_input,
            intent=intent,
            confidence=1.0,
            model=target_model,
            latency_ms=None,
            output="",
            error=str(e)
        )
        return ""
    
    if response["error"]:
        # Fallback: try the other model
        fallback_model = "qwen" if target_model == "deepseek" else "deepseek"
        print_status(f"[IGRIS] {target_model} offline, trying {fallback_model}...", "yellow")
        
        try:
            fallback_prompt = build_prompt(user_input, fallback_model)
            if STREAMING_ENABLED:
                response = run_model_streaming(fallback_model, fallback_prompt, print_streaming)
                print()
            else:
                response = run_model(fallback_model, fallback_prompt)
            if not response["error"]:
                target_model = fallback_model
        except requests.RequestException:
            pass
        
        if response["error"]:
            print_error("All models offline.")
            log_request(
                user_input=user_input,
                intent=intent,
                confidence=1.0,
                model=target_model,
                latency_ms=None,
                output="",
                error=response["error"]
            )
            return ""
    
    # Step 6: Cache successful response
    output = response["output"]
    latency = response["latency_ms"]
    
    set_cached(target_model, prompt, response)
    print_latency(target_model, latency)
    
    log_request(
        user_input=user_input,
        intent=intent,
        confidence=1.0,
        model=target_model,
        latency_ms=latency,
        output=output
    )
    
    # Add to conversation history for context (only for general chat)
    if target_model == "qwen":
        add_to_history(user_input, output)
    
    # For non-streaming mode, return output (streaming already printed)
    if not STREAMING_ENABLED:
        return output
    return ""


def main():
    """Main REPL loop."""
    global STREAMING_ENABLED
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    print_status(f"[{timestamp}] IGRIS online", "bold green")
    print("Features: streaming, caching, syntax highlighting")
    print("Commands: /status, /stats, /clear, /cache, /stream, /reset, /quit")
    
    log_system_event("STARTUP", {"version": "1.0", "time": timestamp})
    
    while True:
        try:
            user_input = input(">> ").strip()
            if not user_input:
                continue

            # Built-in commands
            if user_input == "/status":
                print(status())
                continue
            
            if user_input == "/stats":
                stats = get_session_stats()
                print(f"[SESSION] {stats}")
                continue
            
            if user_input == "/clear":
                clear_history()
                print_success("[IGRIS] Conversation history cleared.")
                continue
            
            if user_input == "/cache":
                count = clear_cache()
                print_success(f"[IGRIS] Cleared {count} cached responses.")
                continue
            
            if user_input == "/stream":
                STREAMING_ENABLED = not STREAMING_ENABLED
                state = "ON" if STREAMING_ENABLED else "OFF"
                print_status(f"[IGRIS] Streaming: {state}", "cyan")
                continue
            
            if user_input == "/history":
                if conversation_history:
                    print(f"[HISTORY] {len(conversation_history)} turns stored")
                    for i, (u, a) in enumerate(conversation_history):
                        print(f"  {i+1}. User: {u[:50]}...")
                else:
                    print("[HISTORY] Empty")
                continue
            
            if user_input == "/reset":
                # Clear everything: history, cache, and today's logs
                clear_history()
                cache_count = clear_cache()
                log_count = clear_today_logs()
                print_success(f"[IGRIS] Reset complete: {log_count} log entries cleared, {cache_count} cached responses cleared, history cleared.")
                continue
            
            if user_input in ("/quit", "/exit"):
                log_system_event("SHUTDOWN", {"reason": "user_exit"})
                print_status("Exiting IGRIS.", "yellow")
                break
            
            if user_input == "/help":
                print("""
Commands:
  /status   - Check model health
  /stats    - Session statistics
  /clear    - Clear conversation history
  /cache    - Clear response cache
  /stream   - Toggle streaming mode
  /history  - Show conversation history
  /reset    - Reset all (clear logs, cache, history)
  /help     - Show this help
  /quit     - Exit IGRIS
""")
                continue

            response = orchestrate(user_input)
            if response:
                # Non-streaming mode - format and print
                format_output(response)

        except KeyboardInterrupt:
            log_system_event("SHUTDOWN", {"reason": "interrupt"})
            print("\nExiting IGRIS.")
            break


if __name__ == "__main__":
    main()
