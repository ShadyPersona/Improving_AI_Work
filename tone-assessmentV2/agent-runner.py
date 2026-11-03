#!/usr/bin/env python3
"""agent-runner.py — provider-agnostic agent CLI for harness.py.

Invoked by harness.py as runner.command. Reads the step prompt file, asks the
configured model/agent endpoint to produce the step's outputs as a JSON file
map, writes the files into the run directory, and creates the done marker when
all expected outputs exist.

Configuration (environment variables — never commit secrets):
  AGENT_PROVIDER     copilot-studio | openai | azure | ollama | anthropic
  AGENT_API_KEY      API key for cloud providers (not needed for ollama)
  AGENT_BASE_URL     endpoint URL (Direct Line / OpenAI / Azure / http://localhost:11434 / api.anthropic.com)
  HARNESS_MODEL      model/deployment name recorded in step records

Harness-provided env vars:
  HARNESS_RUN_ID, HARNESS_STEP, HARNESS_PROMPT_FILE, HARNESS_RUN_DIR,
  HARNESS_DONE_MARKER, HARNESS_EXPECTED_OUTPUTS (comma-separated)

Exit codes: 0 success; 1 API/parse/output failure (stderr carries detail).
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

WRAPPER = (
    "\n\n---\n"
    "You are running inside an automated harness (harness.py). This is a REAL "
    "production step — actually perform the work the SKILL describes on the "
    "inputs in the run directory; do not summarize or restate the skill.\n"
    "Respond with a SINGLE JSON object and nothing else — no prose, no code "
    "fences — mapping each output file name (relative to the run directory) "
    "to its complete file contents as a string. Write EVERY output file the "
    "skill requires, including failure files (g5-judgment.md, "
    "punchout-missing-content.md) when the skill directs a failure outcome "
    "instead of the success outputs.\n"
    "Example: {\"toned.md\": \"# ...\", \"tone-changes.json\": \"{...}\"}\n"
)

DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "ollama": "http://localhost:11434",
    "anthropic": "https://api.anthropic.com",
}


def _request(url, headers, body, method, timeout=600):
    req = urllib.request.Request(
        url,
        data=(json.dumps(body).encode("utf-8")
              if body is not None else None),
        headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:2000]
        raise RuntimeError(f"HTTP {e.code}: {detail}")
    except Exception as e:
        raise RuntimeError(str(e))


def _post(url, headers, body, timeout=None):
    if timeout is None:
        timeout = int(os.environ.get("AGENT_TIMEOUT", "600"))
    return _request(url, headers, body, "POST", timeout)


def _get(url, headers, timeout=None):
    if timeout is None:
        timeout = int(os.environ.get("AGENT_TIMEOUT", "600"))
    return _request(url, headers, None, "GET", timeout)


def call_model(provider, base_url, api_key, model, prompt):
    """Return the model's text response for the given provider."""
    if provider == "anthropic":
        # Streamed request — large prompts + long outputs otherwise hit the
        # non-streaming gateway timeout (HTTP 504).
        max_tokens = int(os.environ.get("AGENT_MAX_TOKENS", "16384"))
        req = urllib.request.Request(
            f"{base_url}/v1/messages",
            data=json.dumps({
                "model": model, "max_tokens": max_tokens,
                "stream": True,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8"),
            headers={"content-type": "application/json",
                     "x-api-key": api_key,
                     "anthropic-version": "2023-06-01"},
            method="POST")
        try:
            resp = urllib.request.urlopen(req, timeout=14400)
        except urllib.error.HTTPError as e:
            # Capture the diagnostic headers — Anthropic/CDN request IDs
            # pinpoint which edge rejected the call.
            hdrs = {k.lower(): v for k, v in e.headers.items()
                    if k.lower() in ("x-request-id", "request-id",
                                     "cf-ray", "x-should-retry",
                                     "retry-after", "via", "server")}
            detail = e.read().decode("utf-8", errors="replace")[:1500]
            raise RuntimeError(
                f"HTTP {e.code}: headers={hdrs} body={detail}")
        except Exception as e:
            raise RuntimeError(str(e))
        chunks = []
        for raw_line in resp:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                ev = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if (ev.get("type") == "content_block_delta"
                    and ev.get("delta", {}).get("type") == "text_delta"):
                chunks.append(ev["delta"].get("text", ""))
        return "".join(chunks)

    if provider == "ollama":
        # Long-context runs: AGENT_NUM_CTX sets the KV window (prompt +
        # output). Ollama silently truncates at its default 4k/8k context,
        # which would clip this pipeline's large step prompts.
        opts = {}
        num_ctx = os.environ.get("AGENT_NUM_CTX", "")
        if num_ctx:
            opts["num_ctx"] = int(num_ctx)
        for env_name, option in (("AGENT_MAX_TOKENS", "num_predict"),
                                 ("AGENT_NUM_THREAD", "num_thread")):
            value = os.environ.get(env_name, "")
            if value:
                if int(value) <= 0:
                    raise ValueError(f"{env_name} must be a positive integer")
                opts[option] = int(value)
        body = {"model": model, "stream": False,
                "options": opts,
                "messages": [{"role": "user", "content": prompt}]}
        think = os.environ.get("AGENT_THINK", "")
        if think:
            body["think"] = think.lower() in ("1", "true", "yes", "on")
        data = _post(
            f"{base_url}/api/chat",
            {"content-type": "application/json"},
            body)
        return data.get("message", {}).get("content", "")

    if provider == "azure":
        # AGENT_BASE_URL should be the full chat-completions URL, e.g.
        # https://<res>.openai.azure.com/openai/deployments/<dep>/chat/completions?api-version=2024-08-01-preview
        data = _post(
            base_url,
            {"content-type": "application/json", "api-key": api_key},
            {"max_tokens": 8192,
             "messages": [{"role": "user", "content": prompt}]})
        return data["choices"][0]["message"]["content"]

    if provider == "copilot-studio":
        # Direct Line conversation. AGENT_BASE_URL should be the bot endpoint,
        # e.g. https://directline.botframework.com/v3/directline
        conv = _post(
            f"{base_url}/conversations",
            {"Authorization": f"Bearer {api_key}",
             "content-type": "application/json"}, {})
        conv_id = conv["conversationId"]
        _post(
            f"{base_url}/conversations/{conv_id}/activities",
            {"Authorization": f"Bearer {api_key}",
             "content-type": "application/json"},
            {"type": "message",
             "from": {"id": "harness"},
             "text": prompt})
        # Poll for the bot reply (simple long-poll loop)
        import time
        watermark = ""
        for _ in range(120):
            time.sleep(2)
            acts = _get(
                f"{base_url}/conversations/{conv_id}/activities?watermark={watermark}",
                {"Authorization": f"Bearer {api_key}"})
            watermark = acts.get("watermark", watermark)
            bot_msgs = [a for a in acts.get("activities", [])
                        if a.get("type") == "message"
                        and a.get("from", {}).get("id") != "harness"
                        and a.get("text")]
            if bot_msgs:
                return bot_msgs[-1]["text"]
        raise RuntimeError("copilot-studio: no bot reply within timeout")

    # default: openai-compatible chat completions
    max_tokens = int(os.environ.get("AGENT_MAX_TOKENS", "8192"))
    body = {"model": model, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]}
    effort = os.environ.get("AGENT_REASONING_EFFORT", "")
    if effort:
        body["reasoning_effort"] = effort
    data = _post(
        f"{base_url}/chat/completions",
        {"content-type": "application/json",
         "Authorization": f"Bearer {api_key}"},
        body)
    choice = data.get("choices", [{}])[0]
    msg = choice.get("message") or {}
    content = msg.get("content")
    if content is None:
        # Reasoning models (e.g. DeepSeek) can return content:null when the
        # token budget is consumed by reasoning, or carry the reply in
        # reasoning_content. Surface the shape for diagnosis.
        keys = sorted(msg.keys())
        reasoning = (msg.get("reasoning_content") or "")[:200]
        raise RuntimeError(
            f"null content; finish_reason={choice.get('finish_reason')}, "
            f"message keys={keys}, reasoning[:200]={reasoning!r}")
    return content


def extract_file_map(text):
    """Parse the model response into {filename: contents}."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not m:
        raise RuntimeError("no JSON object found in model response")
    try:
        files = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"invalid JSON file map: {e}")
    if not isinstance(files, dict) or not files:
        raise RuntimeError("file map is empty or not an object")
    return {str(k): (v if isinstance(v, str) else json.dumps(v, indent=2))
            for k, v in files.items()}


def safe_write(run_dir, name, content):
    """Write a file inside run_dir; reject path escapes."""
    rel = name.strip().replace("\\", "/").lstrip("/")
    if not rel or rel.startswith("../") or "/../" in rel or rel.endswith("/.."):
        raise RuntimeError(f"unsafe output path rejected: {name}")
    dest = (run_dir / rel).resolve()
    if run_dir.resolve() not in dest.parents and dest != run_dir.resolve():
        raise RuntimeError(f"output path escapes run dir: {name}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return rel


def main():
    try:
        run_dir = Path(os.environ["HARNESS_RUN_DIR"])
        prompt_file = Path(os.environ["HARNESS_PROMPT_FILE"])
        done_marker = Path(os.environ["HARNESS_DONE_MARKER"])
        expected = [n for n in os.environ.get(
            "HARNESS_EXPECTED_OUTPUTS", "").split(",") if n]
        step = os.environ.get("HARNESS_STEP", "?")
        run_id = os.environ.get("HARNESS_RUN_ID", "?")
        model = os.environ.get("HARNESS_MODEL", "unknown")
        provider = os.environ.get("AGENT_PROVIDER", "openai").lower()
        api_key = os.environ.get("AGENT_API_KEY", "")
        base_url = os.environ.get(
            "AGENT_BASE_URL",
            DEFAULT_BASE_URLS.get(provider, "https://api.openai.com/v1")
        ).rstrip("/")

        prompt = prompt_file.read_text(encoding="utf-8") + WRAPPER

        text = None
        last_err = None
        attempts = int(os.environ.get("AGENT_RETRIES", "4"))
        import time as _time
        for attempt in range(attempts):
            t0 = _time.time()
            try:
                text = call_model(provider, base_url, api_key, model, prompt)
                files = extract_file_map(text)
                break
            except Exception as e:
                last_err = e
                sys.stderr.write(
                    f"[attempt {attempt + 1}/{attempts}] "
                    f"{_time.time() - t0:.1f}s: {e}\n")
                if attempt < attempts - 1:
                    _time.sleep(min(90, 15 * (2 ** attempt)))  # 15s,30s,60s
        else:
            # Dump the raw model reply for diagnosis (kept out of audit/;
            # lives inside the run dir like any other step artifact).
            if text:
                try:
                    (run_dir / f"agent-raw-step{step}.txt").write_text(
                        text, encoding="utf-8")
                except Exception:
                    pass
            sys.stderr.write(
                f"agent-runner step {step} run {run_id}: {last_err}\n")
            return 1

        written = []
        for name, content in files.items():
            written.append(safe_write(run_dir, name, content))

        failure_files = {"g5-judgment.md", "punchout-missing-content.md"}
        produced_failure = any(n in failure_files for n in written)
        missing = [n for n in expected if not (run_dir / n).exists()]

        if produced_failure:
            # Legitimate failure output — do not create the done marker; the
            # harness reads the failure file and loops/escalates.
            print(json.dumps({"status": "failure-output", "step": step,
                              "written": written}))
            return 0

        if expected and not missing:
            done_marker.touch()
            print(json.dumps({"status": "ok", "step": step,
                              "written": written}))
            return 0

        sys.stderr.write(
            f"agent-runner step {step} run {run_id}: expected outputs "
            f"missing: {missing}; wrote {written}\n")
        return 1

    except Exception as e:
        sys.stderr.write(f"agent-runner fatal: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
