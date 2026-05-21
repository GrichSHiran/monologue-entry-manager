import json
import os
from pathlib import Path

from dotenv import load_dotenv

MODEL = 'claude-haiku-4-5-20251001'

PROMPT_TEMPLATE = """Generate a short, meaningful name for each journal entry below. This name will be used as a filename.

Rules:
- Natural language — write it as you would a title or short phrase
- Capitalize the first word; use natural capitalization for proper nouns
- Keep it concise: a phrase or short sentence, not a paragraph
- Forbidden characters: periods, forward slashes, colons, backslashes, square brackets, curly brackets
- Thai script: preserve Thai characters as-is
- Quotes: wrap the full name in quotation marks and use the quote text verbatim. If the quote is longer than one sentence, use whichever sentence — first or last — is more impactful
- Instructional entries (exercise, recipe, technique): name the specific subject being described
- Never use generic filler: "Reflection", "Thoughts", "Notes", "Entry", "Journal", "Today", "Gratitude"

Return ONLY a valid JSON object mapping entry number (as string) to its name. No explanation.
Example: {{"1": "Choose to believe", "2": "Relationships beyond competition", "3": "\\"Why not?\\""}}

Entries:
{entries_block}"""


BATCH_SIZE = 30


def _name_batch(client, entries: list[dict], offset: int) -> dict[int, str]:
    """Name a single batch of entries. Returns dict of batch-local index (1-based) -> name."""
    blocks = []
    for i, entry in enumerate(entries, 1):
        story = entry.get('story', 'journal')
        text = entry.get('text', '').strip()
        blocks.append(f'Entry {i} | story: {story}\n{text}')

    prompt = PROMPT_TEMPLATE.format(entries_block='\n\n'.join(blocks))

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{'role': 'user', 'content': prompt}],
    )
    response = message.content[0].text.strip()
    if response.startswith('```'):
        response = response.split('```')[1].lstrip('json').strip()
    return json.loads(response)


def generate_filenames(entries: list[dict]) -> dict[str, str]:
    """
    entries: list of dicts with keys: id, text, story
    returns: dict mapping entry id -> filename name string
    Falls back to empty dict on any failure — caller uses date-only filename instead.
    """
    if not entries:
        return {}

    load_dotenv(Path(__file__).parent / '.env')

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {}

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        return {}

    results: dict[str, str] = {}
    for offset in range(0, len(entries), BATCH_SIZE):
        batch = entries[offset:offset + BATCH_SIZE]
        id_map = {str(i): entry['id'] for i, entry in enumerate(batch, 1)}
        try:
            names = _name_batch(client, batch, offset)
            for k, v in names.items():
                if k in id_map:
                    results[id_map[k]] = v
        except Exception:
            pass  # partial failure — remaining entries fall back to date-only

    return results
