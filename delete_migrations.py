import glob
import os

"""
Fixes and Improvements:
Excludes the virtual environment (env) – Prevents deletion of migrations in site-packages.
Keeps __init__.py files – Avoids breaking the migration package structure.
Ensures only Django apps' migrations are deleted – Won't mistakenly remove critical Django files.
"""

# Get the root directory of the Django project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# List all directories inside the project (assumed to be Django apps)
for root, dirs, files in os.walk(BASE_DIR):
    if "migrations" in dirs and "env" not in root:  # Exclude the virtual environment
        migration_path = os.path.join(root, "migrations")
        migration_files = glob.glob(os.path.join(migration_path, "*.py"))

        for file in migration_files:
            if not file.endswith("__init__.py"):  # Keep __init__.py
                os.remove(file)
                print(f"Deleted: {file}")
