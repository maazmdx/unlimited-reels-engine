"""
engine/llm_router.py - Zero-Dependency Multi-Provider LLM Waterfall Router

Supports:
0. Custom Gateway: LLM_GATEWAY_URL / LLM_GATEWAY_KEY / LLM_GATEWAY_MODEL (OmniRoute / FreeLLMAPI)
1. Google Gemini: gemini-2.5-flash ONLY via GEMINI_API_KEY (zero weak flash-lite fallbacks)
2. Groq Cloud: llama-3.3-70b-versatile via GROQ_API_KEY
3. OpenRouter: google/gemma-4-31b-it:free -> openrouter/free via OPENROUTER_API_KEY
4. Mistral AI: mistral-large-latest -> mistral-small-latest via MISTRAL_API_KEY
5. LLM7.io: keyless free fallback with model 'default'

Standard library urllib.request ONLY - Zero extra pip dependencies.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List


def _get_secret(key: str) -> Optional[str]:
    """Retrieves secret from environment or Kaggle UserSecretsClient fallback."""
    val = os.environ.get(key)
    if val and str(val).strip():
        return str(val).strip()
    try:
        from kaggle_secrets import UserSecretsClient
        s = UserSecretsClient().get_secret(key)
        if s and str(s).strip():
            os.environ[key] = str(s).strip()
            return str(s).strip()
    except Exception:
        pass
    return None


def _post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: float = 35.0) -> Dict[str, Any]:
    """Posts JSON payload using standard urllib.request with clean timeout handling."""
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        resp_body = response.read().decode("utf-8")
        return json.loads(resp_body)


def _call_custom_gateway(
    prompt: str,
    system_prompt: str,
    json_mode: bool,
    temperature: float,
    timeout: float = 30.0
) -> Optional[str]:
    gateway_url = _get_secret("LLM_GATEWAY_URL")
    if not gateway_url:
        return None

    gateway_key = _get_secret("LLM_GATEWAY_KEY") or "dummy-key"
    model_name = _get_secret("LLM_GATEWAY_MODEL") or "gemini-2.5-flash"

    # Normalize endpoint URL
    clean_url = gateway_url.rstrip("/")
    if not clean_url.endswith("/chat/completions"):
        clean_url = f"{clean_url}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {gateway_key}",
        "User-Agent": "AntigravityLLMRouter/1.0",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload: Dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    t0 = time.time()
    try:
        res = _post_json(clean_url, payload, headers, timeout=timeout)
        choices = res.get("choices", [])
        if choices:
            text = choices[0].get("message", {}).get("content", "")
            elapsed = time.time() - t0
            print(f"✨ [LLMRouter] gateway/{model_name} succeeded in {elapsed:.2f}s ({len(text)} chars)")
            return text
    except Exception as e:
        print(f"⚠️ [LLMRouter] gateway/{model_name} failed: {e}")
    return None


def _call_gemini_25_flash(
    prompt: str,
    system_prompt: str,
    json_mode: bool,
    temperature: float,
    timeout: float = 35.0
) -> Optional[str]:
    api_key = _get_secret("GEMINI_API_KEY")
    if not api_key:
        return None

    # gemini-2.5-flash ONLY
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AntigravityLLMRouter/1.0",
    }

    contents = [{"role": "user", "parts": [{"text": prompt}]}]
    generation_config: Dict[str, Any] = {
        "temperature": temperature,
    }
    if json_mode:
        generation_config["responseMimeType"] = "application/json"

    payload: Dict[str, Any] = {
        "contents": contents,
        "generationConfig": generation_config,
    }
    if system_prompt:
        payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

    t0 = time.time()
    try:
        res = _post_json(url, payload, headers, timeout=timeout)
        candidates = res.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                text = parts[0].get("text", "")
                elapsed = time.time() - t0
                print(f"✨ [LLMRouter] gemini/gemini-2.5-flash succeeded in {elapsed:.2f}s ({len(text)} chars)")
                return text
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")[:160]
        except Exception:
            pass
        print(f"⚠️ [LLMRouter] gemini/gemini-2.5-flash HTTP {e.code}: {body}")
    except Exception as e:
        print(f"⚠️ [LLMRouter] gemini/gemini-2.5-flash failed: {e}")

    return None


def _call_openai_compat(
    url: str,
    api_key: str,
    model: str,
    prompt: str,
    system_prompt: str,
    json_mode: bool,
    temperature: float,
    provider_name: str,
    timeout: float = 30.0
) -> Optional[str]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}" if api_key else "Bearer none",
        "User-Agent": "AntigravityLLMRouter/1.0",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    t0 = time.time()
    try:
        res = _post_json(url, payload, headers, timeout=timeout)
        choices = res.get("choices", [])
        if choices:
            text = choices[0].get("message", {}).get("content", "")
            elapsed = time.time() - t0
            print(f"✨ [LLMRouter] {provider_name}/{model} succeeded in {elapsed:.2f}s ({len(text)} chars)")
            return text
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")[:160]
        except Exception:
            pass
        print(f"⚠️ [LLMRouter] {provider_name}/{model} HTTP {e.code}: {body}")
    except Exception as e:
        print(f"⚠️ [LLMRouter] {provider_name}/{model} failed: {e}")

    return None


def _call_groq(
    prompt: str,
    system_prompt: str,
    json_mode: bool,
    temperature: float,
    timeout: float = 30.0
) -> Optional[str]:
    api_key = _get_secret("GROQ_API_KEY")
    if not api_key:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    return _call_openai_compat(
        url=url,
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        prompt=prompt,
        system_prompt=system_prompt,
        json_mode=json_mode,
        temperature=temperature,
        provider_name="groq",
        timeout=timeout,
    )


def _call_openrouter(
    prompt: str,
    system_prompt: str,
    json_mode: bool,
    temperature: float,
    timeout: float = 30.0
) -> Optional[str]:
    api_key = _get_secret("OPENROUTER_API_KEY")
    if not api_key:
        return None
    url = "https://openrouter.ai/api/v1/chat/completions"
    for model in ["google/gemma-4-31b-it:free", "openrouter/free"]:
        res = _call_openai_compat(
            url=url,
            api_key=api_key,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=json_mode,
            temperature=temperature,
            provider_name="openrouter",
            timeout=timeout,
        )
        if res:
            return res
    return None


def _call_mistral(
    prompt: str,
    system_prompt: str,
    json_mode: bool,
    temperature: float,
    timeout: float = 30.0
) -> Optional[str]:
    api_key = _get_secret("MISTRAL_API_KEY")
    if not api_key:
        return None
    url = "https://api.mistral.ai/v1/chat/completions"
    for model in ["mistral-large-latest", "mistral-small-latest"]:
        res = _call_openai_compat(
            url=url,
            api_key=api_key,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=json_mode,
            temperature=temperature,
            provider_name="mistral",
            timeout=timeout,
        )
        if res:
            return res
    return None


def _call_llm7(
    prompt: str,
    system_prompt: str,
    json_mode: bool,
    temperature: float,
    timeout: float = 30.0
) -> Optional[str]:
    url = "https://api.llm7.io/v1/chat/completions"
    return _call_openai_compat(
        url=url,
        api_key="default",
        model="default",
        prompt=prompt,
        system_prompt=system_prompt,
        json_mode=json_mode,
        temperature=temperature,
        provider_name="llm7",
        timeout=timeout,
    )


def generate_text(
    prompt: str,
    system_prompt: str = "",
    json_mode: bool = False,
    temperature: float = 0.8
) -> Optional[str]:
    """
    Main Entrypoint: Waterfall across all configured LLM providers in priority order.
    Returns generated string content or None if all providers fail.
    """
    # 0. Custom Gateway (OmniRoute / FreeLLMAPI)
    res = _call_custom_gateway(prompt, system_prompt, json_mode, temperature)
    if res:
        return res

    # 1. Gemini (gemini-2.5-flash ONLY)
    res = _call_gemini_25_flash(prompt, system_prompt, json_mode, temperature)
    if res:
        return res

    # 2. Groq (llama-3.3-70b-versatile)
    res = _call_groq(prompt, system_prompt, json_mode, temperature)
    if res:
        return res

    # 3. OpenRouter (google/gemma-4-31b-it:free -> openrouter/free)
    res = _call_openrouter(prompt, system_prompt, json_mode, temperature)
    if res:
        return res

    # 4. Mistral (mistral-large-latest -> mistral-small-latest)
    res = _call_mistral(prompt, system_prompt, json_mode, temperature)
    if res:
        return res

    # 5. LLM7 (keyless fallback)
    res = _call_llm7(prompt, system_prompt, json_mode, temperature)
    if res:
        return res

    print("❌ [LLMRouter] All providers exhausted.")
    return None


if __name__ == "__main__":
    test_res = generate_text("Say 'Hello from LLMRouter' in JSON format.", json_mode=True)
    print("Test Result:", test_res)
