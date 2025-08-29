#HAPPY MAX_WORKERS
import os
import re
import sys
from pathlib import Path
import xxhash  # For fast non-cryptographic hashing of files
import shutil  # For high-level file operations like copy and move
import datetime
import threading
import logging
from typing import Union
import fnmatch  # For Unix-style filename pattern matching
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from exceptions import InvalidPathError, PermissionDeniedError


# A dictionary of file extensions and names categorized as "junk" or temporary.
# This can be used to exclude these files from operations.
JUNK_EXTENSIONS = {
    "fylex_artifacts": [
        ".fylex_deprecated", # For the directory itself
        ".fylex_quarantine",
        "fylex.deprecated" # For the specific folder created in no_change()
    ],
    "temporary_backup": [
        ".tmp", ".temp", ".bak", ".backup", ".bkp", ".old", ".orig", ".save", "~"
    ],
    "system_log": [
        ".log", ".dmp", ".mdmp", ".hdmp", ".ds_store", ".lnk", "thumbs.db",
        "desktop.ini"
    ],
    "dev_artifacts": [
        ".class", ".o", ".obj", ".pyc", ".pyo", ".pyd", ".elc",
        ".egg", ".egg-info", ".whl", ".map", ".coverage", ".gcda", ".gcno",
        ".aux", ".out", ".toc", ".synctex.gz"
    ],
    "platform_trash": [
        ".Trash", ".Trashes", ".Spotlight-V100", ".AppleDouble", ".fseventsd",
        ".apdisk", "ehthumbs.db", ".TemporaryItems", ".DocumentRevisions-V100"
    ],
    "browser_cache": [
        ".cache", ".cached", ".part", ".crdownload", ".download"
    ],
    "editor_ide_junk": [
        ".suo", ".user", ".ncb", ".sdf", ".dbmdl", ".project", ".classpath",
        ".sublime-workspace", ".idea", ".vscode"
    ],
    "ci_cd_test": [
        ".test", ".tmp", ".out", ".stackdump"
    ],
    "document_temp": [
        ".wbk", ".asd", ".tmp", ".~lock"
    ]
}

# --- Constants ---
MAX_RETRIES = 5  # Maximum number of times to retry a failed file operation.
ON_CONFLICT_MODES = ["larger", "smaller", "newer", "older", "rename", "skip", "prompt", "replace"]
DEFAULT_CHUNK_SIZE = 16 * 1024 * 1024  # 16 MB

# --- Use Variables ---
temp_folders = []
func_route = []

# -------- Logger Setup --------
class PrintToLogger:
    """
    A file-like object that redirects stdout to the logging module.
    This allows capturing print statements from other libraries or parts of the code
    and routing them through the configured logger.
    """
    def __init__(self, verbose):
        self.verbose = verbose

    def write(self, msg):
        msg = msg.strip()
        if msg:
            logging.info(msg)
            # If verbose mode is on, also write to the actual standard output.
            if self.verbose:
                sys.__stdout__.write(msg + "\n")
                sys.__stdout__.flush()

    def flush(self):
        # This method is required for file-like objects.
        pass

def safe_logging(verbose=True):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("fylex.log", mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.__stdout__) if verbose else logging.NullHandler()
        ]
    )
    sys.stdout = PrintToLogger(verbose)
    
def log_copier(func_name, summary):
    global func_route
    if func_route[0] == func_name:
        # --- Finalization ---
        if summary:
            for handler in logging.getLogger().handlers:
                handler.flush()
                handler.close()

            logging.shutdown()
            shutil.copy2("fylex.log", summary) # Save the log file to a specified path.
        func_route = []

# -------- Hashing --------
def hash_file(path: Union[str, Path], *, chunk_size: int = DEFAULT_CHUNK_SIZE):
    path = Path(path)
    hasher = xxhash.xxh64()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# -------- Handle renames --------
def handle_rename(src_file, dest_path, src_name, dry_run, is_move):
    base, ext = os.path.splitext(src_name)
    for i in range(1, 100000000):
        new_name = f"{base}({i}){ext}"
        new_path = dest_path / new_name
        if not new_path.exists():
            if dry_run:
                if is_move:
                    logging.info(f"[DRY RUN] Would rename and move to: {new_path}")
                else:
                    logging.info(f"[DRY RUN] Would rename and copy to: {new_path}")
            else:
                if is_move:
                    logging.info(f"Renamed: and moved to avoid conflict: {src_file.name} -> {new_name}")
                    shutil.move(src_file, new_path)
                else:
                    shutil.copy2(src_file, new_path)
                    logging.info(f"Renamed: and copied to avoid conflict: {src_file.name} -> {new_name}")
            return

# -------- Input Prompt --------
def ask_user(question):
    """
    Prompts the user with a question and returns their stripped, lowercase response.
    Uses a lock to ensure thread-safe I/O.
    """
    sys.__stdout__.write(question)
    sys.__stdout__.flush()
    return input().strip().lower()

# -------- Delete Empty Directories --------
def delete_empty_dirs(target):
    """
    Recursively deletes all empty subdirectories within a given target directory.
    It traverses the directory tree from the bottom up to ensure child directories
    are removed before their parents.
    """
    root_path = Path(target)
    if not root_path.is_dir():
        raise ValueError(f"{target} is not a valid directory.")
    deleted_count = 0
    # Traverse from the bottom up (sorted reverse) to delete empty children first.
    for dir_path in sorted(root_path.rglob('*'), reverse=True):
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            try:
                dir_path.rmdir()
                deleted_count += 1
            except OSError as e:
                logging.error(f"Failed to delete {dir_path}: {e}")
    logging.info(f"Removed: {deleted_count} empty directories from {target} after flattening.")
    return deleted_count

# -------- Validators --------
def is_subpath(src: Path, dest: Path) -> bool:
    """
    Checks if the source path is a subpath of the destination path.
    This is important to prevent infinite recursion, e.g., copying a folder into itself.
    """
    try:
        src = Path(src).resolve()
        dest = Path(dest).resolve()
        # This will raise a ValueError if src is not a subpath of dest.
        src.relative_to(dest)
        return src != dest
    except ValueError:
        return False

