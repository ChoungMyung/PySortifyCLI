# v1: Basic CLI menu and folder path input


def show_menu():
    print("\n=== PySortifyCLI v1 ===")
    print("1. Scan folder")
    print("0. Exit")


def main():
    while True:
        show_menu()
        choice = input("Select option: ").strip()
        if choice == "1":
            folder = input("Target folder path: ").strip()
            print(f"Selected folder: {folder}")
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
