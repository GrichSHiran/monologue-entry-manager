import json
import datetime as dt
import pandas as pd


# Attributes: paths to JSON, and CSV files
# Methods: parse JSON, check against CSV files to append new entries
class MonoEntryLoader:

    def __init__(self, entry_table, story_table) -> None:

        self.entry_table = entry_table
        self.story_table = story_table

    def load_mono_json(self, json_path) -> tuple:

        with open(json_path, 'r') as file:
            data = json.load(file)

        entries = data['entries']
        stories = data['stories']

        return (entries, stories)

    # def check_tables(self):

    #     try:
    #         saved_entry_table = pd.read_csv(self.entry_table, index_col='id')
    #         has_entry_table = True
    #     except FileNotFoundError:
    #         has_entry_table = False

    def process_stories(self, stories) -> pd.DataFrame:

        story_df = pd.DataFrame(stories)
        story_df = story_df.drop(columns=['color', 'created'])

        story_df.loc[len(story_df.index)] = ['NO_STORYID', 'FREE_ENTRY']
        story_df['isArchive'] = 0

        story_df = story_df.set_index('id', verify_integrity=True)
        # story_df is now a DataFrame with id, name, and isArchive headers

        return story_df

    def process_entries(self, entries, story_df) -> pd.DataFrame:

        entry_df = pd.DataFrame(entries)

        try:
            entry_df = entry_df.drop(columns=['modified'])
        except KeyError:
            pass

        col_rename_dict = {'story': 'storyId', 'date': 'created', 'text': 'body'}
        entry_df = entry_df.rename(columns=col_rename_dict)
        entry_df['storyId'] = entry_df['storyId'].fillna('NO_STORYID')

        story_names = entry_df['storyId'].map(story_df['name'])
        entry_df = entry_df.assign(storyName=story_names)

        entry_df = entry_df.set_index('id', verify_integrity=True)
        entry_df = entry_df['created', 'storyId', 'storyName', 'body']
        # entry_df is now a DataFrame with created, storyId, storyName, and body as headers and id as index

        return entry_df