def validator(src, dest, no_create, recursive_check):
    """
    Validates source and destination paths before starting any operation.
    Raises errors for common issues like source not existing, destination being the same as source,
    or being unable to create the destination directory.
    """
    src_path = Path(src)
    dest_path = Path(dest)
    abs_src_path = src_path.resolve(strict=False)

    if abs_src_path == dest_path.resolve(strict=False):
        raise ValueError(f"Source and destination are the same file: {abs_src_path}")
    if not src_path.exists():
        raise InvalidPathError(str(src_path))
    if not dest_path.exists():
        if no_create:
            raise InvalidPathError(str(dest_path), "Destination does not exist and creation is disabled.")
        try:
            dest_path.mkdir(parents=True, exist_ok=True)
            temp_folders.append(dest_path.resolve())
        except PermissionError:
            raise PermissionDeniedError(str(dest_path), "write")
    if recursive_check and is_subpath(src, dest):
        raise ValueError("Cannot enable recursive_check when src is inside dest — this can cause unintended behavior.")

# -------- Backup files --------
def backup(backup_dir, dest_file, dry_run):
    try:
        backup_dir = backup_dir / "fylex.deprecated"

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_file = backup_dir / f"{dest_file.stem}.{timestamp}{dest_file.suffix}"

        if not dry_run:
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(dest_file, backup_file)
    except Exception as e:
        logging.error(f"Could not back up {dest_file}: {e}")

# -------- Depth Search Directories --------
def depth_first_rglob(root: Path, pattern="*", exclude="fylex.deprecated"):
        root = Path(root)
        exclude = {exclude} if isinstance(exclude, str) else set(exclude or [])
        for path in sorted(root.iterdir()):
            if path.name in exclude:
                continue
            if path.is_dir():
                yield from depth_first_rglob(path, pattern, exclude)
            elif path.match(pattern):
                yield path

# -------- Metadata Gathering --------
def file_filter(directory, match_regex=None, match_names=None, exclude_regex=None, exclude_names=None, recursive_check=False, has_extension=False, is_nest=False, nest_filter=None):
    """
    Scans a directory for files, applying various filters.
    It can operate in two modes:
    1. is_nest=False: Gathers file data and creates a `_filter` set based on size or size+extension.
    2. is_nest=True: Uses a pre-existing `nest_filter` to find matching files in the destination.
    """
    file_data, _filter = {}, set()
    match_re = re.compile(match_regex) if match_regex else None
    exclude_re = re.compile(exclude_regex) if exclude_regex else None
    dir_path = Path(directory)
    
    # Decide whether to scan recursively or just the top level.
    entries = dir_path.rglob("*") if (recursive_check and not is_nest) else dir_path.iterdir()
    
    for entry in entries:
        if entry.is_dir():
            continue
        name = entry.name
        # Apply exclusion filters
        if exclude_re and exclude_re.fullmatch(name):
            continue
        if exclude_names and name in exclude_names:
            continue
        # Apply inclusion filters
        if not ((match_re and match_re.fullmatch(name)) or (match_names and name in match_names)):
            continue
            
        try:
            file_size = entry.stat().st_size
            file_suffix = entry.suffix.lower()
        except:
            logging.error("File: {entry} vanished before operation")
            continue
        
        # When checking the destination ('nest'), use the filter from the source scan.
        if is_nest:
            if has_extension:
                if (file_size, file_suffix) not in nest_filter:
                    continue
            else:
                if file_size not in nest_filter:
                    continue
        
        # Hash the file to get a unique identifier.
        file_hash = hash_file(entry)
        file_data[(file_hash, file_size)] = {"name": name, "path": entry.resolve()}
        
        # When scanning the source, build up the filter for the destination scan.
        if not is_nest:
            if has_extension:
                _filter.add((file_size, file_suffix))
            else:
                _filter.add(file_size)
                
    return (file_data, _filter) if not is_nest else file_data

def folder_filter(target, match_regex=r".+", match_names=[], exclude_regex=None, exclude_names=[], levels=1):
    """
    Recursively finds all files within subdirectories up to a specified depth (`levels`).
    This is used by the `spill` function.
    """
    
    match_re = re.compile(match_regex) if match_regex else None
    exclude_re = re.compile(exclude_regex) if exclude_regex else None
    dir_path = Path(target).resolve()

    def recursive(_path, current_level, processed):
        try:
            entries = list(_path.iterdir())
        except PermissionError:
            logging.warning(f"Permission denied: {_path}")
            return
        for entry in entries:
            name = entry.name

            if entry.is_dir():
                if name == "fylex.deprecated":
                    continue
                if levels == -1 or current_level < levels:
                    recursive(entry, current_level + 1, processed)
                continue  # skip dir from matching below

            # Now we know it's a file:
            if exclude_re and exclude_re.fullmatch(name):
                continue
            if exclude_names and name in exclude_names:
                continue
            if not ((match_re and match_re.fullmatch(name)) or (match_names and name in match_names)):
                continue
            # Include based on depth (only if deeper than root)
            if current_level > 0 or levels == 0:
                processed.append(entry)
        return processed
    return recursive(dir_path, 0, [])


# -------- Regex compilation --------
def sanitize_glob_regex(glob_pattern):
    """Converts a glob pattern into a regex pattern, stripping the default anchors."""
    glob_re = fnmatch.translate(glob_pattern)
    # fnmatch.translate wraps the pattern in `(?s:...)` and `\Z`
    if glob_re.startswith("(?s:") and glob_re.endswith(")\\Z"):
        return glob_re[4:-3]
    return glob_re

def extract_global_flags(regex):
    """Separates global regex flags (e.g., `(?i)`) from the regex pattern itself."""
    match = re.match(r"^\(\?([aiLmsux]+)\)", regex)
    if match:
        return match.group(1), regex[match.end():]
    return "", regex

