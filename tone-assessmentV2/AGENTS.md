# Local runner verification

- `agent-runner.py` can be imported without executing its CLI using `runpy.run_path("agent-runner.py")`. Mock `call_model.__globals__["_post"]` to verify provider request options without paid API calls.
- Ollama options: `AGENT_NUM_CTX` maps to `num_ctx`, `AGENT_MAX_TOKENS` maps to `num_predict`, `AGENT_NUM_THREAD` maps to `num_thread`, and `AGENT_THINK` maps to the `think` flag (disable thinking for reasoning models like qwen3). Unset options retain Ollama defaults.
- Use `git diff --check` to check whitespace. Keep local model benchmarks separate from harness E2E evidence; a short generation does not validate full-prompt context capacity or gate compliance.
