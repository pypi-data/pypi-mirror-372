"""
token_count: simple token counting for OpenAI, Anthropic, and Google (Gemini).

Public API:
- count_text_tokens(provider, model, text, **kwargs) -> int
- count_message_tokens(provider, model, messages, **kwargs) -> int

Message format (provider-agnostic):
messages = [
    {"role": "system"|"user"|"assistant", "content": "string content"},
    ...
]

Providers:
- provider="openai"     (local via tiktoken)
- provider="anthropic"  (via anthropic SDK / Messages.count_tokens)
- provider="google"     (via google-genai SDK / models.countTokens)

Notes:
- OpenAI (messages): counts mirror the OpenAI Cookbook heuristics for ChatML-style
  messages. They are considered estimates; exact accounting is reported by the API
  when you actually call it. (See refs in README / docstring.)
- Anthropic & Google: counts come from the providers' official count endpoints.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple
import warnings
import os

# -------------------
# OpenAI via tiktoken
# -------------------
import tiktoken


def _openai_encoding_for_model(model: str):
    """
    Returns a tiktoken encoding for a given OpenAI model name,
    with robust fallback to o200k_base (newer 4o family).
    """
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        # Conservative fallback; o200k_base covers gpt-4o/4o-mini families
        return tiktoken.get_encoding("o200k_base")


def _openai_count_text_tokens(model: str, text: str) -> int:
    enc = _openai_encoding_for_model(model)
    return len(enc.encode(text))


def _openai_num_tokens_from_messages(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-2024-08-06",
) -> int:
    """
    Estimate tokens used by a list of messages for OpenAI chat models.

    Source: OpenAI Cookbook guidance (kept minimal and in-sync with common models).
    Treat the result as an estimate; exact counts may change with model updates.

    Recognized sets below mirror the cookbook's approach:
    - gpt-3.5-turbo-0125, gpt-4-0613, gpt-4-32k-0613, gpt-4o-2024-08-06, gpt-4o-mini-2024-07-18
    - If you pass 'gpt-4o'/'gpt-4o-mini'/'gpt-4', we normalize to dated variants.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        warnings.warn("Model not found in tiktoken. Using o200k_base as fallback.")
        encoding = tiktoken.get_encoding("o200k_base")

    # Normalize as in the cookbook so tokens_per_message constants apply.
    if model in {
        "gpt-3.5-turbo-0125",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif "gpt-3.5-turbo" in model:
        warnings.warn(
            "gpt-3.5-turbo family evolves; assuming gpt-3.5-turbo-0125 accounting."
        )
        return _openai_num_tokens_from_messages(messages, "gpt-3.5-turbo-0125")
    elif "gpt-4o-mini" in model:
        warnings.warn(
            "gpt-4o-mini evolves; assuming gpt-4o-mini-2024-07-18 accounting."
        )
        return _openai_num_tokens_from_messages(messages, "gpt-4o-mini-2024-07-18")
    elif "gpt-4o" in model:
        warnings.warn(
            "gpt-4o evolves; assuming gpt-4o-2024-08-06 accounting."
        )
        return _openai_num_tokens_from_messages(messages, "gpt-4o-2024-08-06")
    elif "gpt-4" in model:
        warnings.warn("gpt-4 evolves; assuming gpt-4-0613 accounting.")
        return _openai_num_tokens_from_messages(messages, "gpt-4-0613")
    else:
        raise NotImplementedError(
            f"OpenAI message token estimation not implemented for model '{model}'. "
            "Use a known ChatGPT-family name (e.g., gpt-4o, gpt-4, gpt-3.5-turbo) "
            "or count raw text instead."
        )

    num_tokens = 0
    for message in messages:
        # Add structural overhead for each message
        num_tokens += tokens_per_message
        # Count tokens in each value
        for key, value in message.items():
            if not isinstance(value, str):
                raise TypeError("message values must be strings")
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    # every reply is primed with <|start|>assistant<|message|>
    num_tokens += 3
    return num_tokens


# -------------------
# Anthropic (Claude)
# -------------------

def _anthropic_imports():
    try:
        import anthropic  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "anthropic package not installed. pip install 'token-count[anthropic]'"
        ) from e
    return anthropic


def _split_system_and_non_system(messages: List[Dict[str, str]]) -> Tuple[Optional[str], List[Dict[str, str]]]:
    """
    Anthropic takes 'system' as a top-level field (not a message role).
    We collect any system messages and join them; return (system_text, non_system_messages).
    """
    sys_parts: List[str] = []
    out: List[Dict[str, str]] = []
    for m in messages:
        role = m.get("role")
        if role == "system":
            sys_parts.append(m.get("content", ""))
        else:
            if role not in ("user", "assistant"):
                raise ValueError("Anthropic messages must use roles 'user' or 'assistant' (plus top-level 'system').")
            out.append({"role": role, "content": m.get("content", "")})
    system_text = "\n\n".join(p for p in sys_parts if p.strip()) if sys_parts else None
    return system_text, out


def _anthropic_count_text_tokens(model: str, text: str, api_key: Optional[str] = None) -> int:
    anthropic = _anthropic_imports()
    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    resp = client.messages.count_tokens(
        model=model,
        messages=[{"role": "user", "content": text}],
    )
    # SDK returns TypedDict/obj with .input_tokens
    return int(resp.input_tokens)


def _anthropic_count_message_tokens(
    model: str,
    messages: List[Dict[str, str]],
    api_key: Optional[str] = None,
) -> int:
    anthropic = _anthropic_imports()
    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    system_text, conv = _split_system_and_non_system(messages)
    kwargs: Dict[str, Any] = {"model": model, "messages": conv}
    if system_text:
        kwargs["system"] = system_text
    resp = client.messages.count_tokens(**kwargs)
    return int(resp.input_tokens)


