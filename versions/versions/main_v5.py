# v5: Save move history to JSON and support undo
from pathlib import Path
import json
import shutil

HISTORY_FILE = Path("history.json")
CATEGORIES = {
    "Documents": [".pdf", ".txt", ".xlsx", ".csv"],
    "Images": [".jpg", ".jpeg", ".png"],
    "Code": [".py", ".json", ".md"],
    "Archives": [".zip"],
}


def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_history(records: list):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def undo_last_batch():
    records = load_history()
    if not records:
        print("No history to undo.")
        return
    last_batch = records.pop()
    for entry in reversed(last_batch):
        src = Path(entry["to"])
        dst = Path(entry["from"])
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
    save_history(records)
    print("Undo completed.")


def main():
    print("1. Organize folder | 2. Undo last run")
    cmd = input("Choice: ").strip()
    if cmd == "2":
        undo_last_batch()
    elif cmd == "1":
        folder = Path(input("Target folder path: ").strip().strip('"'))
        if not folder.is_dir():
            print("Invalid folder.")
            return
        batch = []
        for item in folder.iterdir():
            if item.is_file() and item.name != HISTORY_FILE.name:
                cat = next((k for k, v in CATEGORIES.items() if item.suffix.lower() in v), "Others")
                dest_dir = folder / cat
                dest_dir.mkdir(exist_ok=True)
                dest_file = dest_dir / item.name
                shutil.move(str(item), str(dest_file))
                batch.append({"from": str(item), "to": str(dest_file)})
        if batch:
            hist = load_history()
            hist.append(batch)
            save_history(hist)
        print(f"Moved {len(batch)} file(s).")


if __name__ == "__main__":
    main()
