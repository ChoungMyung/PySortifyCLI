# PySortifyCLI

A command-line Python file organizer that scans a target folder, previews sorting changes with a dry-run mode, safely moves files into category folders with duplicate name protection, logs sort sessions to JSON, supports undoing the last sort, and exports summary reports.

## Features

- **Folder Scanning (`1`)**: Lists regular non-system files in a chosen folder (or current working directory).
- **Dry-Run Preview (`2`)**: Shows the planned `filename -> Category/` mapping before moving any files.
- **Safe File Sorting (`3`)**: Creates category folders on demand, moves files safely, and appends `_1`, `_2`, etc. when a file with the same name already exists.
- **Undo Last Sort (`4`)**: Restores files from the most recent sort batch back to their original paths and cleans up empty category folders.
- **Customizable Categories (`5`)**: Loads and saves extension rules in `categories.json`, allowing new categories or extensions to be added interactively.
- **Summary Report Export (`6`)**: Appends session logs and writes overall summary statistics to `sort_report.txt`.

## How to Run

Requires Python 3 (standard library only: `os`, `shutil`, `json`, `datetime`).

```bash
python main.py
```

## Sample Output

```text
=== PySortifyCLI ===
1) Scan files in folder
2) Preview file sorting (dry-run)
3) Sort files now
4) Undo last sort
5) View / Add file categories
6) Export summary report
0) Exit
Select an option (0-6): 2
Enter folder path to preview (press Enter for current directory): sample_files

--- Dry-Run Preview (4 file(s)) ---
  notes.txt                    ->  Documents/
  photo.png                    ->  Images/
  script.py                    ->  Code/
  archive.zip                  ->  Others/
```
