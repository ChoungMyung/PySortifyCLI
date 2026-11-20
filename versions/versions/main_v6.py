# v6: Summary statistics and external categories.json support
from pathlib import Path
import json
import shutil

CONFIG_FILE = Path("categories.json")
DEFAULT_CATEGORIES = {
    "Documents": [".pdf", ".txt", ".xlsx", ".csv"],
    "Images": [".jpg", ".jpeg", ".png"],
    "Code": [".py", ".json", ".md"],
    "Archives": [".zip"],
}


def load_categories() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULT_CATEGORIES
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else DEFAULT_CATEGORIES
    except (json.JSONDecodeError, OSError):
        print("Warning: Invalid categories.json, using defaults.")
        return DEFAULT_CATEGORIES


def run_organize(folder_path: str):
    categories = load_categories()
    src_dir = Path(folder_path)
    if not src_dir.is_dir():
        print("Folder does not exist.")
        return
    stats = {}
    for item in src_dir.iterdir():
        if not item.is_file():
            continue
        ext = item.suffix.lower()
        cat = next((k for k, exts in categories.items() if ext in exts), "Others")
        dest_dir = src_dir / cat
        dest_dir.mkdir(exist_ok=True)
        dest_file = dest_dir / item.name
        i = 1
        while dest_file.exists():
            dest_file = dest_dir / f"{item.stem}_{i}{item.suffix}"
            i += 1
        shutil.move(str(item), str(dest_file))
        stats[cat] = stats.get(cat, 0) + 1

    print("\n--- Summary ---")
    for cat, count in sorted(stats.items()):
        print(f"{cat}: {count}")
    print(f"Total moved: {sum(stats.values())}")


def main():
    folder = input("Target folder path: ").strip().strip('"')
    run_organize(folder)


if __name__ == "__main__":
    main()
