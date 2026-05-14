#!/usr/bin/env python3
"""
aqua-config — bulk-edit Aqua Voice settings via the app's own sync API.

Zero dependencies. Requires Python 3.8+ (ships with macOS).
Token is read automatically from Aqua's local settings file.

Usage:
    python aqua_config.py status              # show current settings summary
    python aqua_config.py pull                # print current cloud settings as JSON
    python aqua_config.py push my_config.json # merge & push to Aqua cloud
    python aqua_config.py push my_config.json --dry-run
"""

import json
import sys
import urllib.request
import urllib.error
import argparse
import shutil
import datetime
from pathlib import Path

SETTINGS_PATH = Path.home() / "Library/Application Support/Aqua Voice/settings.json"
API_BASE = "https://aqua-server.fly.dev"
APP_VERSION = "0.14.3"   # update if Aqua bumps its version


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_local():
    if not SETTINGS_PATH.exists():
        sys.exit(
            f"Settings file not found at:\n  {SETTINGS_PATH}\n"
            "Make sure Aqua Voice is installed and you have logged in at least once."
        )
    with SETTINGS_PATH.open() as f:
        return json.load(f)


def get_token(settings):
    token = settings.get("token", "")
    if not token:
        sys.exit("No auth token found. Open Aqua Voice and sign in, then try again.")
    return token


def api_post(path, payload, token):
    body = json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit(f"API error {e.code}: {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")


def backup_settings():
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = SETTINGS_PATH.with_suffix(f".bak-{ts}")
    shutil.copy2(SETTINGS_PATH, bak)
    return bak


def build_global_payload(current, config):
    """
    Merge config (user's additions) into current (local Aqua settings)
    and return a ready-to-send global-scope payload.
    """
    # --- dictionary: merge, no duplicates ---
    existing = list(current.get("dictionary", []))
    existing_set = set(existing)
    added = []
    for word in config.get("dictionary", []):
        if word not in existing_set:
            existing.append(word)
            existing_set.add(word)
            added.append(word)

    # --- replacements: user config wins on key collision ---
    existing_reps = {r["from"]: r for r in current.get("replacements", [])}
    for rep in config.get("replacements", []):
        existing_reps[rep["from"]] = rep

    # --- other global fields: config overrides if present ---
    def pick(key, default=None):
        return config.get(key, current.get(key, default))

    global_settings = {
        "dictionary":           existing,
        "replacements":         list(existing_reps.values()),
        "customInstructions":   pick("customInstructions", ""),
        "casualMessaging":      pick("casualMessaging", False),
        "language":             pick("language", "auto"),
        "savedLanguages":       pick("savedLanguages", []),
        "streamingMode":        pick("streamingMode", "default"),
        "transcriptionModel":   pick("transcriptionModel", "nova-3"),
        "fastLLMModel":         pick("fastLLMModel"),
        "promptSet":            pick("promptSet"),
        "streamingModel":       pick("streamingModel"),
        "cloudSync":            pick("cloudSync", True),
        "privacyMode":          pick("privacyMode", False),
        "fileTaggingEnabled":   pick("fileTaggingEnabled", False),
        "marketingBannerEnabled": pick("marketingBannerEnabled", True),
    }
    # Remove None values for nullable/optional fields (server is strict)
    for k in ("fastLLMModel", "promptSet", "streamingModel", "useCase"):
        if global_settings.get(k) is None:
            global_settings.pop(k, None)

    return (
        {
            "scope": "global",
            "settings": global_settings,
            "appVersion": APP_VERSION,
        },
        added,
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status(args):
    s = load_local()
    token = s.get("token", "")
    print(f"Token:         {'present' if token else 'MISSING — sign in to Aqua Voice'}")
    print(f"Dictionary:    {len(s.get('dictionary', []))} entries")
    print(f"Replacements:  {len(s.get('replacements', []))}")
    ci = s.get("customInstructions") or ""
    print(f"Instructions:  {len(ci)} chars")
    print(f"Cloud sync:    {s.get('cloudSync')}")
    print(f"App version:   {s.get('version')}")
    print(f"Settings file: {SETTINGS_PATH}")


def cmd_pull(args):
    s = load_local()
    out = {
        "dictionary":        s.get("dictionary", []),
        "replacements":      s.get("replacements", []),
        "customInstructions": s.get("customInstructions", ""),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_push(args):
    config_path = Path(args.config)
    if not config_path.exists():
        sys.exit(f"Config file not found: {config_path}")

    with config_path.open() as f:
        config = json.load(f)

    current = load_local()
    token = get_token(current)

    payload, added = build_global_payload(current, config)
    gs = payload["settings"]

    print(f"Dictionary:    {len(gs['dictionary'])} total ({len(added)} new words)")
    print(f"Replacements:  {len(gs['replacements'])}")
    print(f"Instructions:  {len(gs.get('customInstructions',''))} chars")

    if args.dry_run:
        print("\nDRY RUN — payload (not sent):")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    bak = backup_settings()
    print(f"Backed up settings → {bak.name}")

    result = api_post("/users/devices/update-settings/", payload, token)
    if result.get("success"):
        print(f"\nDone. {result.get('message', 'Settings updated.')}")
        print("Restart Aqua Voice (or wait ~30 s) to load the new settings.")
    else:
        print(f"Unexpected response: {result}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Bulk-edit Aqua Voice settings via the app's own sync API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python aqua_config.py status
  python aqua_config.py pull > my_aqua_settings.json
  python aqua_config.py push my_aqua_settings.json
  python aqua_config.py push my_aqua_settings.json --dry-run
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show current settings summary").set_defaults(func=cmd_status)
    sub.add_parser("pull",   help="Print current settings as JSON (redirect to save)").set_defaults(func=cmd_pull)

    push_p = sub.add_parser("push", help="Merge a config file and push to Aqua cloud")
    push_p.add_argument("config", help="Path to your JSON config file")
    push_p.add_argument("--dry-run", action="store_true", help="Show what would be sent, don't send")
    push_p.set_defaults(func=cmd_push)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