# -------------------
# Google (Gemini)
# -------------------

def _google_imports():
    """
    Prefer the official 'google-genai' client (from google import genai).
    As a convenience, we also try the older 'google.generativeai' if needed.
    """
    try:
        from google import genai  # type: ignore
        from google.genai import types as genai_types  # type: ignore
        return ("new", genai, genai_types)
    except Exception:
        # Fallback to older SDK if present
        try:
            import google.generativeai as old_genai  # type: ignore
            return ("old", old_genai, None)
        except Exception as e:
            raise RuntimeError(
                "Google GenAI SDK not installed. pip install 'token-count[google]'"
            ) from e


def _google_to_contents(messages: List[Dict[str, str]], genai_types) -> list:
    """
    Convert our message format to Google 'contents':
      - 'user' -> role='user'
      - 'assistant' -> role='model'
      - (system messages handled separately; if present and we can't pass
        as system_instruction, we ignore or prepend as user note)
    """
    contents = []
    for m in messages:
        role = m.get("role")
        text = m.get("content", "")
        if role == "system":
            # We'll pass separately if possible; skip here
            continue
        g_role = "user" if role == "user" else "model"
        if genai_types:
            contents.append(
                genai_types.Content(role=g_role, parts=[genai_types.Part(text=text)])
            )
        else:
            # old SDK expects dict-like
            contents.append({"role": g_role, "parts": [{"text": text}]})
    return contents


def _google_split_system(messages: List[Dict[str, str]]) -> Tuple[Optional[str], List[Dict[str, str]]]:
    sys_parts: List[str] = []
    out: List[Dict[str, str]] = []
    for m in messages:
        if m.get("role") == "system":
            sys_parts.append(m.get("content", ""))
        else:
            out.append(m)
    system_text = "\n\n".join(p for p in sys_parts if p.strip()) if sys_parts else None
    return system_text, out


def _google_count_text_tokens(model: str, text: str, api_key: Optional[str] = None) -> int:
    flavor, genai, genai_types = _google_imports()
    if flavor == "new":
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
        resp = client.models.count_tokens(model=model, contents=text)
        return int(resp.total_tokens)
    else:
        # old google.generativeai
        genai.configure(api_key=api_key)
        gm = genai.GenerativeModel(model)
        resp = gm.count_tokens(text)
        # old SDK returns an object with .total_tokens (or dict-like)
        return int(getattr(resp, "total_tokens", resp.get("total_tokens")))


def _google_count_message_tokens(
    model: str,
    messages: List[Dict[str, str]],
    api_key: Optional[str] = None,
) -> int:
    flavor, genai, genai_types = _google_imports()
    system_text, non_system = _google_split_system(messages)
    contents = _google_to_contents(non_system, genai_types)

    if flavor == "new":
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
        # If possible, add system instruction via config (available in new SDK).
        config = None
        if system_text and genai_types is not None:
            try:
                config = genai_types.GenerateContentConfig(system_instruction=system_text)
            except Exception:
                # If the installed version doesn't expose this, omit it.
                pass
        if config is not None:
            resp = client.models.count_tokens(model=model, contents=contents, config=config)
        else:
            # If we couldn't set system instruction via config, prepend as user text
            # to keep counting closer to reality.
            if system_text:
                extra = genai_types.Content(role="user", parts=[genai_types.Part(text=f"[system]\n{system_text}")])
                contents = [extra] + contents
            resp = client.models.count_tokens(model=model, contents=contents)
        return int(resp.total_tokens)
    else:
        # old google.generativeai
        genai.configure(api_key=api_key)
        gm = genai.GenerativeModel(model, system_instruction=system_text if system_text else None)
        # old SDK accepts either a list of contents or a chat session; pass contents
        resp = gm.count_tokens(contents)
        return int(getattr(resp, "total_tokens", resp.get("total_tokens")))


# -------------------
# Public API
# -------------------

def count_text_tokens(
    provider: str,
    model: str,
    text: str,
    **kwargs: Any,
) -> int:
    """
    Count tokens for a plain text string.

    Args:
        provider: "openai" | "anthropic" | "google"
        model: provider-specific model id
        text: text to count tokens for
        **kwargs: provider-specific arguments (e.g., api_key)

    Returns:
        int: token count

    Raises:
        ValueError: if provider is unsupported
        RuntimeError: if required SDK is not installed
    """
    if provider == "openai":
        return _openai_count_text_tokens(model, text)
    elif provider == "anthropic":
        api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        return _anthropic_count_text_tokens(model, text, api_key)
    elif provider == "google":
        api_key = kwargs.get("api_key") or os.getenv("GOOGLE_API_KEY")
        return _google_count_text_tokens(model, text, api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def count_message_tokens(
    provider: str,
    model: str,
    messages: List[Dict[str, str]],
    **kwargs: Any,
) -> int:
    """
    Count tokens for a list of messages.

    Args:
        provider: "openai" | "anthropic" | "google"
        model: provider-specific model id
        messages: list of message dicts with 'role' and 'content' keys
        **kwargs: provider-specific arguments (e.g., api_key)

    Returns:
        int: token count

    Raises:
        ValueError: if provider is unsupported or message format is invalid
        RuntimeError: if required SDK is not installed
        TypeError: if message values are not strings (OpenAI)
    """
    if provider == "openai":
        return _openai_num_tokens_from_messages(messages, model)
    elif provider == "anthropic":
        api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        return _anthropic_count_message_tokens(model, messages, api_key)
    elif provider == "google":
        api_key = kwargs.get("api_key") or os.getenv("GOOGLE_API_KEY")
        return _google_count_message_tokens(model, messages, api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


# Expose public API
__all__ = ["count_text_tokens", "count_message_tokens"]