def combine_regex_and_glob(user_regex, glob_pattern):
    """Combines a user-provided regex and a glob pattern into a single regex."""
    glob_part = sanitize_glob_regex(glob_pattern) if glob_pattern else ""
    user_flags, user_core = extract_global_flags(user_regex or "")
    
    combined_core = ""
    if user_core and glob_part:
        # Combine with a non-capturing group OR
        combined_core = f"(?:{user_core})|(?:{glob_part})"
    elif user_core:
        combined_core = user_core
    elif glob_part:
        combined_core = glob_part
    
    # Re-apply the global flags if they existed.
    if user_flags:
        return f"(?{user_flags}:{combined_core})"
    else:
        return combined_core

# -------- File Copying/Moving Task --------
def file_copy_or_move_task(file_key, src_path, dest_path, src_name, file_nest, on_conflict, interactive, verbose, dry_run, summary, move):
    src_file = src_name
    dest_file = dest_path / src_name.name
    src_name = src_name.name
    retries, proceed = 0, True

    if interactive:
        response = ""
        if move:
            response = ask_user(f"Move {src_file} to {dest_file}? [y/N]: ")
        else:
            response = ask_user(f"Copy {src_file} to {dest_file}? [y/N]: ")
        proceed = response == "y"
        if not proceed:
            if move:
                logging.info(f"Moving of {dest_file} was skipped by user.")
            else:
                logging.info(f"Copying of {dest_file} was skipped by user.")
            return True

    while retries < MAX_RETRIES and proceed:
        try:
            if file_key in file_nest:
                existing_name = file_nest[file_key]["name"]
                existing_file = dest_path / existing_name
                if dry_run:
                    logging.info(f"[DRY RUN] Duplicate would have been renamed: {existing_name} to {src_name}")
                    return True  
                else:
                    if ( existing_name != src_name ):
                        shutil.move(existing_file, dest_file)
                        logging.info(f"Duplicate renamed: {existing_name} to {src_name}")
                        if move:
                            backup(src_path, src_file, dry_run)
                        return True
                    else:
                        logging.info(f"File already present: {file_nest[file_key]['path']}")
                        if move:
                            backup(src_path, src_file, dry_run)
                        return True

            if dest_file.exists():
                # Conflict handling
                try:
                    native_size = dest_file.stat().st_size
                    native_time = dest_file.stat().st_mtime
                except:
                    logging.error(f"File: {dest_file} vanished before operation")
                    continue
                try:
                    immigrant_size = src_file.stat().st_size
                    immigrant_time = src_file.stat().st_mtime
                except:
                    logging.error(f"File: {src_file} vanished before operation")
                    continue
                def replace():
                    #backup_dir = dest_path / "fylex.deprecated"
                    backup(dest_path, dest_file, dry_run)
                    if dry_run:
                        logging.info(f"[DRY RUN] Would have replaced: {dest_file} with {src_file}")
                    else:
                        logging.info(f"Replacing: {dest_file} with {src_file}")
                        shutil.copy2(src_file, dest_file)


                def no_change():
                    if move:
                        #backup_dir = src_path / "fylex.deprecated"
                        backup(src_path, src_file, dry_run)
                    if dry_run:
                        logging.info(f"[DRY RUN] No changes to: {dest_file}")
                    else:
                        logging.info(f"No changes to: {dest_file}")

                            
                if dest_file.is_dir():
                    logging.warning(f"A folder with the same name exists in the destination directory: {dest_file}")
                    base, ext = os.path.splitext(src_name)
                    i = 1
                    new_name = f"{base}({i}){ext}"
                    new_file = dest_path / new_name
                    while new_file.exists():
                        i += 1
                        new_name = f"{base}({i}){ext}"
                        new_file = dest_path / new_name
                    if dry_run:
                        logging.info(f"[DRY RUN] Would have renamed: {base} to {new_file}")
                    else:
                        logging.info(f"Renaming: {base} to {new_file}")
                        shutil.copy2(src_file, new_file)
                    return True
                
                elif dest_file.is_file():
                    if on_conflict == "replace":
                        replace()
                    elif on_conflict == "larger":
                        if native_size >= immigrant_size:
                            no_change()
                            return True
                        replace()
                    elif on_conflict == "smaller":
                        if native_size <= immigrant_size:
                            no_change()
                            return True
                        replace()
                    elif on_conflict == "newer":
                        if native_time >= immigrant_time:
                            no_change()
                            return True
                        replace()
                    elif on_conflict == "older":
                        if native_time <= immigrant_time:
                            no_change()
                            return True
                        replace()
                    elif on_conflict == "skip":
                        if dry_run:
                            logging.info(f"[DRY RUN] Would have been skipped due to conflict: {dest_file}")
                        else:
                            logging.info(f"Skipping due to conflict: {dest_file}")
                        return True
                    elif on_conflict == "rename":
                        base, ext = os.path.splitext(src_name)
                        i = 1
                        new_name = f"{base}({i}){ext}"
                        new_file = dest_path / new_name
                        while new_file.exists():
                            i += 1
                            new_name = f"{base}({i}){ext}"
                            new_file = dest_path / new_name
                        if dry_run:
                            logging.info(f"[DRY RUN] Would have renamed: {base} to {new_file}")
                        else:
                            logging.info(f"Renaming: {base} to {new_file}")
                            shutil.copy2(src_file, new_file)
                        return True
                    elif on_conflict == "prompt":
                        response = ask_user(f"Replace {dest_file} with {src_file}? [y/N]: ")
                        if response == "y":
                            if dry_run:
                                logging.info(f"[DRY RUN] Would have replaced: {dest_file} with {src_file}")
                            else:
                                replace()
                        else:
                            if dry_run:
                                logging.info(f"Would have been skipped by user: {dest_file}")
                            else:
                                logging.info(f"Skipped by user: {dest_file}")
                            return True
                    else:
                        logging.error(f"Unrecognized on_conflict mode supplied: {on_conflict}\nChoose from: {ON_CONFLICT_MODES}")
            else:
                if dry_run:
                    if move:
                        logging.info(f"[DRY RUN] Would have moved: {src_file} -> {dest_file}")
                    else:
                        logging.info(f"[DRY RUN] Would have copied: {src_file} -> {dest_file}")
                    return True
                shutil.copy2(src_file, dest_file)

            
            if not dry_run:
                new_hash = hash_file(dest_file)
                try:
                    new_size = dest_file.stat().st_size
                except:
                    logging.error(f"File: {dest_file} vanished before operation")
                    continue
                if (new_hash, new_size) != file_key:
                    logging.warning(f"Hash mismatch: {dest_file}. Retrying...")
                    retries += 1
                    try:
                        dest_file.unlink(missing_ok=True)
                    except Exception as e:
                        logging.warning(f"Could not clean up file {dest_file}: {e}")
                    continue
                if move:
                    os.remove(src_file)
                    logging.info(f"Moved and verified: {src_file} -> {dest_file}")
                else:
                    logging.info(f"Copied and verified: {src_file} -> {dest_file}")
                return True
            else:
                if move:
                    logging.info(f"[DRY RUN] Would have moved and verified: {src_file} -> {dest_file}")
                else:
                    logging.info(f"[DRY RUN] Would have copied and verified: {src_file} -> {dest_file}")
                return True

        except Exception as e:
            retries += 1
            if retries >= MAX_RETRIES:
                if move:
                    logging.error(f"Failed to move {src_file} after MAX_RETRIES. \nError: {e}")
                else:
                    logging.error(f"Failed to copy {src_file} after MAX_RETRIES. \nError: {e}")
                return False

