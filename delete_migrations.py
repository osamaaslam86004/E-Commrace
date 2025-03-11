import glob
import os

# Get the current working directory (where manage.py is located)
BASE_DIR = os.getcwd()

# Find virtual environments in both local and PythonAnywhere
POSSIBLE_ENV_FOLDERS = ["env", "venv", ".virtualenvs"]


def find_virtual_env():
    """Finds the virtual environment directory inside or outside BASE_DIR."""
    # Check if env/venv is inside BASE_DIR (local machine case)
    for env_folder in POSSIBLE_ENV_FOLDERS:
        env_path = os.path.join(BASE_DIR, env_folder)
        if os.path.exists(env_path):
            return env_path  # Found env inside E-Commrace

    # If not found, check in the parent directory (PythonAnywhere case)
    PARENT_DIR = os.path.dirname(BASE_DIR)
    for env_folder in POSSIBLE_ENV_FOLDERS:
        env_path = os.path.join(PARENT_DIR, env_folder)
        if os.path.exists(env_path):
            return env_path  # Found env outside E-Commrace (PythonAnywhere case)

    return None  # No virtual environment found


# Get the virtual environment path
ENV_PATH = find_virtual_env()


def get_installed_apps_migration_folders():
    """Finds migration folders in installed apps, excluding virtual environments."""
    migration_folders = []

    for root, dirs, files in os.walk(BASE_DIR):
        if "migrations" in dirs:
            # Exclude migrations inside virtual environment
            if ENV_PATH and root.startswith(ENV_PATH):
                continue
            migration_folders.append(os.path.join(root, "migrations"))

    return migration_folders


def delete_migration_files(migration_folders):
    """Deletes migration files, keeping __init__.py."""
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
