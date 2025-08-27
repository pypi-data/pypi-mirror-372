<p align="center">
  <img src="docs/assets/logo.svg" alt="LLM Chatbot Kit" width="560" />
</p>

<p align="center">
  <b>Developer‑first kit for LLM chatbots</b><br/>
  Streaming • Memory • Personas (Discord‑first)
</p>

# LLM Chatbot Kit

![Build Docs](https://github.com/maiko/llm-chatbot-kit/actions/workflows/docs.yml/badge.svg?branch=main)
![Build Package](https://github.com/maiko/llm-chatbot-kit/actions/workflows/package.yml/badge.svg?branch=main)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)

Install (pipx recommended)

- pipx: `pipx install .` (from repo root) or `pipx install git+https://github.com/maiko/llm-chatbot-kit@main`
- Run (Discord): `llm-chatbot discord run --personality personalities/aelita.yml`
  - Default behavior streams replies as natural message bursts (no edits), with typing indicator.
  - Disable streaming: `llm-chatbot discord run --no-stream` (or `--stream=false`).

Demo personalities (Code Lyoko)

- Aelita (ally): `llm-chatbot discord run --personality personalities/aelita.yml`
- XANA (antagonist): `llm-chatbot discord run --personality personalities/xana.yml`

Configuration (env)

- `DISCORD_TOKEN`: Discord bot token
- `OPENAI_API_KEY`: OpenAI key
- `OPENAI_MODEL` (optional): defaults to `gpt-5-mini`.
- `OPENAI_VERBOSITY` (optional): `low` (default), `medium`, or `high` (GPT‑5 only; not for `gpt-5-chat-latest`).
- `DISCORD_OWNER_ID` (optional): User ID for `reboot`
- `COMMAND_PREFIX` (default `~`), `MAX_TURNS` (default `20`)
- `CONTEXT_STORE_PATH` (optional): override default JSON context path.

Run multiple personas

- Use one process per bot (each with its own `DISCORD_TOKEN`).
- Aelita: `llm-chatbot discord run --personality personalities/aelita.yml` (prefix `!`)
- XANA: `llm-chatbot discord run --personality personalities/xana.yml` (prefix `^`)

Models & generation

- Generation model: GPT‑5 mini by default (`OPENAI_MODEL=gpt-5-mini`).
- Judge/classifier (listening): GPT‑5 nano.
- GPT‑5 features used (except `gpt-5-chat-latest`):
  - `reasoning: { effort: "minimal" }` for faster time-to-first-token.
  - `text: { format: { type: "text" }, verbosity: <OPENAI_VERBOSITY> }` (default `low`).
- Requests use the Responses API with typed items (developer/user/assistant). Chat Completions is kept only as a fallback.

Create a new personality

- Duplicate `personalities/aelita.yml`, adjust `name`, `developer_prompt`, `system_prompt`.
- Optional pacing in YAML:
  ```yaml
  streaming:
    rate_hz: 1.0
    min_first: 80
    min_next: 120
  ```
- Optional environment & listening:
  ```yaml
  command_prefix: "!"
  environment:
    include_emojis: true
    emojis_limit: 50
    include_online_members: true
    online_limit: 50
  listen:
    enabled: false
    judge_enabled: true
    judge_model: gpt-5-nano
  truncation: auto  # hide meta and let API auto-truncate context
  ```
- Run with `--personality path/to/your.yml`.

Notes

- Messages are stored in a JSON file under `~/.cache/llm-chatbot-kit/context.json` (or `CONTEXT_STORE_PATH`). On first run, the kit migrates an existing `~/.cache/discord-llm-bot/context.json` automatically.
- Keep replies under Discord’s 2000-char limit; bot auto-chunks.
- Streaming is default; on failure it falls back to non-streaming.
- Enable intents in the Developer Portal: Message Content (required) and Presence (for online members).
- Mentions: The bot allows user mentions but blocks roles/everyone. It adds a reminder to the developer prompt not to mention itself and strips leading self-mentions.
- Environment context in guilds includes a “Membres visibles” list with member names and IDs for correct mentions, and an optional online members list by name only.

Commands (per persona prefix)

- Memory: `<prefix>context`, `<prefix>reset`, `<prefix>reboot` (owner)
- Listening: `<prefix>listen on|off|status|ban|unban`
- Costs: `<prefix>cost status|budget daily|budget monthly|hardstop on|off`
- Emojis: `<prefix>emoji list`
- Truncation: `<prefix>truncation status|set <auto|disabled>`

Planned

- Multi-platform supervisor: run the same persona across Discord and other platforms concurrently via `llm-chatbot multi run --platforms discord,slack`. See issue #3.
- Slack integration: first-class adapter and `slack run` subcommand. See issue #2.
- Logging improvements: phased verbosity, JSON logs, redaction, usage summaries. See issue #4.
- Docker packaging: official image and compose example. See issue #5.

Documentation

- Overview: `docs/Overview.md`
- Installation: `docs/Installation.md`
- Configuration: `docs/Configuration.md`
- Personalities: `docs/Personality.md`
- Streaming details: `docs/Streaming.md`
- Listening (Experimental): `docs/Listening.md`
- Costs: `docs/Costs.md`
- Commands: `docs/Commands.md`
- Packaging (CI builds): `docs/Packaging.md`
- Development: `docs/Development.md`
- Security: `docs/Security.md`
- Troubleshooting: `docs/Troubleshooting.md`

Quick tips

- Set `DISCORD_OWNER_ID` to receive DM alerts on spend thresholds and to unlock owner-only commands.
- If running via pipx, use `pipx upgrade llm-chatbot-kit` (or reinstall) after pulling updates.
