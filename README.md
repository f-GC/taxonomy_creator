# WordPress Taxonomy Creator

This script reads a list of taxonomies with their names from an excel file, checks if they exist and creates them if they don't.

## Usage:

Simply run `taxonomy_creator.py your-excel-file.xlsx`.

## Excel format:

The scipt looks for two columns in the excel; taxonomy, which contains the taxonomies as they appear in WordPress (e.g.- tags, categories...) and name, which contains the name you want to give to that taxonomy.

- Example table:

| taxonomy      | name      |
| -----------   | --------  |
| tags          | my_tag1   |
| tags          | my_tag2   |
| tags          | my_tag3   |
| tags          | my_tag4   |
| categories    | category1 |
| categories    | category2 |