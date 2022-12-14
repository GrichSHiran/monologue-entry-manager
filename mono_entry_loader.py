import json
import pandas as pd


class MonoEntryLoader:

    def __init__(self) -> None:

       self.story_header = ['id', 'name', 'isArchive']
       self.entry_header = ['id', 'created', 'storyId', 'storyName', 'isArchive', 'body']

       self.story_header_str = ','.join(self.story_header) + '\n'
       self.entry_header_str = ','.join(self.entry_header) + '\n'

       self.null_story_id = '00000000-XXXX-0000-XXXX-000000000000'

    def load_mono_json(self, json_path, option='entries') -> dict:

        val_options = ['stories', 'entries']
        if option not in val_options:
            print(f"Invalid Option Argument: '{option}'")
            return 

        with open(json_path, 'r') as file:
            data = json.load(file)

        dict = data[option]

        return dict

    def load_table(self, table_path, option='entry') -> pd.DataFrame:

        val_options = ['story', 'entry']
        if option not in val_options:
            print(f"Invalid Option Argument: '{option}'")
            return

        header_str = self.story_header_str if option == 'story' else self.entry_header_str
        
        try:

            has_table = True
            table_df = pd.read_csv(table_path, index_col=0)

        except FileNotFoundError:

            has_table = False
            with open(table_path, 'w') as file:
                file.write(header_str)

            table_df = pd.read_csv(table_path, index_col=0)

        return table_df

    def process_stories(self, stories: dict) -> pd.DataFrame:

        story_df = pd.DataFrame(stories)
        story_df = story_df.drop(columns=['color', 'created'])

        story_df.loc[len(story_df.index)] = [self.null_story_id, 'FREE_ENTRY']
        story_df['isArchive'] = 0

        story_df = story_df.set_index('id', verify_integrity=True)

        return story_df

    def process_entries(self, entries: dict, story_df: pd.DataFrame) -> pd.DataFrame:

        entry_df = pd.DataFrame(entries)

        try:
            entry_df = entry_df.drop(columns=['modified'])
        except KeyError:
            pass

        col_rename_dict = {'story': 'storyId', 'date': 'created', 'text': 'body'}
        entry_df = entry_df.rename(columns=col_rename_dict)
        entry_df['storyId'] = entry_df['storyId'].fillna(self.null_story_id)

        story_names = entry_df['storyId'].map(story_df['name'])
        archive_status = entry_df['storyId'].map(story_df['isArchive'])
        entry_df = entry_df.assign(storyName=story_names, isArchive=archive_status)

        entry_df = entry_df.set_index('id', verify_integrity=True)

        index_free_header = self.entry_header.copy()
        index_free_header.remove('id')

        entry_df = entry_df[index_free_header]

        return entry_df

    def drop_duplicates(self, loaded_df: pd.DataFrame, saved_df: pd.DataFrame) -> pd.DataFrame:

        append_loc = (~loaded_df.index.isin(saved_df.index))
        append_df = loaded_df.loc[append_loc]

        return append_df

    def output_md(self, entry_df: pd.DataFrame, compost, archive) -> None:

        for index, row in entry_df.iterrows():

            fname = f"{row['created'].replace(':', '')}.md"

            if row['isArchive'] == 1:
                status = 'buried'
                output_path = archive
            else:
                status = 'ripe'
                output_path = compost

            content = self.generate_md_content(row, index, status)

            with open(f'{output_path}/{fname}', 'w') as file:
                file.write(content)

            print(f"\nThe File '{fname}' has been successfully created!\n")

    def generate_md_content(self, row: pd.Series, id: str, default_status='ripe') -> str:

        content_lines = [
            f'---',
            f'entryId: "{id}"',
            f'created: "{row["created"]}"',
            f'story: "{row["storyName"]}"',
            f'---',
            f'',
            f'status:: {default_status}',
            f'#dumped/monoEntry',
            f'# {row["storyName"]}',
            f'',
            f'{row["body"]}',
            f'',
        ]

        content = '\n'.join(content_lines)

        return content

    def update_table(self, append_df: pd.DataFrame, table_path):

        with open(table_path, 'a') as file:

            new_rows = append_df.to_csv(header=False)
            file.write(new_rows)

            print(f"\nA total of {len(append_df)} new records has been successfully appended to: \n\t{table_path}")

