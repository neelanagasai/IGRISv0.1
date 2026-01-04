from qwen import run_face
from mistral import run_mistral
from deepseek import run_deepseek
from datetime import datetime
import time


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def orchestrate(user_input: str) -> str:
    """
    Main orchestration logic for IGRIS.
    """

    log("Face: received user input")

    # Step 1: Let Mistral analyze and decide
    log("Mistral: analyzing intent")
    t0 = time.time()
    decision = run_mistral(user_input)
    t1 = time.time()

    intent = decision.get("intent", "ambiguous")
    confidence = decision.get("confidence", 0.0)

    log(f"Mistral: intent={intent}, confidence={confidence:.2f}, time={t1 - t0:.2f}s")

    # Step 2: Handle ambiguous / low confidence
    if intent == "ambiguous" or confidence < 0.6:
        log("Face: requesting clarification")
        return run_face("Your request is unclear. Please clarify what you want to do.")

    # Step 3: Heavy coding → DeepSeek
    if intent == "heavy_code":
        task = decision.get("task", user_input)

        log("DeepSeek: executing task")
        t0 = time.time()
        result = run_deepseek(task)
        t1 = time.time()

        log(f"DeepSeek: completed execution in {t1 - t0:.2f}s")
        log("Face: formatting response")
        return run_face(result)

    # Step 4: Light tasks → Face
    log("Face: handling task directly")
    return run_face(user_input)


def main():
    log("IGRIS online. Awaiting input.")

    while True:
        try:
            user_input = input(">> ").strip()
            if not user_input:
                continue

            response = orchestrate(user_input)
            print(response)

        except KeyboardInterrupt:
            log("IGRIS shutting down.")
            break


if __name__ == "__main__":
    main()
