from datetime import datetime
import json
import os
import shutil

HISTORY_FILE = "history.json"

# skip files
SYSTEM_FILES = {
    "main.py",
    "categories.json",
    "history.json",
    "sort_report.txt",
    "demo_output.txt",
    "README.md",
    ".gitignore",
}

# default extensions
DEFAULT_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".xlsx", ".txt", ".csv", ".pptx"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv"],
    "Code": [".py", ".js", ".html", ".css", ".json"],
}


def display_menu():
    print("\n=== PySortifyCLI ===")
    print("1) Scan files in folder")
    print("2) Preview file sorting (dry-run)")
    print("3) Sort files now")
    print("4) Undo last sort")
    print("5) View file categories")
    print("0) Exit")
    return input("Select an option (0-5): ").strip()


def get_valid_path(prompt):
    # loop until user enters a valid folder (empty input defaults to cwd)
    while True:
        raw_path = input(prompt).strip()
        if raw_path == "":
            return os.getcwd()
        if os.path.isdir(raw_path):
            return os.path.abspath(raw_path)
        print("[ERROR] Directory not found. Please try again.")


def scan_folder(path):
    files = []
    try:
        for entry in sorted(os.listdir(path)):
            full_path = os.path.join(path, entry)
            # ignore subfolders, hidden files, and project files
            if (
                os.path.isfile(full_path)
                and entry not in SYSTEM_FILES
                and not entry.startswith(".")
            ):
                files.append(entry)
    except OSError as e:
        print(f"[ERROR] Cannot access directory: {e}")
    return files


def classify_file(filename, categories):
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    if not ext:
        return "Others"

    # match extension against category rules
    for category, extensions in categories.items():
        if ext in [e.lower() for e in extensions]:
            return category
    return "Others"


def dry_run(path, categories):
    files = scan_folder(path)
    if not files:
        print("No files found in this directory.")
        return []

    plan = []
    print(f"\n--- Dry-Run Preview ({len(files)} file(s)) ---")
    for filename in files:
        category = classify_file(filename, categories)
        plan.append({"filename": filename, "category": category})
        print(f"  {filename:<28} ->  {category}/")
    return plan


def get_unique_destination(dest_dir, filename):
    dest_path = os.path.join(dest_dir, filename)
    if not os.path.exists(dest_path):
        return dest_path

    # append counter suffix if filename already exists
    base, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_name = f"{base}_{counter}{ext}"
        new_path = os.path.join(dest_dir, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def load_history(history_file):
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def save_history(history_file, history):
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except OSError as e:
        print(f"[ERROR] Could not save history: {e}")


def organize_files(path, categories, history_file=HISTORY_FILE):
    files = scan_folder(path)
    if not files:
        print("No files found to sort.")
        return []

    moved_records = []
    for filename in files:
        category = classify_file(filename, categories)
        dest_dir = os.path.join(path, category)
        os.makedirs(dest_dir, exist_ok=True)

        src_path = os.path.join(path, filename)
        dest_path = get_unique_destination(dest_dir, filename)
        final_name = os.path.basename(dest_path)

        try:
            shutil.move(src_path, dest_path)
            moved_records.append(
                {
                    "original_name": filename,
                    "saved_name": final_name,
                    "category": category,
                    "from": src_path,
                    "to": dest_path,
                }
            )
            print(f"  [MOVED] {filename} -> {category}/{final_name}")
        except OSError as e:
            print(f"  [ERROR] Failed to move {filename}: {e}")

    # append batch record to history log
    if moved_records:
        history = load_history(history_file)
        history.append(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "target_dir": path,
                "files": moved_records,
            }
        )
        save_history(history_file, history)

    print(f"\nDone! Sorted {len(moved_records)} file(s).")
    return moved_records


def undo_last_sort(history_file=HISTORY_FILE):
    history = load_history(history_file)
    if not history:
        print("No sorting history found to undo.")
        return

    last_batch = history.pop()
    print(f"\n--- Undoing sort from {last_batch['timestamp']} ---")
    restored = 0

    for item in reversed(last_batch["files"]):
        current_path = item["to"]
        original_path = item["from"]
        if not os.path.exists(current_path):
            print(f"  [SKIP] Missing file: {item['saved_name']}")
            continue

        try:
            shutil.move(current_path, original_path)
            restored += 1
            print(f"  [RESTORED] {item['category']}/{item['saved_name']} -> {item['original_name']}")

            # remove empty category folder after moving file back
            cat_dir = os.path.dirname(current_path)
            if os.path.isdir(cat_dir) and not os.listdir(cat_dir):
                os.rmdir(cat_dir)
        except OSError as e:
            print(f"  [ERROR] Failed to restore {item['saved_name']}: {e}")

    save_history(history_file, history)
    print(f"\nRestored {restored} file(s).")


def display_categories(categories):
    print("\n--- File Categories ---")
    for category, extensions in categories.items():
        print(f"  * {category:<12}: {', '.join(extensions)}")
    return len(categories)


def main():
    while True:
        choice = display_menu()

        if choice == "0":
            print("Goodbye!")
            break

        elif choice == "1":
            target_dir = get_valid_path(
                "Enter folder path (press Enter for current directory): "
            )
            files = scan_folder(target_dir)
            print(f"\nTarget: {target_dir}")
            if not files:
                print("No files found in this directory.")
            else:
                print(f"Found {len(files)} file(s):")
                for idx, filename in enumerate(files, start=1):
                    print(f"  {idx}. {filename}")

        elif choice == "2":
            target_dir = get_valid_path(
                "Enter folder path to preview (press Enter for current directory): "
            )
            dry_run(target_dir, DEFAULT_CATEGORIES)

        elif choice == "3":
            target_dir = get_valid_path(
                "Enter folder path to sort (press Enter for current directory): "
            )
            plan = dry_run(target_dir, DEFAULT_CATEGORIES)
            if plan:
                confirm = input("\nProceed with sorting? (y/n): ").strip().lower()
                if confirm == "y":
                    organize_files(target_dir, DEFAULT_CATEGORIES)
                else:
                    print("Sorting cancelled.")

        elif choice == "4":
            undo_last_sort()

        elif choice == "5":
            total = display_categories(DEFAULT_CATEGORIES)
            print(f"Total: {total} categories")

        else:
            print("[ERROR] Invalid option. Please choose 0-5.")


if __name__ == "__main__":
    main()