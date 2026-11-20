# v2: Scan files and map extensions to categories
from pathlib import Path

DEFAULT_CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".csv"],
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Code": [".py", ".js", ".html", ".css"],
    "Archives": [".zip", ".rar", ".7z"],
}


def detect_category(ext: str, categories: dict) -> str:
    ext = ext.lower()
    for cat, exts in categories.items():
        if ext in exts:
            return cat
    return "Others"


def preview_files(folder_path: str):
    p = Path(folder_path)
    if not p.exists() or not p.is_dir():
        print("Folder not found.")
        return
    for item in p.iterdir():
        if item.is_file():
            cat = detect_category(item.suffix, DEFAULT_CATEGORIES)
            print(f"{item.name} -> {cat}")


def main():
    folder = input("Target folder path: ").strip()
    preview_files(folder)


if __name__ == "__main__":
    main()
