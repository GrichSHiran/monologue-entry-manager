# Import and read monologueAllEntries
# save as pandas dataframe
# check if each id already exist in AllEntries.csv
# if not, add; else move on

# Import
import config

import os
import json
import datetime as dt
import pandas as pd

# Constants
main_json_path = r'env/monologueAllEntries2.json'
entry_table_path = r'env/entry-table.csv'
entry_ids_path = r'env/entry-ids.csv'

entry_table_headers = ['id', 'created', 'imported', 'expire', 'storyId', 'storyName', 'status', 'text']
entry_ids_headers = ['num', 'id']

entry_table_header_str = ",".join(entry_table_headers)
entry_ids_header_str = ",".join(entry_ids_headers)

# Load Monologue's Main JSON File

with open(main_json_path, 'r') as file:
    main_data = json.load(file)

main_entries = main_data['entries']
main_stories = main_data['stories']

# print(len(main_entries))
# print(main_stories)

# --- START STORY TABLE ---
story_dict = dict()
story_dict['NO_STORYID'] = 'FREE_ENTRY'

for item in main_stories:
    story_dict[item['id']] = item['name']

print(story_dict)
# --- END STORY TABLE ---

# Load Saved Entry Table & Create entry-table.csv if not exist
try:

    saved_entry_table = pd.read_csv(entry_table_path, index_col='id')

except FileNotFoundError:

    with open(entry_table_path, 'w') as file:
        file.write(entry_table_header_str)

# MAYBE DON'T NEED SEPARATE FILE FOR IDS
# # Load CSV File of Saved Entries
# try:

#     saved_entry_id_list = pd.read_csv(entry_ids_path)
#     print(saved_entry_id_list.head())

# except FileNotFoundError:

#     print("!!---entry_ids.csv has not been created---!!")

#     with open(entry_ids_path, 'w') as file:
#         file.write(entry_ids_header_str)

#     saved_entry_id_list = pd.read_csv(entry_ids_path)

# DataFrame of New Entries
df_entry = pd.DataFrame(main_entries)

df_entry = df_entry.drop(columns=['modified'])
df_entry = df_entry.rename(columns={'story': 'storyId', 'date': 'created'})

# Set 'id' as index
df_entry = df_entry.set_index('id', verify_integrity=True)

# If an id is already in entry-ids.csv, drop the row with that id
print(f"Before Drop Shape: {df_entry.shape}")

# print(saved_entry_table.tail())

try:
    df_entry = df_entry.drop(list(saved_entry_table.index))
except NameError:
    print("!!---entry_table.csv has not been created---!!")
    pass

print(f"After Drop Shape: {df_entry.shape}")

# Add 'imported' and 'expire' columns
df_entry['imported'] = dt.date.today()
df_entry['expire'] = df_entry['imported'] + dt.timedelta(days=3)

# Add 'storyId' and 'storyName' Columns
df_entry['storyId'] = df_entry['storyId'].fillna('NO_STORYID')
df_entry['storyName'] = df_entry['storyId'].map(lambda x: story_dict[x])

# Add 'status' column
auto_buried_list = ['Mantras']

df_entry['status'] = '#ripe'
df_entry['status'].loc[df_entry['storyName'].isin(auto_buried_list)] = '#buried'

# Rearrange columns & Set 'id' as Index
df_entry = df_entry[['created', 'imported', 'expire', 'storyId', 'storyName', 'status', 'text']]

# Save as CSV
# entry_id_list = pd.Series(df_entry.index)

# with open(entry_ids_path, 'a') as file:

#     new_ids = entry_id_list.to_csv(header=False)
#     print("\n\nThese are the new entry ids:")
#     print(new_ids)

#     file.write(f"\n{new_ids}")

with open(entry_table_path, 'a') as file:

    new_entries = df_entry.to_csv(header=False)
    print("\n\nThese are the new entries:")
    print(new_entries)

    file.write(f"\n{new_entries}")
