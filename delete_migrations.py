import glob
import os


def delete_migration_files():
    base_dir = os.getcwd()  # Get current working directory
    for root, dirs, files in os.walk(base_dir):
        if "migrations" in dirs:  # Look for 'migrations' folder
            migration_dir = os.path.join(root, "migrations")
            migration_files = glob.glob(
                os.path.join(migration_dir, "*.py")
            )  # Find all .py files

            # Delete all migration files except '__init__.py'
            for file in migration_files:
                if not file.endswith("__init__.py"):
                    os.remove(file)
                    print(f"Deleted: {file}")


if __name__ == "__main__":
    delete_migration_files()
    print("\n✅ All migration files (except __init__.py) have been deleted.")
