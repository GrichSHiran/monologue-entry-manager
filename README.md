# Monologue Entry Manager

Imports journal entries from [Monologue](https://www.monologueapp.com/) into an Obsidian vault. Entries are exported from iPhone and delivered to `importer.py` via a **[nanobot](https://github.com/HKUDS/nanobot)** agent — a Telegram bot that receives the JSON file and triggers the import automatically.

## How It Works

1. Tap **Export Entries** in Monologue → share the JSON file to your nanobot agent via Telegram
2. The agent receives the file and runs `importer.py` against it
3. `importer.py` parses the JSON, skips already-imported entries, and writes new ones as individual Markdown files to the configured output folder
4. The agent archives the JSON and replies with the entry count

Deduplication is handled via `data/imported_entries.csv`, which tracks every imported entry by its unique ID. Re-sending the same export is safe — duplicates are skipped automatically.

## Project Structure

```
monologue-entry-manager/
  config.json       ← configurable paths
  importer.py       ← parses JSON and writes Markdown files
  data/
    imported_entries.csv   ← import log (gitignored)
  test-output/      ← local test output (gitignored)
```

## Configuration

Edit `config.json` to set your paths:

```json
{
  "output_folder": "~/ai-workspace/projects/monologue-entry-manager/test-output",
  "data_folder":   "~/ai-workspace/projects/monologue-entry-manager/data"
}
```

| Key | Description |
|---|---|
| `output_folder` | Where Markdown files are written. Point this at your vault's `inbox/` when going live. |
| `data_folder` | Where the import log CSV is stored. |

## Running Manually

```bash
python3 importer.py ~/path/to/Monologue.json
```

Re-run with the same file — it should report `No new entries to import.`

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