# -------- Main fileprocess --------
def fileprocess(src, dest, no_create=False, interactive=False, dry_run=False, match_regex=None, match_names=None, match_glob=None,
                exclude_regex=None, exclude_names=None, exclude_glob=None, summary=None, on_conflict="rename", 
                max_workers=4, verbose=False, recursive_check=False, has_extension=False, move=False):
    """
    The main orchestrator function. It sets up logging, validates paths,
    gathers file metadata from source and destination, and then dispatches
    the copy/move tasks to a thread pool.
    """
    # --- Setup ---
    match_regex = combine_regex_and_glob(match_regex, match_glob)
    exclude_regex = combine_regex_and_glob(exclude_regex, exclude_glob)

    if not (match_regex or match_names):
        match_regex = r".+" # Match all files if no specific match pattern is given

    # Reset and configure logging for this run.
    safe_logging(verbose)

    src_path = Path(src)
    dest_path = Path(dest)

    # If a single file is provided as the source, adjust parameters to handle it correctly.
    if src_path.is_file():
        match_names = [src_path.name]
        src_path = src_path.parent
        match_regex = None
    
    # --- Execution ---
    validator(src, dest, no_create, recursive_check)

    # Scan source and destination directories
    file_birds, nest_filter = file_filter(src_path, match_regex, match_names, exclude_regex, exclude_names, recursive_check, has_extension, False, None)
    file_nest = file_filter(dest_path, ".+", [], None, [], recursive_check, has_extension, True, nest_filter)

    if not file_birds:
        logging.error("No files match the given filters/description.")
        return
    logging.info(f"Collected {len(file_birds)} source file(s)")
    logging.info(f"Nested filter has {len(nest_filter)} entries: {nest_filter}")
    logging.info(f"Matched {len(file_nest)} file(s) at destination")
    
    for file_key, info in file_birds.items():
        file_copy_or_move_task(file_key, src_path, dest_path, info["path"], file_nest, on_conflict, interactive, verbose, dry_run, summary, move)

 
# -------- Main Smart Copy --------
def copy_files(src, dest, no_create=False, interactive=False, dry_run=False, match_regex=None, match_names=None, match_glob=None,
               exclude_regex=None, exclude_names=None, exclude_glob=None, summary=None,
               on_conflict="rename", max_workers=4, verbose=False, recursive_check=False, has_extension=False):
    """Public-facing function for copying files. A wrapper around `fileprocess`."""
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "copy_files"
    func_route.append(func_name)
    fileprocess(src, dest, no_create, interactive, dry_run, match_regex, match_names, match_glob,
                exclude_regex, exclude_names, exclude_glob, summary, on_conflict.lower(), max_workers, verbose, recursive_check, has_extension, move=False)
    log_copier(func_name, summary)

# -------- Main Smart Move --------
def move_files(src, dest, no_create=False, interactive=False, dry_run=False, match_regex=None, match_names=None, match_glob=None,
               exclude_regex=None, exclude_names=None, exclude_glob=None, summary=None,
               on_conflict="rename", max_workers=4, verbose=False, recursive_check=False, has_extension=False):
    """Public-facing function for moving files. A wrapper around `fileprocess`."""
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "move_files"
    func_route.append(func_name)
    fileprocess(src, dest, no_create, interactive, dry_run, match_regex, match_names, match_glob,
                exclude_regex, exclude_names, exclude_glob, summary, on_conflict.lower(), max_workers, verbose, recursive_check, has_extension, move=True)
    log_copier(func_name, summary)

# -------- Main Spill --------
def spill(target, interactive=False, dry_run=False, match_regex=None, match_names=None, match_glob=None,
          exclude_regex=None, exclude_names=None, exclude_glob=None, summary=None,
          on_conflict="rename", max_workers=4, levels=-1, verbose=False):
    """
    Moves files from subdirectories into the parent `target` directory.
    `levels` controls the depth of subdirectories to scan (-1 for infinite).
    """
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "spill"
    func_route.append(func_name)
    target = Path(target)
    if not target.is_dir():
        raise ValueError(f"Invalid path or not a directory: {target}")

    match_regex = combine_regex_and_glob(match_regex, match_glob)
    exclude_regex = combine_regex_and_glob(exclude_regex, exclude_glob)

    if not (match_regex or match_names):
        match_regex = r".+"

    # Setup logging
    safe_logging(verbose)
    
    # Find all files in subfolders that match the criteria.
    files_to_move = folder_filter(target, match_regex, match_names, exclude_regex, exclude_names, levels)

    if not files_to_move:
        logging.error("No files match the given filters/description.")
        return
    logging.info(f"Found {len(files_to_move)} files to spill.")
    
    # Use the `move_files` function for each file found.
    for file_path in files_to_move:
        # Note: This calls move_files for each individual file.
        # It could be slightly more efficient to batch them, but this is simpler and safer.
        move_files(str(file_path), str(target), True, interactive, dry_run, None, [file_path.name], None, 
                   None, None, None, summary, on_conflict, max_workers, verbose, False, False)
    log_copier(func_name, summary)

