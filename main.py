import os

VERSION = "1.0.0"

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
    print(f"\n=== PySortifyCLI v{VERSION} ===")
    print("1) Scan files in folder")
    print("2) View file categories")
    print("0) Exit")
    return input("Select an option (0-2): ").strip()


def get_valid_path(prompt):
    # loop until user enter a valid folder (empty input default)
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
            total = display_categories(DEFAULT_CATEGORIES)
            print(f"Total: {total} categories")

        else:
            print("[ERROR] Invalid option. Please choose 0-2.")


if __name__ == "__main__":
    main()