# aqua-config

Bulk-edit your [Aqua Voice](https://withaqua.com) dictionary, replacements, and custom instructions from the command line.

**Zero dependencies.** Just Python 3 (already on every Mac).

---

## The problem

Aqua Voice is great, but its settings UI doesn't let you:
- Import a list of 50+ words into your dictionary at once
- Bulk-add text replacements (email, phone, addresses, shortcuts)
- Version-control your custom instructions

And since Aqua syncs everything to the cloud, editing the local `settings.json` file directly doesn't stick — the cloud copy wins on every restart.

## The solution

This script uses the same internal API endpoint that Aqua itself uses to sync your settings. Changes go straight to the cloud, so they survive restarts and work across all your devices.

---

## Quick start

```bash
# 1. Clone or download
git clone https://github.com/visualpharm/aqua-config
cd aqua-config

# 2. Check your current settings
python aqua_config.py status

# 3. Copy the example config and edit it
cp example_config.json my_config.json
# ... edit my_config.json with your words, replacements, instructions ...

# 4. Preview what will be sent
python aqua_config.py push my_config.json --dry-run

# 5. Push to Aqua cloud
python aqua_config.py push my_config.json

# 6. Restart Aqua Voice (or wait ~30 s)
```

That's it. Your dictionary, replacements, and instructions are now live.

---

## Commands

| Command | What it does |
|---|---|
| `status` | Show a summary of your current Aqua settings |
| `pull` | Dump current settings as JSON (good for backup / starting point) |
| `push <file>` | Merge your config file and push to Aqua cloud |
| `push <file> --dry-run` | Preview the payload without sending anything |

---

## Config file format

Your config file is a plain JSON with three optional sections. You only need to include the parts you want to change.

```json
{
  "dictionary": [
    "Acme Corp",
    "SFBA",
    "PostgreSQL",
    "iboyko"
  ],

  "replacements": [
    { "from": "my email",    "to": "you@example.com" },
    { "from": "my phone",    "to": "+1 555 123 4567" },
    { "from": "signature",   "to": "Jane Doe\njane@example.com" }
  ],

  "customInstructions": "Keep my direct style. Preserve technical terms and URLs exactly. Do not add greetings or emojis."
}
```

**Dictionary** — words are merged with your existing list. Duplicates are skipped.

**Replacements** — merged by the `from` key. If a replacement with the same trigger already exists, your config version wins.

**customInstructions** — replaces the entire instructions field if present.

---

## How it works

Aqua stores a JWT in `~/Library/Application Support/Aqua Voice/settings.json`. The script reads that token automatically (no login step) and POSTs your settings to `aqua-server.fly.dev/users/devices/update-settings/` — the same endpoint Aqua's own app uses for cloud sync.

Before every push, the script backs up your local settings file to `settings.json.bak-<timestamp>`.

---

## Storing your config in dotfiles

Since the config is plain JSON, you can commit it to your dotfiles repo and push updates with one command:

```bash
python aqua_config.py push ~/dotfiles/aqua_settings.json
```

---

## Requirements

- macOS (Aqua Voice is Mac-only)
- Python 3.8+ (ships with macOS Ventura and later; `python3 --version` to check)
- Aqua Voice installed and logged in

No pip install required.

---

## Notes

- This uses Aqua's **internal, undocumented** sync API. It may break if Aqua changes their backend — open an issue if that happens.
- The script never reads your transcription history or audio.
- Only the fields you specify in your config are changed. Everything else is left as-is.

---

## Contributing

PRs welcome. Obvious things that would be nice:
- `add-words` subcommand for quick one-liners
- Windows support (different settings path)
- Auto-detect app version from the installed `.app`

---

## License

MIT
