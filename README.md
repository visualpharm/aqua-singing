# aqua-singing

Teach [Aqua Voice](https://withaqua.com) your vocabulary. Your Aqua Voice sings when it knows your words.

Bulk-edit dictionary, replacements, and custom instructions from the command line. Zero dependencies. Python 3 ships with macOS.

---

## The problem

Aqua syncs settings to the cloud. Editing `settings.json` locally doesn't stick. Cloud wins on every restart. There's no import UI and no documented API.

This script uses the same internal sync endpoint Aqua's own app uses. Changes go straight to the cloud.

---

## Install

```bash
curl -O https://raw.githubusercontent.com/visualpharm/aqua-config/main/aqua_config.py
python aqua_config.py status
```

Or paste this into Claude Code or Cursor:

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

Dictionary words are merged. Nothing is removed, duplicates are skipped. Replacements are merged by `from` key. `customInstructions` replaces the full field.

---

## Keep it current with AI

Your AI coding assistant already knows your codebase: package names, class names, git authors. Point it at aqua-config and it generates the dictionary for you. Run it again when you start a new project or bring someone new onto the team.

**First-time setup:**

```
Scan this codebase. Generate aqua_settings.json for Aqua Voice with:
- Proper nouns: component names, class names, non-generic filenames
- Package names from package.json / requirements.txt / go.mod / etc.
- Author names from: git log --format="%an" | sort -u
- Domain abbreviations and acronyms from comments and variable names
Then run: python aqua_config.py push aqua_settings.json
```

**Weekly refresh:**

```
Check what changed since last week: new files, dependencies, contributors.
Update aqua_settings.json and run: python aqua_config.py push aqua_settings.json
```

**After a meeting or document:**

```
Read [transcript / doc]. Extract proper nouns and terms Aqua might mis-transcribe.
Add to aqua_settings.json and push.
```

**New domain:**

```
I work in [field]. List 50-100 terms a dictation app would likely get wrong.
Add to aqua_settings.json and push.
```

Commit `aqua_settings.json` to your dotfiles. Re-run push as your work evolves.

---

## How it works

The script reads your JWT from `~/Library/Application Support/Aqua Voice/settings.json`. No separate login.

Endpoint discovered by extracting `app.asar`:

```
POST https://aqua-server.fly.dev/users/devices/update-settings/
Authorization: Bearer <token>
{ "scope": "global", "settings": { ... }, "appVersion": "0.14.3" }
```

Undocumented. May break on backend changes. Open an issue if it does.

The script backs up your local settings file before every push.

---

## Contributing

PRs welcome. Good next things:
- `add` subcommand for quick one-liners
- Windows support
- `watch` mode: auto-push when the config file changes

---

## License

MIT — [Icons8](https://icons8.com)
