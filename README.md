# Monologue Entry Manager

Imports journal entries from [Monologue](https://www.monologueapp.com/) into an Obsidian vault. Entries are exported from the iPhone via AirDrop, automatically detected on the Mac, and written as individual Markdown files.

## How It Works

1. Tap **Export Entries** in Monologue → AirDrop to Mac → file lands in `~/Downloads`
2. A launchd background service detects the new file and triggers `watcher.py`
3. `watcher.py` calls `importer.py`, which parses the JSON, skips already-imported entries, and writes new ones as Markdown files to the configured output folder
4. The processed JSON is moved to `data/processed/` as an archive

Deduplication is handled via `data/imported_entries.csv`, which tracks every imported entry by its unique ID. This means you can safely rename, move, or delete output Markdown files without causing duplicates on the next import.

## Project Structure

```
monologue-entry-manager/
  config.json       ← all configurable paths live here
  importer.py       ← parses JSON and writes Markdown files
  watcher.py        ← triggered by launchd, calls importer
  data/
    imported_entries.csv   ← import log (gitignored)
    processed/             ← processed JSON archives (gitignored)
    watcher.log            ← launchd stdout (gitignored)
    watcher.err            ← launchd stderr (gitignored)
  launchd/
    com.grich.monologue-watcher.plist
  test-output/      ← local test output, gitignored
```

## Configuration

Edit `config.json` to set your paths:

```json
{
  "watch_folder": "~/Downloads",
  "output_folder": "~/ai-workspace/projects/monologue-entry-manager/test-output",
  "data_folder":   "~/ai-workspace/projects/monologue-entry-manager/data"
}
```

| Key | Description |
|---|---|
| `watch_folder` | Where AirDrop drops files. Must match `WatchPaths` in the launchd plist. |
| `output_folder` | Where Markdown files are written. Point this at your vault's `inbox/` when going live. |
| `data_folder` | Where the import log CSV and processed JSON archives are stored. |

## Testing

Run the importer manually against the exported JSON:

```bash
cd ~/ai-workspace/projects/monologue-entry-manager
python3 importer.py ~/Downloads/Monologue.*.json
```

Output files will appear in `test-output/`. Check a few to confirm the format looks right, then re-run — it should report `No new entries to import.`

## Setup (Going Live)

**1. Update `config.json`**

Change `output_folder` to your vault inbox:

```json
"output_folder": "~/ai-workspace/main-vault/inbox"
```

**2. Register the launchd service**

```bash
cp launchd/com.grich.monologue-watcher.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.grich.monologue-watcher.plist
```

The watcher is now active. AirDrop a Monologue export to your Mac and entries will appear in your vault automatically.

**3. Note on Python path**

The plist uses `/usr/bin/python3`. If you use a custom Python install (pyenv, conda, etc.), update the `ProgramArguments` path in the plist to match before loading it.

**To stop the service:**

```bash
launchctl unload ~/Library/LaunchAgents/com.grich.monologue-watcher.plist
```

## Output Format

Each entry is written as a Markdown file with YAML frontmatter:

```markdown
---
entryId: "7AA6C77B-CFE0-4FE4-B6AA-44F5E8F1E92C"
created: "2020-08-01T17:31:07+07:00"
story: "journal"
source: monologue
---

Entry text here...
```

Filename format: `YYYY-MM-DD HH-MM-SS.md`

---

*Maintained by: Grich + Average Joe*
