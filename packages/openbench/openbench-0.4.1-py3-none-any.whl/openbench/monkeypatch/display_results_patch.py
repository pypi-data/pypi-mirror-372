"""
Monkey patch for inspect_ai display results to show "bench eval-retry" instead of "inspect eval-retry".

Usage:
    from openbench.monkeypatch.display_results_patch import patch_display_results
    patch_display_results()

Call this before invoking inspect_ai.eval_retry().
"""


def patch_display_results():
    """
    Monkey patch inspect_ai display functions to replace "inspect eval-retry" with "bench eval-retry".
    """
    try:
        import inspect_ai._display.core.results as results_mod

        # Store original function
        original_task_interrupted = results_mod.task_interrupted

        def custom_task_interrupted(profile, samples_completed):  # type: ignore
            # Call original function
            result = original_task_interrupted(profile, samples_completed)

            # If result is a string, replace the text
            if isinstance(result, str):
                result = result.replace("inspect eval-retry", "bench eval-retry")
            # If it's a Text object from rich, we need to handle it differently
            elif hasattr(result, "_text") and isinstance(result._text, list):
                # Rich Text objects store segments internally
                for i, segment in enumerate(result._text):
                    if isinstance(segment, tuple) and len(segment) >= 1:
                        text = segment[0]
                        if isinstance(text, str) and "inspect eval-retry" in text:
                            # Create a new segment with replaced text
                            new_text = text.replace(
                                "inspect eval-retry", "bench eval-retry"
                            )
                            result._text[i] = (new_text,) + segment[1:]

            return result

        # Apply patch
        results_mod.task_interrupted = custom_task_interrupted

    except (ImportError, AttributeError):
        # If inspect_ai is not installed or the module structure changed, silently continue
        pass
