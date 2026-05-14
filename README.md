# aqua-config

**Your Aqua Voice dictionary, kept up to date by the AI assistant you're already using.**

---

## The vision: a dictionary that updates itself

Imagine dictating a message to a colleague — Aqua already knows their name.  
Starting a new project — Aqua already knows the repo name, the stack, the key classes.  
Installing a new library — Aqua already knows the package name.

Your AI coding assistant (Claude Code, Cursor, Windsurf) already has this context. It reads your codebase, your git history, your dependencies. `aqua-config` is the bridge that turns that knowledge into an up-to-date Aqua Voice dictionary — automatically, on demand, in seconds.

The practical result: **you stop correcting the same words over and over.** Your dictionary grows with your work instead of lagging behind it.

---

## The situation

Aqua Voice syncs all settings — dictionary, replacements, custom instructions — to the cloud. That's why your settings survive reinstalls and work across devices. But it also means:

- Editing `~/Library/Application Support/Aqua Voice/settings.json` directly **doesn't stick** — the cloud copy overwrites it on every restart.
- There is no bulk-import UI. Adding 50 words means 50 clicks.
- There is no API documented for third-party tools.

`aqua-config` fixes this by using the same internal sync endpoint Aqua's own app uses. Your changes go to the cloud, and stay there.

---

## Install in one prompt

Open Claude Code, Cursor, or any AI coding assistant. Paste this:

```
Download https://raw.githubusercontent.com/visualpharm/aqua-config/main/aqua_config.py
to my home directory (or project root). Then run: python ~/aqua_config.py status
```

That's it. No pip install. No dependencies. Python 3 is already on your Mac.

Or manually:

```bash
curl -O https://raw.githubusercontent.com/visualpharm/aqua-config/main/aqua_config.py
python aqua_config.py status
```

---

## Prompts that fill your dictionary

Paste any of these into Claude Code, Cursor, or your preferred AI assistant.

---

### First-time setup — scan your project

```
Scan this codebase and generate an aqua_settings.json for Aqua Voice.

Include in the dictionary:
- All proper nouns: component names, class names, file names that aren't generic
- All package and library names from package.json / requirements.txt / Cargo.toml / go.mod / etc.
- All author names from `git log --format="%an" | sort -u`
- All domain-specific abbreviations or acronyms you notice in comments and variable names
- Any company names, product names, or brand names referenced in the code or README

Include in replacements (triggers → expansions):
- Common shorthand I might dictate: repo name, main URL, primary email if visible in git config

Set customInstructions to match the project's technical domain.

Save the result to aqua_settings.json, then run:
python aqua_config.py push aqua_settings.json
```

---

### Weekly refresh — keep it current

```
Check what's new in this project since last week.
Look at: new files added, new dependencies, new git contributors, new class/function names.
Update aqua_settings.json with any new terms and run:
python aqua_config.py push aqua_settings.json
```

---

### People and contacts

```
Read my recent git log, any CODEOWNERS or CONTRIBUTORS file, and any contact-like
data in this repo (emails in README, Slack handles, etc.).
Add all proper names and handles to the Aqua Voice dictionary in aqua_settings.json.
Run: python aqua_config.py push aqua_settings.json
```

---

### Domain vocabulary dump

```
I work in [your field: medicine / law / finance / design / etc.].
Generate 50–100 domain-specific terms, proper nouns, and abbreviations commonly
used in this field that a dictation app would mis-transcribe.
Add them to aqua_settings.json and run:
python aqua_config.py push aqua_settings.json
```

---

### After any meeting or document

```
Read [meeting transcript / document / email thread].
Extract all proper nouns, product names, people names, and technical terms
that Aqua Voice might not know. Add them to aqua_settings.json and push.
```

---

## Config file format

The config file is plain JSON. Include only the sections you want to change.

```json
{
  "dictionary": [
    "Acme Corp",
    "PostgreSQL",
    "Barbara Minto",
    "MECE"
  ],

  "replacements": [
    { "from": "my email",    "to": "you@example.com" },
    { "from": "my phone",    "to": "+1 555 123 4567" },
    { "from": "my address",  "to": "123 Main St, City, Country" },
    { "from": "signature",   "to": "Jane Doe\nyou@example.com\n+1 555 123 4567" },
    { "from": "my github",   "to": "https://github.com/yourhandle" }
  ],

  "customInstructions": "Keep my direct style. Preserve technical terms and URLs exactly. Do not add greetings or emojis."
}
```

**Dictionary** entries are merged with your existing list — nothing is removed, duplicates are skipped.  
**Replacements** are merged by the `from` key — your config wins on collision.  
**customInstructions** replaces the entire field if present.

---

## Commands

```bash
python aqua_config.py status              # summary of current settings
python aqua_config.py pull                # dump current settings as JSON
python aqua_config.py push my_config.json # merge and push to Aqua cloud
python aqua_config.py push my_config.json --dry-run
```

`pull` is useful for your first run — save the output as your starting config, then edit and push.

---

## Store your config in dotfiles

Since the config is plain JSON, commit it to your dotfiles:

```bash
python aqua_config.py push ~/dotfiles/aqua_settings.json
```

As you add projects, teammates, and tools — update the file and re-run.

---

## How it works (technical)

Aqua Voice stores a JWT in `~/Library/Application Support/Aqua Voice/settings.json`.  
The script reads that token — no separate login step.

The sync endpoint (discovered by extracting `app.asar`):

```
POST https://aqua-server.fly.dev/users/devices/update-settings/
Authorization: Bearer <token>
Content-Type: application/json

{
  "scope": "global",
  "settings": { ... },
  "appVersion": "0.14.3"
}
```

Global settings (synced across all your devices): `dictionary`, `replacements`, `customInstructions`, `language`, `transcriptionModel`, and a few others.

Before every push, the script backs up your local settings file to `settings.json.bak-<timestamp>`.

This uses Aqua's **internal, undocumented** API. It may break if they change their backend — open an issue if that happens.

---

## Requirements

- macOS (Aqua Voice is Mac-only)
- Python 3.8+ (`python3 --version` — ships with macOS Ventura and later)
- Aqua Voice installed and logged in

---

## Contributing

PRs welcome. Good next things:
- Windows support (different settings path)
- Auto-detect installed app version
- A `watch` mode that re-pushes whenever the config file changes
- An `add` subcommand for quick one-liners: `python aqua_config.py add "Barbara Minto" "MECE"`

---

## License

MIT — Ivan Boyko / [Icons8](https://icons8.com)