# -------- Main flatten --------
def flatten(target, interactive=False, dry_run=False, summary=None, on_conflict="rename", max_workers=4, verbose=False):
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "flatten"
    func_route.append(func_name)
    """
    Flattens a directory structure by moving all files from all subdirectories
    into the root `target` directory and then deleting the now-empty subdirectories.
    """
    # First, spill all files from all levels.
    spill(target, interactive, dry_run, ".+", None, None, None, None, None, summary, on_conflict, max_workers, -1, verbose)
    
    # Then, clean up the empty directories left behind.
    if not dry_run:
        empty_dirs_count = delete_empty_dirs(target)
    else:
        logging.info(f"[DRY RUN] Would have flattened and removed empty directories from {target}.")
    log_copier(func_name, summary)

# -------- Main categorize --------
def categorize_by_name(target, grouping, default=None, interactive=False, dry_run=False, summary=None, max_workers=4, verbose=False):
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "categorize_by_name"
    func_route.append(func_name)
    for key in grouping:
        # Handle case: key is a plain string (assumed to be a regex)
        if isinstance(key, str):
            move_files(target, grouping[key], interactive=interactive, dry_run=dry_run,
                match_regex=key, summary=summary, on_conflict="rename", max_workers=max_workers,
                verbose=verbose, recursive_check=False, has_extension=False, no_create=False
            )
        # Handle case: key is a tuple like ("*.txt", "glob") or ("abc.*", "regex")
        elif isinstance(key, tuple):
            if len(key) != 2:
                raise ValueError(f"Categorization key tuples must have exactly 2 elements: {key}")
            pattern, mode = key
            mode = mode.lower()
            if mode not in ["regex", "glob"]:
                raise ValueError(f"Invalid mode in key {key}. Expected 'regex' or 'glob'.")

            move_files( target, grouping[key], interactive=interactive, dry_run=dry_run, match_regex=pattern if mode == "regex" else None,
                match_glob=pattern if mode == "glob" else None, summary=summary, on_conflict="rename", max_workers=max_workers,
                verbose=verbose, recursive_check=False, has_extension=False, no_create=False
            )
        else:
            raise TypeError(f"Invalid key type: {key} (must be str or tuple)")

    if default:
        move_files(target, default, interactive=interactive, dry_run=dry_run, match_regex=r".+",
                match_glob=None, summary=summary, on_conflict="rename", max_workers=max_workers,
                verbose=verbose, recursive_check=False, has_extension=False, no_create=False)
    for dest_dir in temp_folders:
        if dest_dir.is_dir() and not any(dest_dir.iterdir()) and dry_run:
            dest_dir.rmdir()
    log_copier(func_name, summary)

def categorize_by_size(target, grouping, default=None, interactive=False, dry_run=False, summary=None, max_workers=4, verbose=False):
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "categorize_by_size"
    func_route.append(func_name)
    safe_logging(verbose)
    all_files = Path(target).glob("*")
    if not all_files:
        logging.error("{Categorize} found no files to operate on.")
        return
    for file in all_files:
        if not file.is_file():
            continue
        try:
            size = file.stat().st_size
        except:
            logging.error(f"File: {file} vanished before operation")
            continue
        dest_dir = default
        try:
            dest_dir = grouping[size]
        except:
            for key, path in grouping.items():
                if isinstance(key, tuple):
                    a, b = key
                    if isinstance(b, str) and b.lower() == "max":
                        if a <= size:
                            dest_dir = path
                            break
                    else:
                        if a <= size <= b:
                            dest_dir = path
                            break
        if dest_dir:
            move_files(str(file), dest_dir, False, interactive, dry_run, None, None, None, 
                       None, None, None, summary, "rename", max_workers, verbose, False, False)
    if default:
        move_files(target, default, interactive=interactive, dry_run=dry_run, match_regex=r".+",
                match_glob=None, summary=summary, on_conflict="rename", max_workers=max_workers,
                verbose=verbose, recursive_check=False, has_extension=False, no_create=False)
                
    for dest_dir in temp_folders:
        if dest_dir.is_dir() and not any(dest_dir.iterdir()) and dry_run:
            dest_dir.rmdir()
    log_copier(func_name, summary)
                
def categorize_by_ext(target, default=None, interactive=False, dry_run=False, summary=None, max_workers=4, verbose=False, recursive_check=False):
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "categorize_by_ext"
    func_route.append(func_name)
    safe_logging(verbose)
    target_path = Path(target).resolve()
    all_files = target_path.glob("*")
    if not all_files:
        logging.error("{Categorize} found no files to operate on.")
        return
    ext_files_map = {}

    for file in all_files:
        if not file.is_file():
            continue
        logging.info(f"Processing file: {file}")

        # Get full extension (e.g., ".tar.gz" or just ".txt")
        suffix = "".join(file.suffix).lower() or "_no_ext"

        # Destination directory: either per extension or default
        if suffix == "_no_ext":
            dest_dir = Path(default) if default else (target_path / "_no_ext")
        else:
            dest_dir = target_path / suffix

        # Accumulate files for each destination
        ext_files_map.setdefault(dest_dir, []).append(file.name)

    # Batch move files per extension
    for dest_dir, filenames in ext_files_map.items():
        move_files( target, str(dest_dir), no_create=False, interactive=interactive, dry_run=dry_run, 
        match_names=filenames, summary=summary, on_conflict="rename", max_workers=max_workers, verbose=verbose, recursive_check=False, has_extension=False )
        if dry_run:
            if dest_dir.is_dir() and not any(dest_dir.iterdir()) and dest_dir.resolve() in temp_folders:
                dest_dir.rmdir()
    log_copier(func_name, summary)

def categorize(target, categorize_by, grouping=None, default = None, interactive=False, dry_run=False, summary=None, max_workers=4, verbose=False):
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "categorize"
    func_route.append(func_name)
    if categorize_by == "name":
        categorize_by_name(target, grouping, default, interactive, dry_run, summary, max_workers, verbose)
    elif categorize_by == "size":
        categorize_by_size(target, grouping, default, interactive, dry_run, summary, max_workers, verbose)
    elif categorize_by == "ext":
        categorize_by_ext(target, default, interactive, dry_run, summary, max_workers, verbose)
    else:
        raise ValueError(f"Unrecognized categorize_by mode provided: {categorize_by}. Choose from: [\"name\",\"size\",\"ext\"]")
    log_copier(func_name, summary)
    
