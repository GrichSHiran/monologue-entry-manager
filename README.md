# Monologue Entry Manager

This is an automation module for my [PKM system](https://github.com/GrichSHiran/pkm-system). It is designed to be used with Monologue and an Obsidian Vault. It loads the data from the Monologue JSON file and store each entry as a unique record with a primary key in CSV format.


##### Stages of Development

1. Loading Module: Load and transform data from the main JSON file with all entries from Monologue
2. Output Module: Output each entry as a dumped note to a specific directory in the Obsidian vault, depending on the entry's type
3. Status Module: Check if each dumped note had been sitting in the vault unprocessed for too long and update its status tag or move the file to an archive folder accordingly
4. Automation: Automate the module (either with AppleScript or via a `systemd` daemon)

### Stage 1: Loading Module

End Result:
- Data from `monologueAllEntries.json` is read
- The `allEntries.csv` and `storyTable.csv` files are updated
- For each `x: x = id` in `entries` in `monologueAllEntries.json`, if `x` is not in `id` in`allEntries.csv`, add object where `id = x` to `allEntries.csv`

Objectives:

1. Read the `monologueAllEntries.json` file and individually add entries to the dumped note CSV where each entry are treated as a record with a primary key and a status on whether if it has been processed.
    1. Use `id` of an entry as its primary key
    2. Save `id` of each `story` as their own primary key in another table where each story is a type of note
    3. Have each entry have a `story` as a foreigner key that points to a `story`
2. Check if an entry of the same `id` has already been added to the database.
    1. If so, do nothing;
    2. Else, add the entry to the CSV file.


