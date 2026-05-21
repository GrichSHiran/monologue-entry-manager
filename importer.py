import csv
import json
import sys
from datetime import datetime
from pathlib import Path

from namer import generate_filenames


def log(msg, file=sys.stdout):
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}', file=file, flush=True)


def load_config() -> dict:
    config_path = Path(__file__).parent / 'config.json'
    with open(config_path) as f:
        config = json.load(f)
    return {k: Path(v).expanduser() for k, v in config.items()}


def load_imported_ids(csv_path: Path) -> set:
    if not csv_path.exists():
        return set()
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return {row['id'] for row in reader}


def append_imported_records(csv_path: Path, records: list):
    is_new = not csv_path.exists()
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'created', 'story', 'filename'])
        if is_new:
            writer.writeheader()
        writer.writerows(records)


def format_filename(date_str: str, name: str = '') -> str:
    date_part = date_str[:10]
    if name:
        return f'{date_part} - {name}.md'
    return f'{date_part}.md'


def generate_md(entry: dict, story_name: str) -> str:
    lines = [
        '---',
        f'entryId: "{entry["id"]}"',
        f'created: "{entry["date"]}"',
        f'story: "{story_name}"',
        f'source: monologue',
        '---',
        '',
        entry.get('text', ''),
        '',
    ]
    return '\n'.join(lines)


def run(json_path: Path, config: dict):
    output_folder = config['output_folder']
    data_folder = config['data_folder']
    csv_path = data_folder / 'imported_entries.csv'

    output_folder.mkdir(parents=True, exist_ok=True)
    data_folder.mkdir(parents=True, exist_ok=True)

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    stories = {s['id']: s['name'] for s in data.get('stories', [])}
    entries = data.get('entries', [])
    imported_ids = load_imported_ids(csv_path)

    new_entries = [e for e in entries if e['id'] not in imported_ids]

    if not new_entries:
        log('No new entries to import.')
        return

    log(f'Generating filenames for {len(new_entries)} entries...')
    slugs = generate_filenames([
        {'id': e['id'], 'text': e.get('text', ''), 'story': stories.get(e.get('story'), 'journal')}
        for e in new_entries
    ])

    records = []
    for entry in new_entries:
        story_id = entry.get('story')
        story_name = stories.get(story_id, 'journal') if story_id else 'journal'

        filename = format_filename(entry['date'], slugs.get(entry['id'], ''))
        output_path = output_folder / filename

        counter = 1
        while output_path.exists():
            output_path = output_folder / f'{filename[:-3]}-{counter}.md'
            counter += 1

        output_path.write_text(generate_md(entry, story_name), encoding='utf-8')
        log(f'Created: {output_path.name}')

        records.append({
            'id': entry['id'],
            'created': entry['date'],
            'story': story_name,
            'filename': output_path.name,
        })

    append_imported_records(csv_path, records)
    log(f'{len(records)} entries imported.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        log('Usage: python importer.py <path-to-monologue.json>')
        sys.exit(1)
    config = load_config()
    run(Path(sys.argv[1]).expanduser(), config)
