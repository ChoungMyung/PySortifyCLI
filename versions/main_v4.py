# v4: Input validation and try/except error handling
from pathlib import Path
import shutil

CATEGORIES = {
    "Documents": [".pdf", ".txt", ".xlsx", ".csv"],
    "Images": [".jpg", ".jpeg", ".png"],
    "Code": [".py", ".json", ".md"],
    "Archives": [".zip"],
}


def prompt_valid_folder() -> Path | None:
    raw = input("Target folder path: ").strip().strip('"')
    if not raw:
        print("Error: Folder path cannot be empty.")
        return None
    target = Path(raw)
    if not target.exists() or not target.is_dir():
        print("Error: Target directory does not exist.")
        return None
    return target


def organize_safe(src_dir: Path):
    for item in src_dir.iterdir():
        if not item.is_file():
            continue
        try:
            ext = item.suffix.lower()
            category = next((k for k, v in CATEGORIES.items() if ext in v), "Others")
            dest_dir = src_dir / category
            dest_dir.mkdir(exist_ok=True)
            dest_file = dest_dir / item.name
            idx = 1
            while dest_file.exists():
                dest_file = dest_dir / f"{item.stem}_{idx}{item.suffix}"
                idx += 1
            shutil.move(str(item), str(dest_file))
            print(f"OK: {item.name} -> {category}/{dest_file.name}")
        except (PermissionError, OSError) as e:
            print(f"Skip {item.name}: {e}")


def main():
    folder = prompt_valid_folder()
    if folder:
        organize_safe(folder)


if __name__ == "__main__":
    main()