# -------- Main Refine --------
def refine(target, interactive=False, dry_run=False, match_regex=None, match_names=None, match_glob=None,
          exclude_regex=None, exclude_names=None, exclude_glob=None, summary=None,
          on_conflict="rename", max_workers=4, recursive_check=False, verbose=False):
    """
    Refines the target directory by removing duplicates.
    Loose files are moved to backups rather than the ones in organized directories.
    """
    if interactive and dry_run:
        raise ValueError("Interactive and Dry Run cannot be enabled simultaneously.")
                
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "refine"
    func_route.append(func_name)
    target = Path(target)
    if not target.is_dir():
        raise ValueError(f"Invalid path or not a directory: {target}")
    
    match_regex = combine_regex_and_glob(match_regex, match_glob)
    exclude_regex = combine_regex_and_glob(exclude_regex, exclude_glob)
    
    if not (match_regex or match_names):
        match_regex = r".+"
    
    match_re = re.compile(match_regex) if match_regex else None
    exclude_re = re.compile(exclude_regex) if exclude_regex else None

    # Setup logging
    safe_logging(verbose)
    # Find all files in subfolders that match the criteria.
    # logging.info(f"Found {len(files_to_move)} files to check for refinement.")
    refine_dict = {}
    file_iter = depth_first_rglob(target) if recursive_check else target.glob("*")
    if not file_iter:
        logging.error("No files match the given filters/description.")
        return
    for file_path in file_iter:
        if "fylex.deprecated" in file_path.parts:
            continue
        if file_path.is_dir():
            continue
        name = file_path.name
        # Apply exclusion filters
        if exclude_re and exclude_re.fullmatch(name):
            continue
        if exclude_names and name in exclude_names:
            continue
        # Apply inclusion filters
        if not ((match_re and match_re.fullmatch(name)) or (match_names and name in match_names)):
            continue
        try:
            file_size = file_path.stat().st_size
        except:
            logging.error(f"{file_path} vanished before operation")
            continue
        try:
            if refine_dict[file_size][None]:
                refine_dict[file_size][hash_file(refine_dict[file_size][None])] = file_path
                del refine_dict[file_size][None]
            hash_value = hash_file(file_path)
            if hash_value in refine_dict[file_size].keys():
                logging.info(f"Duplicate: {file_path} is a duplicate of: {refine_dict[file_size][hash_value]}")
                if not dry_run:
                    if interactive and ask_user(f"Do you wish to deprecate {file_path}? [y/N]") != "y":
                        logging.info(f"Deprecation of {file_path} halted by user.")
                        continue
                    backup(target, Path(file_path), dry_run)

                    logging.info(f"Duplicate: {file_path} safely backed up at {os.path.join(target,'fylex.deprecate')}")
                else:
                    logging.info(f"[DRY RUN] Duplicate: {file_path} would have been safely backed up at {os.path.join(target,'fylex.deprecate')}")
            else:
                refine_dict[file_size].append(hash_value)
                if not dry_run:
                    logging.info(f"File retained: {file_path}")
                else:
                    logging.info(f"[DRY RUN] File would have been retained: {file_path}")
        except:
            refine_dict[file_size] = {None: str(file_path)}
            if not dry_run:
                logging.info(f"File retained: {file_path}")
            else:
                logging.info(f"[DRY RUN] File would have been retained: {file_path}")
    log_copier(func_name, summary)
    
# -------- Main Folder identity --------
def folder_fingerprint(path: Path):
    try:
        return (f.stat().st_size for f in path.rglob("*") if (f.is_file() and "fylex.deprecated" not in f.parts))
    except:
        logging.error(f"External interference in {path} caused troubles.")
        sys.exit(1)

def hash_files_size_based(folder: Path, file_size):
    """Hash files having size = file_size"""
    try:
        return {
            str(f): hash_file(f)
            for f in sorted(folder.rglob("*"), key=lambda x: x.stat().st_size)
            if f.is_file() and f.stat().st_size == file_size and "fylex.deprecated" not in f.parts
        }
    except:
        logging.error(f"External interference in {folder} caused troubles.")
        sys.exit(1)
    
# -------- Recursive Operations--------
def rec_ops(src, dest, verbose, max_workers, mode="copy"):
    copy_files(src, dest, verbose=verbose) if mode == "copy" else move_files(src, dest, verbose=verbose)
    for folder in src.iterdir():
        if folder.is_dir():
            new_folder = dest / folder.name
            new_folder.mkdir(exist_ok=False)
            rec_ops(folder, new_folder, verbose, mode)
            
