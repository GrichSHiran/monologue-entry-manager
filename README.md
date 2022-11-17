# Monologue Entry Manager

This is an automation module for automating the process of importing fleeting notes and integrating them into a [PKM system](https://github.com/GrichSHiran/pkm-system). It is designed to be used with [Monologue](https://www.monologueapp.com/) and an [Obsidian](https://obsidian.md/) vault. It loads the data from the Monologue JSON file and store each entry as a unique record with a primary key in CSV format and output it to a particular directory in the vault depending on how you configure the application.

## Installation & Configuration

> *This section will be updated soon after the MVP of the first module is fully developed*
## Architecture

The application is separted into 2 modules:

1. **Loading Module:**  Responsible for parsing the main JSON file imported from [Monologue](https://www.monologueapp.com/), generating and updating story and entry CSV tables containing the list of imported items with unique IDs, and outputting each entry as a formatted markdown file to a specific directory depending on the entry's story and its configuration.
2. **Automating Module:** Responsible for changing the `status` metadata of an outputted markdown file after it's been imported for a certain amount of time, moving files with archive status to archive directory, and listening for changes in the main JSON file to trigger the relavant series of procedures.

### Status Keywords of Fleeting Notes:

- `ripe` : The note needs to be reviewed and processed
- `rotten` : The note has been imported for too long and needs to be processed ASAP
- `buried` : The note has been processed and is ready to be moved to the archive directory
- `preserved` : The fleeting note is kept as an active log

## Development Pinboard

### Assumption & Boundaries

Here are the assumptions and boundaries for developing the MVP to avoid designing unnecessarily complex system in the early stage of development.

- The main JSON is not empty and has at least 1 entry
- A row cannot delete from the CSV tables
- An entry connot be reassigned to a new story
- An entry connot be modified after it is imported
- An entry's `isArchive` status connot be switched after it is imported
- A story's `name` and `isArchive` attributes cannot be editted after it is imported

### Main Processes

1. Story Loading: Import and load the stories from the main JSON file and drop duplicates—if story table already exist—before adding new stories as new rows to the story table
2. Story Config: A configuration prompt for setting the `isArchive` default status when new stories are imported
3. Entry Loading: Import and and load the entries from the main JSON file and drop duplicates—if entry table already exist—before adding new entries as new rows to the entry table and output each new entry as a formatted markdown file

### Testing Scenarios

These are the test scenarios in which the first module of application will encounter and must handle.

1. Fresh Run: First time running the application without any prior CSV tables
    - Run Story Loading, Story Config, and Entry Loading
2. Basic Loading: Importing new entries without any new stories from the main JSON file
    - Run Story Loading and Entry Loading
3. Loading with New Stories: Importing new entries with new stories from the main JSON file with prior CSV tables
    - Run Story Loading, Story Config, and Entry Loading