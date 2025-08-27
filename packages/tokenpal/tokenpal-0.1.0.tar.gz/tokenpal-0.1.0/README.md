# token-count

A simple, practical Python package for counting tokens across OpenAI, Anthropic, and Google (Gemini) models using their official tokenizers and APIs.

## Features

- **OpenAI**: Local, offline token counting via `tiktoken` (official tokenizer)
- **Anthropic**: Official `messages.count_tokens` API
- **Google (Gemini)**: Official `models.countTokens` via `google-genai` SDK
- Provider-agnostic message format
- Robust model name handling with fallbacks
- Optional dependencies for each provider

## Installation

```bash
# Basic installation (OpenAI support only)
pip install token-count

# With Anthropic support
pip install 'token-count[anthropic]'

# With Google support  
pip install 'token-count[google]'

# With all providers
pip install 'token-count[anthropic,google]'
