# v3: Safe filename deduplication and moving files
from pathlib import Path
import shutil

CATEGORIES = {
    "Documents": [".pdf", ".txt", ".xlsx", ".csv"],
    "Images": [".jpg", ".jpeg", ".png"],
    "Code": [".py", ".json", ".md"],
    "Archives": [".zip"],
}


def get_unique_destination(dest_dir: Path, filename: str) -> Path:
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize_folder(folder_path: str):
    src_dir = Path(folder_path)
    for item in src_dir.iterdir():
        if not item.is_file():
            continue
        ext = item.suffix.lower()
        category = next((k for k, v in CATEGORIES.items() if ext in v), "Others")
        dest_dir = src_dir / category
        dest_dir.mkdir(exist_ok=True)
        target = get_unique_destination(dest_dir, item.name)
        shutil.move(str(item), str(target))
        print(f"Moved: {item.name} -> {category}/{target.name}")


def main():
    folder = input("Target folder path: ").strip()
    organize_folder(folder)


if __name__ == "__main__":
    main()
