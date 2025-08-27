from tempfile import TemporaryDirectory
from pathlib import Path
import shutil

SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_STATIC_DIR = SCRIPT_DIR / "static"

# Unified working directory for all generated and static files
_temp_dir = TemporaryDirectory()
TEMP_DIR_PATH = Path(_temp_dir.name)
DOWNLOADED_SPEC_PATH = TEMP_DIR_PATH / "openapi.json"

SPEC_FILE_URL = 'https://docs.developers.clio.com/openapi.json'
# SPEC_FILE_PATH = DOWNLOADED_SPEC_PATH

# Copy static files into root of TEMP_DIR_PATH
if LOCAL_STATIC_DIR.exists():
    for item in LOCAL_STATIC_DIR.iterdir():
        dest = TEMP_DIR_PATH / item.name
        if item.is_file():
            shutil.copy2(item, dest)
        elif item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
else:
    print(f'⚠️ Static directory "{LOCAL_STATIC_DIR}" not found, no files copied.')

def export_temp_contents(target_path: str | Path, overwrite: bool = True) -> None:
    """
    Copy all files and directories from the temp directory to a specified directory.

    Args:
        target_path (str | Path): The exact destination directory to write into.
        overwrite (bool): If False, creates a backup of the destination directory.
    """
    dest_dir = Path(target_path).resolve()

    # If the target directory exists and overwrite is False, back it up
    if dest_dir.exists() and not overwrite:
        backup_index = 0
        while True:
            suffix = f".backup{backup_index}" if backup_index else ".backup"
            backup_path = dest_dir.with_name(dest_dir.name + suffix)
            if not backup_path.exists():
                shutil.move(str(dest_dir), str(backup_path))
                print(f"📦 Existing directory moved to: {backup_path}")
                break
            backup_index += 1

    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy contents from temp dir to dest_dir
    for item in TEMP_DIR_PATH.iterdir():
        dest = dest_dir / item.name
        if item.is_file():
            if dest.exists() and not overwrite:
                continue
            shutil.copy2(item, dest)
        elif item.is_dir():
            if dest.exists() and not overwrite:
                continue
            shutil.copytree(item, dest, dirs_exist_ok=True if overwrite else False)

    print(f"✅ Temp directory contents copied to: {dest_dir}")
