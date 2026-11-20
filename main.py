from datetime import datetime
import json
import os
import shutil

CONFIG_FILE = "categories.json"
HISTORY_FILE = "history.json"
REPORT_FILE = "sort_report.txt"

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


def load_categories(config_file=CONFIG_FILE):
    if not os.path.exists(config_file):
        save_categories(config_file, DEFAULT_CATEGORIES)
        return {k: list(v) for k, v in DEFAULT_CATEGORIES.items()}
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and data:
                return data
    except (OSError, json.JSONDecodeError):
        pass
    return {k: list(v) for k, v in DEFAULT_CATEGORIES.items()}


def save_categories(config_file, categories):
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[ERROR] Could not save categories: {e}")


def display_menu():
    print("\n=== PySortifyCLI ===")
    print("1) Scan files in folder")
    print("2) Preview file sorting (dry-run)")
    print("3) Sort files now")
    print("4) Undo last sort")
    print("5) View / Add file categories")
    print("6) Export summary report")
    print("0) Exit")
    return input("Select an option (0-6): ").strip()


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
            json.dump(history, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[ERROR] Could not save history: {e}")


def append_sort_report(target_dir, moved_records, report_file=REPORT_FILE):
    # count moved files per category
    counts = {}
    for item in moved_records:
        cat = item["category"]
        counts[cat] = counts.get(cat, 0) + 1

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(report_file, "a", encoding="utf-8") as f:
            f.write(f"=== Sort Session: {timestamp} ===\n")
            f.write(f"Target Directory: {target_dir}\n")
            f.write(f"Total Sorted: {len(moved_records)} file(s)\n")
            for cat, total in sorted(counts.items()):
                f.write(f"  - {cat}: {total}\n")
            f.write("-" * 40 + "\n")
    except OSError as e:
        print(f"[ERROR] Could not write report: {e}")


def export_full_report(history_file=HISTORY_FILE, report_file=REPORT_FILE):
    history = load_history(history_file)
    if not history:
        print("No sorting history available to generate report.")
        return

    total_files = 0
    category_totals = {}
    for batch in history:
        for item in batch.get("files", []):
            total_files += 1
            cat = item["category"]
            category_totals[cat] = category_totals.get(cat, 0) + 1

    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=== PySortifyCLI Summary Report ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Sort Sessions: {len(history)}\n")
            f.write(f"Total Files Organized: {total_files}\n\n")
            f.write("Breakdown by Category:\n")
            for cat, count in sorted(category_totals.items()):
                f.write(f"  * {cat:<12}: {count} file(s)\n")
        print(f"[SAVED] Summary report written to '{report_file}'.")
    except OSError as e:
        print(f"[ERROR] Failed to export report: {e}")


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

    # append batch record to history log and report
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
        append_sort_report(path, moved_records)

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


def manage_categories(categories, config_file=CONFIG_FILE):
    display_categories(categories)
    add = input("\nAdd a new extension rule? (y/n): ").strip().lower()
    if add != "y":
        return

    cat_name = input("Enter category name (e.g., Archives, Music): ").strip()
    if not cat_name:
        print("[ERROR] Category name cannot be empty.")
        return

    ext = input("Enter file extension (e.g., .zip or zip): ").strip().lower()
    if not ext:
        print("[ERROR] Extension cannot be empty.")
        return
    if not ext.startswith("."):
        ext = "." + ext

    # create category list if not exists, then append unique extension
    if cat_name not in categories:
        categories[cat_name] = []
    if ext not in categories[cat_name]:
        categories[cat_name].append(ext)
        save_categories(config_file, categories)
        print(f"[SAVED] Added {ext} to '{cat_name}'.")
    else:
        print(f"[INFO] {ext} already exists in '{cat_name}'.")


def main():
    categories = load_categories()

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
            dry_run(target_dir, categories)

        elif choice == "3":
            target_dir = get_valid_path(
                "Enter folder path to sort (press Enter for current directory): "
            )
            plan = dry_run(target_dir, categories)
            if plan:
                confirm = input("\nProceed with sorting? (y/n): ").strip().lower()
                if confirm == "y":
                    organize_files(target_dir, categories)
                else:
                    print("Sorting cancelled.")

        elif choice == "4":
            undo_last_sort()

        elif choice == "5":
            manage_categories(categories)

        elif choice == "6":
            export_full_report()

        else:
            print("[ERROR] Invalid option. Please choose 0-6.")


if __name__ == "__main__":
    main()