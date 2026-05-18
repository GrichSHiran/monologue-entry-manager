import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import importer


def log(msg, file=sys.stdout):
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}', file=file, flush=True)


def run():
    config = importer.load_config()
    watch_folder = config['watch_folder']
    processed_folder = config['data_folder'] / 'processed'
    processed_folder.mkdir(parents=True, exist_ok=True)

    json_files = list(watch_folder.glob('Monologue*.json'))

    if not json_files:
        log('No Monologue JSON files found.')
        return

    for json_path in json_files:
        log(f'Processing: {json_path.name}')
        try:
            importer.run(json_path, config)
            dest = processed_folder / json_path.name
            counter = 1
            while dest.exists():
                dest = processed_folder / f'{json_path.stem}-{counter}.json'
                counter += 1
            shutil.move(str(json_path), str(dest))
            log(f'Archived to processed/: {dest.name}')
        except Exception as e:
            log(f'Error processing {json_path.name}: {e}', file=sys.stderr)


if __name__ == '__main__':
    run()
