import glob
import os

# Get the current working directory
BASE_DIR = os.getcwd()

# Dynamically find a virtual environment folder (for local and PythonAnywhere)
POSSIBLE_ENV_FOLDERS = ["env", "venv", ".virtualenvs"]
ENV_PATH = None

for env_folder in POSSIBLE_ENV_FOLDERS:
    possible_path = os.path.join(BASE_DIR, env_folder)
    if os.path.exists(possible_path):
        ENV_PATH = possible_path
        break


def get_installed_apps_migration_folders():
    """
    Finds migration folders for installed apps inside the Django project.
    Excludes the virtual environment directory if present.
    """
    migration_folders = []

    for root, dirs, files in os.walk(BASE_DIR):
        if "migrations" in dirs:
            # Exclude migrations inside the virtual environment
            if ENV_PATH and root.startswith(ENV_PATH):
                continue
            migration_folders.append(os.path.join(root, "migrations"))

    return migration_folders


def delete_migration_files(migration_folders):
    """
    Deletes all migration files except __init__.py.
    """
    for migration_dir in migration_folders:
        migration_files = glob.glob(os.path.join(migration_dir, "*.py"))

        for file in migration_files:
            if not file.endswith("__init__.py"):  # Keep __init__.py
                os.remove(file)
                print(f"🗑️ Deleted: {file}")


if __name__ == "__main__":
    migration_folders = get_installed_apps_migration_folders()

    if migration_folders:
        print("\n📂 Found migration folders in installed apps:")
        for folder in migration_folders:
            print(f"  - {folder}")

        proceed = (
            input("\n❗ Do you want to DELETE migration files? (y/n): ").strip().lower()
        )

        if proceed == "y":
            delete_migration_files(migration_folders)
            print(
                "\n✅ All migration files (except __init__.py) have been deleted from installed apps."
            )
        else:
            print("❌ Deletion aborted.")
    else:
        print("✅ No migrations folders found in installed apps.")