# -------- Main Folderprocess --------
def folderprocess(src, dest, mode, no_create=False, interactive=False, dry_run=False, match_regex=None, match_names=None, match_glob=None,
               exclude_regex=None, exclude_names=None, exclude_glob=None, summary=None, on_conflict="rename", max_workers=4, 
               recursive_check=False, verbose=False):
    match_regex = combine_regex_and_glob(match_regex, match_glob)
    exclude_regex = combine_regex_and_glob(exclude_regex, exclude_glob)
    
    if not (match_regex or match_names):
        match_regex = r".+"
    
    match_re = re.compile(match_regex) if match_regex else None
    exclude_re = re.compile(exclude_regex) if exclude_regex else None

    # Setup logging
    safe_logging(verbose)

    src = Path(src)
    dest = Path(dest)
    
    if not dest.exists():
        if not no_create:
            dest.mkdir(exist_ok=True, parents=True)
        else:
            raise InvalidPathError(str(dest), "Destination does not exist and creation is disabled.")
            
    if src.exists():
        if not src.is_dir():
            raise ValueError(f"Given src path is not a directory: {src}")
    else:
        raise ValueError(f"Given src path does not exist: {src}")
    if src.absolute() == dest.absolute():
        raise ValueError(f"Source and destination paths cannot be the same.")
        
    existing_folder_fingerprints = {}
    path_and_size_dict = {}
    
    def key_maker(target):
        return tuple(sorted([file_size for file_size in folder_fingerprint(Path(target)) if file_size != 0]))
    
    def path_and_size_dict_updater():
        for folder in dest.rglob("*"):
            if "fylex.deprecated" in folder.parts:
                continue
            if folder.is_dir() and str(folder.resolve()) not in path_and_size_dict:
                key = key_maker(folder)
                existing_folder_fingerprints.setdefault(key, []).append(str(folder.resolve()))
                path_and_size_dict[str(folder.resolve())] = key
            
    generator = (src.iterdir() if not recursive_check else src.rglob("*"))
    
    if not any(generator):
        logging.error("No files found")
    
    for folder_path in generator:
        if "fylex.deprecated" in folder_path.parts:
            continue
        src_hash_key = {}
        if "fylex.deprecated" in folder_path.parts:
            continue
        if not folder_path.is_dir():
            continue
        name = folder_path.name
        # Apply exclusion filters
        if exclude_re and exclude_re.fullmatch(name):
            continue
        if exclude_names and name in exclude_names:
            continue
        # Apply inclusion filters
        if not ((match_re and match_re.fullmatch(name)) or (match_names and name in match_names)):
            continue
            
        key = key_maker(folder_path)
        if not key: 
            continue
            
        def sequential_hash_compare(target, size):
            file_hashes = []
            target = Path(target)
            for file in target.rglob("*"):
                if "fylex.deprecated" in file.parts:
                    continue
                if not file.is_file():
                    continue
                try:
                    if file.stat().st_size == size:
                        try:
                            file_hashes.append(hash_file(file))
                        except Exception as e:
                            logging.warning(f"Failed to hash {file}: {e}")
                except:
                    logging.error(f"File {file} no longer exists")
            return sorted(file_hashes)
        
        def folder_mechanism():
            final_dir = dest / folder_path.name
            logging.info(f"Entered folder copying mechanism: {final_dir}")
            def folder_replace():
                if not dry_run:
                    if interactive and ask_user(f"Replace {final_dir} with {folder_path}? [y/N]: ") != "y":
                        return
                    backup(dest, final_dir, dry_run)
                    #COPY PROCESS
                    rec_ops(folder_path, final_dir, verbose, max_workers, mode)
                    path_and_size_dict_updater()
                    logging.info(f"{final_dir} replaced with {folder_path}")
                else:
                    logging.info(f"[DRY RUN] {final_dir} would have been replaced with {folder_path}")
                path_and_size_dict_updater()
                
            def no_change():
                if mode == "move":
                    #backup_dir = src_path / "fylex.deprecated"
                    backup(src, folder_path, dry_run)
                if dry_run:
                    logging.info(f"[DRY RUN] No changes to: {final_dir}")
                else:
                    logging.info(f"No changes to: {final_dir}")
                path_and_size_dict_updater()
                
            if final_dir.exists():
                logging.info(f"Path {final_dir} already exists")
                if final_dir.is_file():
                    copy_to = ""
                    suffix_index = 1
                    while Path(str(final_dir)+f"({suffix_index})").exists():
                        suffix_index += 1
                    copy_to = Path(str(final_dir)+f"({suffix_index})")
                    try:
                        Path(str(final_dir)+f"({suffix_index})").mkdir(exist_ok = False, parents = True)
                        logging.info(f"Folder renamed to: {copy_to}")
                    except:
                        raise PermissionError(copy_to)
                elif final_dir.is_dir():
                    path_and_size_dict_updater()
                    existing_size = sum(path_and_size_dict[str(final_dir.resolve())])
                    source_size = sum(key)
                    try:
                        existing_mtime = final_dir.stat().st_mtime
                    except:
                        logging.error(f"Directory: {final_dir} no longer exists")
                    try:
                        source_mtime = folder_path.stat().st_mtime
                    except:
                        logging.error(f"Directory: {folder_path} no longer exists")
                    if on_conflict == "larger":
                        if source_size >= existing_size:
                            folder_replace()
                        else:
                            no_change()
                            return
                    elif on_conflict == "smaller":
                        if source_size <= existing_size:
                            folder_replace()
                        else:
                            no_change()
                            return
                    elif on_conflict == "newer":
                        if source_mtime >= existing_mtime:
                            folder_replace()
                        else:
                            no_change()
                            return
                    elif on_conflict == "older":
                        if source_mtime <= existing_mtime:
                            folder_replace()
                        else:
                            no_change()
                            return
                    elif on_conflict == "rename":
                        if not dry_run:
                            if interactive and ask_user(f"Rename and store {folder_path}? [y/N]: ") != "y":
                                return
                            i = 1
                            new_name = f"{folder_path.name}({i})"
                            new_file = dest / new_name
                            while new_file.exists():
                                i += 1
                                new_name = f"{folder_path.name}({i})"
                                new_file = dest / new_name
                            #COPYPROCESS
                            rec_ops(folder_path, new_file, verbose, max_workers, mode)
                            path_and_size_dict_updater()
                        else:
                            logging.info(f"[DRY RUN] Rename: {folder_path} would have been renamed and stored")
                            
                    elif on_conflict == "skip":
                        if not dry_run:
                            logging.info(f"Skipped {folder_path} because of current on_conflict mode...")
                        else:
                            logging.info(f"[DRY RUN] Skip: Folder would have been skipped: {folder_path}")
                        return
                    elif on_conflict == "prompt":
                        if not dry_run:
                            response = ask_user(f"Replace {final_dir} with {folder_path}? [y/N]: ")
                            if response == "y":
                                #COPYPROCESS
                                rec_ops(folder_path, final_dir, verbose, max_workers, mode)
                                path_and_size_dict_updater()
                            else:
                                pass
                        else:
                            logging.info(f"[DRY RUN] Prompt: {folder_path} would have been prompted for action")
                    elif on_conflict == "replace":
                        folder_replace()
                    else:
                        logging.error(f"Unrecognized on_conflict mode supplied: {on_conflict}\nChoose from: {ON_CONFLICT_MODES}")
            
            else:
                logging.info(f"Non-existent: Path {final_dir} does not already exist")
                rec_ops(folder_path, final_dir, verbose, max_workers, mode)
                path_and_size_dict_updater()
        
        if key in existing_folder_fingerprints:
            logging.info(f"Potential matches: ({folder_path}) AND ({existing_folder_fingerprints[key]})")
            no_matches, clone_path = True, ""
            for potential_match in existing_folder_fingerprints[key]:
                escape = False
                for size in tuple(sorted(set(existing_folder_fingerprints))):
                    if size not in src_hash_key:
                        src_hash_key[size] = sequential_hash_compare(folder_path, size)
                    if sequential_hash_compare(potential_match, size) != src_hash_key[size]:
                        escape = True
                        break
                if escape:
                    continue
                if not escape:
                    clone_path = potential_match
                    no_matches = False
                    break
                        
            if no_matches:
                logging.info(f"No matches found for: {folder_path}")
                #try:
                folder_mechanism()
                #except Exception as e:
                #    logging.error(f"Error in folder_mechanism() for {folder_path}: {e}")
            else:
                logging.info(f"Skipped: {folder_path} as it matches existing {clone_path}")
                if mode == "move":
                    #backup_dir = src_path / "fylex.deprecated"
                    backup(src, folder_path, dry_run)
        else:
            logging.info(f"No matches: No possible matches found for ({folder_path})")
            #try:
            folder_mechanism()
            #except Exception as e:
            #    logging.error(f"Error in folder_mechanism() for {folder_path}: {e}")
                
        def delete_if_only_empty_dirs(path):
            path = Path(path)
            if not path.is_dir():
                return False
            if any(f for f in path.rglob("*") if f.is_file()):
                return False
            for sub in sorted(path.rglob("*"), key=lambda x: -len(x.parts)):
                if sub.is_dir():
                    try: sub.rmdir()
                    except: pass
            try:
                path.rmdir()
                return True
            except:
                return False
        if mode == "move":
            delete_if_only_empty_dirs(folder_path)

