# aqua-config

Bulk-edit your [Aqua Voice](https://withaqua.com) dictionary, replacements, and custom instructions from the command line — and keep them in sync with your actual work via AI prompts.

---

## The problem

Aqua syncs all settings to the cloud. Editing `settings.json` locally doesn't stick — the cloud copy wins on every restart. There's no import UI and no documented API.

This script uses the same internal sync endpoint Aqua's own app uses. Changes go to the cloud and stay there.

---

## Install

```bash
curl -O https://raw.githubusercontent.com/visualpharm/aqua-config/main/aqua_config.py
python aqua_config.py status
```

No dependencies. Python 3 ships with macOS.

**Or, paste this into Claude Code / Cursor:**

```
Download https://raw.githubusercontent.com/visualpharm/aqua-config/main/aqua_config.py
to my home directory, then run: python ~/aqua_config.py status
```

---

## Usage

```bash
python aqua_config.py status              # current settings summary
python aqua_config.py pull                # dump settings as JSON
python aqua_config.py push my_config.json
python aqua_config.py push my_config.json --dry-run
```

---

## Config format

```json
{
  "dictionary": [
    "Acme Corp",
    "PostgreSQL",
    "Barbara Minto"
  ],
  "replacements": [
    { "from": "my email",   "to": "you@example.com" },
    { "from": "my phone",   "to": "+1 555 123 4567" },
    { "from": "signature",  "to": "Jane Doe\nyou@example.com" }
  ],
  "customInstructions": "Keep my direct style. Preserve technical terms and URLs exactly."
}
```

Dictionary words are merged — nothing is removed. Replacements are merged by `from` key. `customInstructions` replaces the full field.

---

## Keep it current with AI prompts

The real power: your AI coding assistant already knows your codebase, teammates, and dependencies. Use it to generate and refresh the config automatically.

**First-time setup — scan your project:**

```
Scan this codebase. Generate aqua_settings.json for Aqua Voice with:
- Proper nouns: component names, class names, non-generic filenames
- All package names from package.json / requirements.txt / go.mod / etc.
- Author names from `git log --format="%an" | sort -u`
- Domain abbreviations and acronyms from comments and variable names
Then run: python aqua_config.py push aqua_settings.json
```

**Weekly refresh:**

```
Check what's new since last week: new files, dependencies, contributors.
Update aqua_settings.json and run: python aqua_config.py push aqua_settings.json
```

**After a meeting or document:**

```
Read [transcript / doc]. Extract proper nouns and technical terms Aqua might mis-transcribe.
Add to aqua_settings.json and push.
```

**Domain vocabulary:**

```
I work in [field]. Generate 50-100 domain terms a dictation app would likely mis-transcribe.
Add to aqua_settings.json and push.
```

Commit `aqua_settings.json` to your dotfiles and re-run `push` as your work evolves.

---

## How it works

The script reads your JWT from `~/Library/Application Support/Aqua Voice/settings.json` — no separate login. It POSTs to Aqua's internal sync endpoint:

```
POST https://aqua-server.fly.dev/users/devices/update-settings/
Authorization: Bearer <token>
{ "scope": "global", "settings": { ... }, "appVersion": "0.14.3" }
```

Discovered by extracting `app.asar`. Undocumented — may break on backend changes.

A timestamped backup of your local settings is created before every push.

---

## Contributing

PRs welcome. Obvious gaps:
- `add` subcommand for quick one-liners
- Windows support
- `watch` mode for auto-push on file change

---

## License

MIT — [Icons8](https://icons8.com)
