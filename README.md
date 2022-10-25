# Monologue Entry Manager

This is an automation module for my [PKM system](https://github.com/GrichSHiran/pkm-system). It is designed to be used with Monologue and an Obsidian Vault. It loads the data from the Monologue JSON file and store each entry as a unique record with a primary key in CSV format.


##### Stages of Development

1. Load and transform data
2. Output markdown files with natural formatting for Obsidian (eg. Pending Entries, Story Lookup Table, Archival Views)
3. Read changes in status from the markdown file and update the csv and that markdown file itself
4. Automate the module (either with AppleScript or via a `systemd` daemon)

