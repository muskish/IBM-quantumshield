"""
File Walker - Phase 2, Step 1
Walks through the fake bank environment and lists every relevant file,
grouped by type. This is the first building block of the scanner.
"""

import os

# Path to the fake bank environment we built in Phase 1
BANK_ENV_PATH = "../bank-env"

# File types we care about for this project
RELEVANT_EXTENSIONS = {
    ".py": "source code",
    ".yaml": "service config/blueprint",
    ".yml": "service config/blueprint",
    ".txt": "dependency list",
    ".crt": "certificate",
    ".pem": "key or certificate",
}


def find_relevant_files(root_path: str) -> list:
    """Walks the folder tree and returns a list of (filepath, file_type) tuples."""
    found_files = []

    for current_folder, subfolders, filenames in os.walk(root_path):
        for filename in filenames:
            extension = os.path.splitext(filename)[1].lower()
            if extension in RELEVANT_EXTENSIONS:
                full_path = os.path.join(current_folder, filename)
                file_type = RELEVANT_EXTENSIONS[extension]
                found_files.append((full_path, file_type))

    return found_files


def main():
    print(f"Scanning folder: {BANK_ENV_PATH}\n")

    files = find_relevant_files(BANK_ENV_PATH)

    if not files:
        print("No files found. Check that BANK_ENV_PATH is correct.")
        return

    print(f"Found {len(files)} relevant files:\n")
    for filepath, file_type in files:
        print(f"  [{file_type}] {filepath}")


if __name__ == "__main__":
    main()