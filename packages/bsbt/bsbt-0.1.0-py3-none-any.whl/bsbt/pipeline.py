from .mock_data import get_mock_response

def run(input_text: str) -> str:
    """
    Phase 1: Returns a hardcoded antigen sequence for testing.
    Later will call a finetuned LLM via API.
    """
    if not input_text.strip():
        raise ValueError("Input must be a non-empty string.")

    # For now: just return hardcoded sequences
    return get_mock_response(input_text)
