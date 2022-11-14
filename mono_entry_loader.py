import json
import datetime as dt
import pandas as pd


# Attributes: paths to JSON, and CSV files
# Methods: parse JSON, check against CSV files to append new entries
class MonoEntryLoader:

    def __init__(self) -> None:

       self.story_header = ['id', 'name', 'isArchive']
       self.entry_header = ['id', 'created', 'storyId', 'storyName', 'isArchive', 'body']

       self.story_header_str = ','.join(self.story_header)
       self.entry_header_str = ','.join(self.entry_header)


    def load_mono_json(self, json_path, option='entries') -> dict:

        with open(json_path, 'r') as file:
            data = json.load(file)

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
            table_df = pd.read_csv(table_path)

        except FileNotFoundError:

            has_table = False
            with open(table_path, 'w') as file:
                file.write(header_str)

            table_df = pd.read_csv(table_path)

        return table_df

    # def check_tables(self):

    #     try:
    #         saved_entry_table = pd.read_csv(self.entry_table, index_col='id')
    #         has_entry_table = True
    #     except FileNotFoundError:
    #         has_entry_table = False

    def process_stories(self, stories: dict) -> pd.DataFrame:

        story_df = pd.DataFrame(stories)
        story_df = story_df.drop(columns=['color', 'created'])

        story_df.loc[len(story_df.index)] = [self.null_story_id, 'FREE_ENTRY']
        story_df['isArchive'] = 0

        story_df = story_df.set_index('id', verify_integrity=True)
        # story_df is now a DataFrame with id, name, and isArchive headers

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
        # entry_df is now a DataFrame with created, storyId, storyName, and body as headers and id as index

        return entry_df