# -------- Main Folder copy --------
def copy_dirs(src, dest, no_create=False, interactive=False, dry_run=False, match_regex=None, match_names=None, match_glob=None,
               exclude_regex=None, exclude_names=None, exclude_glob=None, summary=None, on_conflict="rename", max_workers=4, 
               recursive_check=False, verbose=False):
    """Copies directories smartly into destination directory"""
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "copy_dirs"
    func_route.append(func_name)

    folderprocess(src, dest, "copy", no_create, interactive, dry_run, match_regex, match_names, match_glob,
               exclude_regex, exclude_names, exclude_glob, summary, on_conflict, max_workers, 
               recursive_check, verbose)
    
    log_copier(func_name, summary)

def move_dirs(src, dest, no_create=False, interactive=False, dry_run=False, match_regex=None, match_names=None, match_glob=None,
               exclude_regex=None, exclude_names=None, exclude_glob=None, summary=None, on_conflict="rename", max_workers=4, 
               recursive_check=False, verbose=False):
    """Moves directories smartly into destination directory"""
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "move_dirs"
    func_route.append(func_name)

    folderprocess(src, dest, "move", no_create, interactive, dry_run, match_regex, match_names, match_glob,
               exclude_regex, exclude_names, exclude_glob, summary, on_conflict, max_workers, 
               recursive_check, verbose)
    
    log_copier(func_name, summary)
    

# -------- Main Super Copy --------
def super_copy(src, dest, no_create=False, interactive=False, dry_run=False, folder_match_regex=None, folder_match_names=None, folder_match_glob=None,
               folder_exclude_regex=None, folder_exclude_names=None, folder_exclude_glob=None, file_match_regex=None, file_match_names=None, file_match_glob=None,
               file_exclude_regex=None, file_exclude_names=None, file_exclude_glob=None, summary=None, folder_on_conflict="rename", file_on_conflict="rename", max_workers=4, 
               file_recursive_check=False, folder_recursive_check=False, verbose=False, has_extension=False):
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "super_copy"
    func_route.append(func_name)
    copy_files(src, dest, no_create, interactive, dry_run, file_match_regex, file_match_names, file_match_glob,
                file_exclude_regex, file_exclude_names, file_exclude_glob, summary, file_on_conflict.lower(), max_workers, 
                verbose, file_recursive_check, has_extension)
    try:
        copy_dirs(src, dest, no_create, interactive, dry_run, folder_match_regex, folder_match_names, folder_match_glob,
                   folder_exclude_regex, folder_exclude_names, folder_exclude_glob, summary, folder_on_conflict, max_workers, 
                   folder_recursive_check, verbose)
    except Exception as e:
        logging.error(f"{e}")
    log_copier(func_name, summary)

# -------- Main Super Copy --------
def super_move(src, dest, no_create=False, interactive=False, dry_run=False, folder_match_regex=None, folder_match_names=None, folder_match_glob=None,
               folder_exclude_regex=None, folder_exclude_names=None, folder_exclude_glob=None, file_match_regex=None, file_match_names=None, file_match_glob=None,
               file_exclude_regex=None, file_exclude_names=None, file_exclude_glob=None, summary=None, folder_on_conflict="rename", file_on_conflict="rename", max_workers=4, 
               file_recursive_check=False, folder_recursive_check=False, verbose=False, has_extension=False):
    global func_route
    if not func_route:
        with open('fylex.log', 'w') as f:
            pass
    func_name = "super_move"
    func_route.append(func_name)
    move_files(src, dest, no_create, interactive, dry_run, file_match_regex, file_match_names, file_match_glob,
                file_exclude_regex, file_exclude_names, file_exclude_glob, summary, file_on_conflict.lower(), max_workers, 
                verbose, file_recursive_check, has_extension)
    try:
        move_dirs(src, dest, no_create, interactive, dry_run, folder_match_regex, folder_match_names, folder_match_glob,
               folder_exclude_regex, folder_exclude_names, folder_exclude_glob, summary, folder_on_conflict, max_workers, 
               folder_recursive_check, verbose)
    except Exception as e:    
        logging.error(f"{e}")
    log_copier(func_name, summary)

