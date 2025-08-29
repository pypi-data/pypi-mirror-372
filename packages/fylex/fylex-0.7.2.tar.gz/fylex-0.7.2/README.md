
# Fylex: Your Intelligent File & Directory Orchestrator


[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![PyPI Downloads](https://static.pepy.tech/badge/fylex)](https://pepy.tech/projects/fylex)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Fylex is a powerful and flexible Python utility designed to simplify complex file management tasks. From intelligent copying and moving to flattening chaotic directory structures and resolving file conflicts, Fylex provides a robust, concurrent, and log-detailed solution for organizing your digital life.



## Table of Contents

1.  [Introduction](#introduction)
2.  [Key Features](#key-features)
3.  [Installation](#installation)
4.  [Usage](#usage)
    * [Core Functions Overview](#core-functions-overview)
    * [Common Parameters](#common-parameters)
    * [Conflict Resolution Modes (`on_conflict`)](#conflict-resolution-modes-on_conflict)
    * [Examples](#examples)
        * [`copy_files`: Smart file copying](#copy_files-smart-copying)
        * [`move_files`: Smart file moving](#move_files-smart-moving)
        * [`copy_dirs`: Smart folder copying](#copy_files-smart-copying)
        * [`move_dirs`: Smart folder moving](#move_files-smart-moving)
        * [`super_copy`: Smart unified copying](#copy_files-smart-copying)
        * [`super_move`: Smart unified moving](#move_files-smart-moving)
        * [`spill`: Consolidating Files from Subdirectories](#spill-consolidating-files-from-subdirectories)
        * [`flatten`: Flattening Directory Structures](#flatten-flattening-directory-structures)
        * [`categorize`: Categorizing files](#categorizing-files)
        * [`refine`: Refining directories](#refining-directories)
        * [Handling Junk Files](#handling-junk-files)
        * [Dry Run and Interactive Modes](#dry-run-and-interactive-modes)
        * [Working with Regex and Glob Patterns](#working-with-regex-and-glob-patterns)
        
5.  [Why Fylex is BETTER](#why-fylex-is-better)
6.  [Error Handling](#error-handling)
7.  [Logging](#logging)
8.  [Development & Contributing](#development--contributing)
9.  [License](#license)

## 1. Introduction

Managing files can quickly become a tedious and error-prone process, especially when dealing with large collections, duplicate files, or disorganized directory structures. Traditional command-line tools offer basic copy/move functionalities, but often lack the intelligence to handle conflicts, filter effectively, or automate complex reorganization patterns.

Fylex steps in to fill this gap. It's built on a foundation of robust error handling, concurrent processing, and intelligent decision-making, ensuring your file operations are efficient, safe, and tailored to your needs.

## 2. Key Features

* **Smart Copy (`copy_files`)**: Copy files with advanced filtering, conflict resolution, and integrity verification.
* **Smart Move (`move_files`)**: Move files, similar to copying, but with source file deletion upon successful transfer and verification.
* **Smart Directory Copy (`copy_dirs`)**: Copy entire directory structures with advanced filtering and intelligent conflict resolution, including content-based duplicate folder detection.
* **Smart Directory Move (`move_dirs`)**: Move directory structures, maintaining the same smart features as `copy_dirs`.
* **Unified Super Operations (`super_copy`, `super_move`)**: Perform both file and folder copy/move operations simultaneously, applying distinct filtering and conflict resolution rules for files and directories in a single command. This allows for powerful, combined management tasks.
* **File Hashing for Reliability**: Utilizes `xxhash` for fast, non-cryptographic hashing to ensure file integrity post-transfer and detect true content duplicates.
* **Sophisticated Conflict Resolution**: Offers a comprehensive set of strategies to handle name collisions at the destination (e.g., rename, replace, keep larger/smaller/newer/older, skip, or prompt).
* **Accident Prevention with Deprecated Folders**: Crucially, when an `on_conflict` mode leads to an existing destination file/folder being replaced (e.g., by a "newer" or "larger" incoming item), Fylex automatically moves the *superseded* item into a timestamped `.fylex_deprecated/` subfolder within the destination directory. This acts as a robust safety net against accidental data loss, allowing you to recover older versions if needed. Additionally, if a source file/folder is skipped because its identical counterpart already exists at the destination, it is also moved to `fylex.deprecated/` by default.
* **Flexible File and Folder Filtering**:
    * **Inclusion**: Specify files and/or folders to process using regular expressions (`match_regex`, `folder_match_regex`), exact names (`match_names`, `folder_match_names`), or glob patterns (`match_glob`, `folder_match_glob`).
    * **Exclusion**: Prevent specific files and/or folders from being processed using `exclude_regex`, `folder_exclude_regex`, `exclude_names`, `folder_exclude_names`, or `exclude_glob`, `folder_exclude_glob`.
    * **Junk File Awareness**: Predefined `JUNK_EXTENSIONS` helps easily exclude common temporary, system, and development artifacts.
* **Intelligent Duplicate Folder Detection**: Fylex identifies identical folders (based on their content structure and file hashes) to prevent redundant operations and optimize storage.
* **Directory Reorganization Utilities**:
    * **`spill`**: Consolidate files from nested subdirectories up to a specified depth into a parent directory.
    * **`flatten`**: Move all files from an entire directory tree into a single target directory, then automatically delete the empty subdirectories.
    * **`categorize`**: Organize files into logical subdirectories based on criteria like file name patterns (regex/glob), size ranges, or file extensions.
* **Concurrency for Speed**: Leverages Python's `ThreadPoolExecutor` to perform file and folder operations in parallel, significantly speeding up tasks involving many files.
* **Dry Run Mode**: Simulate any operation without making actual changes to the filesystem. Essential for verifying complex commands before execution.
* **Interactive Mode**: Prompts for user confirmation before each file or folder operation, providing fine-grained control.
* **Comprehensive Logging**: All actions, warnings, and errors are meticulously logged to `fylex.log` for easy auditing and debugging.
* **Robust Path Validation**: Prevents common pitfalls like attempting to copy a directory into itself, or operating on non-existent paths.
* **Retry Mechanism**: Failed file operations are retried up to `MAX_RETRIES` to handle transient network issues or temporary file locks.
* **Intelligent Duplicate Refinement**: Identifies true content duplicates using hashing and safely moves them to a deprecated folder, freeing up disk space.

## 3. Installation

Fylex is designed to be integrated into your Python projects or run as a standalone script.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Crystallinecore/fylex.git
    cd fylex
    ```
2.  **Install dependencies**:
    Fylex requires `xxhash`.
    ```bash
    pip install xxhash
    ```
3.  **Include in your project**:
    You can import Fylex functions directly into your Python scripts:
    ```python
    from fylex import copy_files, move_files, spill, flatten, delete_empty_dirs
    from fylex.exceptions import InvalidPathError, PermissionDeniedError
    ```

## 4. Usage

Fylex functions are designed to be intuitive. Here's a breakdown of the core functions and their parameters.

### Core Functions Overview

| Function | Type | Description |
| :--- | :--- | :--- |
| `copy_files(src, dest, **kwargs)` | `copy` | Copies files from `src` to `dest`. |
| `move_files(src, dest, **kwargs)` | `move` | Moves files from `src` to `dest`. |
| `copy_dirs(src, dest, **kwargs)` | `copy` | Copies directories and their contents from `src` to `dest`. |
| `move_dirs(src, dest, **kwargs)` | `move` | Moves directories and their contents from `src` to `dest`. |
| `super_copy(src, dest, **kwargs)` | `copy` | Copies both files and directories from `src` to `dest` with separate rules. |
| `super_move(src, dest, **kwargs)` | `move` | Moves both files and directories from `src` to `dest` with separate rules. |
| `spill(target, **kwargs)` | `reorganize` | Moves files from subdirectories within `target` to `target`. |
| `flatten(target, **kwargs)` | `reorganize` | Moves all files from subdirectories within `target` to `target` and deletes empty subdirectories. |
| `categorize(target, categorize_by, grouping=None, default=None, **kwargs)` | `organize` | Orchestrates categorization based on specified `categorize_by` mode. |
| `categorize_by_name(target, grouping, default=None, **kwargs)` | `organize` | Categorizes files by name using regex/glob patterns. |
| `categorize_by_size(target, grouping, default=None, **kwargs)` | `organize` | Categorizes files by size, using specific sizes or ranges. |
| `categorize_by_ext(target, default=None, **kwargs)` | `organize` | Categorizes files by their file extension. |
| `refine(target, **kwargs)` | `deduplicate` | Identifies and manages duplicate files within a target directory, moving redundant copies to a deprecated folder. |
| `delete_empty_dirs(target)` | `cleanup` | Recursively deletes all empty subdirectories within `target`. |



### Common Parameters


### Conflict Resolution Modes (`on_conflict`)

Fylex offers smart handling of file name conflicts at the destination. The `on_conflict` parameter accepts one of the following string values:

* **`"rename"` (Default)**: If a file with the same name exists, the incoming file will be renamed (e.g., `document.txt` becomes `document(1).txt`, `document(2).txt`, etc.) to avoid overwriting.
* **`"replace"`**: The incoming file will unconditionally overwrite the existing file at the destination. **The original file will be moved to a timestamped `.fylex_deprecated/` folder within the destination for safety.**
* **`"larger"`**: The file with the larger file size will be kept. If the existing file is larger or equal, the incoming file is skipped. **If skipped, the source file is moved to `fylex.deprecated/`**. If the incoming file is larger, it replaces the existing one, and the **original file is moved to `.fylex_deprecated/`**.
* **`"smaller"`**: The file with the smaller file size will be kept. If the existing file is smaller or equal, the incoming file is skipped. **If skipped, the source file is moved to `fylex.deprecated/`**. If the incoming file is smaller, it replaces the existing one, and the **original file is moved to `.fylex_deprecated/`**.
* **`"newer"`**: The file with the more recent modification timestamp will be kept. If the existing file is newer or has the same timestamp, the incoming file is skipped. **If skipped, the source file is moved to `fylex.deprecated/`**. If the incoming file is newer, it replaces the existing one, and the **original file is moved to `.fylex_deprecated/`**.
* **`"older"`**: The file with the older modification timestamp will be kept. If the existing file is older or has the same timestamp, the incoming file is skipped. **If skipped, the source file is moved to `fylex.deprecated/`**. If the incoming file is older, it replaces the existing one, and the **original file is moved to `.fylex_deprecated/`**.
* **`"skip"`**: The incoming file will be skipped entirely if a file with the same name exists at the destination. **The skipped source file is moved to `fylex.deprecated/` for review.**
* **`"prompt"`**: Fylex will ask the user interactively (via console) whether to replace the existing file or skip the incoming one. If "replace" is chosen, the **original file is moved to `.fylex_deprecated/`**. If "skip" is chosen, the **skipped source file is moved to `fylex.deprecated/`**.

### Examples

Let's assume the following directory structure for the examples:

````
/data/
├── project_A/
│  ├── main.py
│  ├── config.ini
│  └── docs/
│      ├── readme.md
│      └── images/
│          └── img_01.png
├── project_B/
│  ├── index.html
│  └── style.css
├── temp/
│  ├── .tmp
│  ├── old_data.bak
│  └── report.log
├── my_files/
│  ├── photo.jpg
│  ├── document.pdf
│  └── sub_folder/
│      └── nested_file.txt
├── important_notes.txt
└── large_archive.zip (assume large size, e.g., 50MB)
└── small_image.png (assume small size, e.g., 100KB)
└── duplicate_photo.jpg (exact same content as photo.jpg)

````

And your destination directory is initially empty: `/backup/`

##
#### `copy_files`: Smart Copying

`copy_files` Copies files from a source to a destination, with advanced conflict resolution and filtering options.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `src`            | **Required**   | Source path (directory or iterable of files). |
| `dest`           | **Required**   | Destination directory path. |
| `no_create`      | `False`        | If `True`, raises error if destination does not exist. |
| `interactive`    | `False`        | If `True`, prompts user before each copy. |
| `dry_run`        | `False`        | Simulates the copy without modifying files. |
| `match_regex`    | `None`         | Regex pattern to include matching files. |
| `match_names`    | `None`         | List of exact filenames to include. |
| `match_glob`     | `None`         | Glob pattern(s) to include. |
| `exclude_regex`  | `None`         | Regex pattern to exclude matching files. |
| `exclude_names`  | `None`         | List of exact filenames to exclude. |
| `exclude_glob`   | `None`         | Glob pattern(s) to exclude. |
| `summary`        | `None`         | Optional list to append summary messages. |
| `on_conflict`    | `"rename"`     | Strategy on conflict: `rename`, `skip`, `replace`, `newer`, `older`, `larger`, `smaller`, `prompt`. |
| `max_workers`    | `4`            | Number of threads for parallel operations. |
| `recursive_check`| `False`        | Recursively filter files in subdirectories. |
| `verbose`        | `False`        | If `True`, prints detailed log for each operation. |

#### Example:
```python
from fylex import copy_files

# Example 1: Copy all Python files from project_A to /backup, resolving conflicts by renaming.
# Only scans the top-level files of project_A if recursive_check=False
copy_files(src="/data/project_A", dest="/backup",
           match_glob="*.py", on_conflict="rename", verbose=True)
# Result: /backup/main.py

# Example 2: Copy all files from /data/my_files including subdirectories,
# excluding .txt files, and keep the newer version on conflict.
# If a file like 'photo.jpg' exists in /backup/my_backup and is older,
# the existing 'photo.jpg' would be moved to '/backup/my_backup/.fylex_deprecated/YYYY-MM-DD_HH-MM-SS/'
# before the new 'photo.jpg' is copied.
copy_files(src="/data/my_files", dest="/backup/my_backup",
           recursive_check=True, exclude_glob="*.txt", on_conflict="newer", verbose=True)
# Result: /backup/my_backup/photo.jpg, /backup/my_backup/document.pdf
# (nested_file.txt would be skipped due to exclusion)

# Example 3: Copy only 'important_notes.txt' from /data to /backup
copy_files(src="/data", dest="/backup",
           match_names=["important_notes.txt"], verbose=True)
# Result: /backup/important_notes.txt
````
##
#### `move_files`: Smart Moving

`move_files` works identically to `copy_files` but deletes the source file after successful transfer.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `src`            | **Required**   | Source path (directory or iterable of files). |
| `dest`           | **Required**   | Destination directory path. |
| `no_create`      | `False`        | If `True`, raises error if destination does not exist. |
| `interactive`    | `False`        | If `True`, prompts user before each copy. |
| `dry_run`        | `False`        | Simulates the copy without modifying files. |
| `match_regex`    | `None`         | Regex pattern to include matching files. |
| `match_names`    | `None`         | List of exact filenames to include. |
| `match_glob`     | `None`         | Glob pattern(s) to include. |
| `exclude_regex`  | `None`         | Regex pattern to exclude matching files. |
| `exclude_names`  | `None`         | List of exact filenames to exclude. |
| `exclude_glob`   | `None`         | Glob pattern(s) to exclude. |
| `summary`        | `None`         | Optional list to append summary messages. |
| `on_conflict`    | `"rename"`     | Strategy on conflict: `rename`, `skip`, `replace`, `newer`, `older`, `larger`, `smaller`, `prompt`. |
| `max_workers`    | `4`            | Number of threads for parallel operations. |
| `recursive_check`| `False`        | Recursively filter files in subdirectories. |
| `verbose`        | `False`        | If `True`, prints detailed log for each operation. |

#### Example
```python
from fylex import move_files

# Example: Move all .html and .css files from project_B to /web_files,
# prompting on conflict.
# If the user chooses to replace, the existing file in /web_files would be moved
# to '/web_files/.fylex_deprecated/YYYY-MM-DD_HH-MM-SS/'.
# If the user chooses to skip, the source file (e.g., /data/project_B/index.html)
# would be moved to 'fylex.deprecated/' (in the current working directory).
move_files(src="/data/project_B", dest="/web_files",
           match_glob="*.{html,css}", on_conflict="prompt", interactive=True, verbose=True)
# User would be prompted for each file if it already exists in /web_files.
# After successful move: /data/project_B will no longer contain index.html or style.css
```
##

#### `copy_dirs`: Smart Directory Copying

`copy_dirs` allows you to copy entire directory structures with advanced filtering and conflict resolution, including content-based duplicate folder detection.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `src`            | **Required**   | Source directory path. |
| `dest`           | **Required**   | Target directory path. |
| `no_create`      | `False`        | Raise error if destination doesn't exist. |
| `interactive`    | `False`        | Prompt user before copying each folder or file. |
| `dry_run`        | `False`        | Simulate the directory copy without changes. |
| `match_regex`    | `None`         | Include files matching regex pattern. |
| `match_names`    | `None`         | Include files with specific names. |
| `match_glob`     | `None`         | Include files matching glob pattern. |
| `exclude_regex`  | `None`         | Exclude files matching regex. |
| `exclude_names`  | `None`         | Exclude files with specific names. |
| `exclude_glob`   | `None`         | Exclude files matching glob pattern. |
| `summary`        | `None`         | Store summary/logging messages. |
| `on_conflict`    | `"rename"`     | Strategy for existing files or directories. |
| `max_workers`    | `4`            | Number of worker threads. |
| `recursive_check`| `False`        | Recursively apply filters during directory traversal. |
| `verbose`        | `False`        | Enable detailed output. |

#### Example
```python
from fylex import copy_dirs

# Example: Copy a specific project folder from a development drive to a backup drive.
# If 'my_project' already exists in '/backups', Fylex will keep the newer version.
# If the existing folder in '/backups' is older, it will be moved to
# '/backups/.fylex_deprecated/YYYY-MM-DD_HH-MM-SS/my_project/' before the new one is copied.
copy_dirs(src="/dev_drive/projects", dest="/backups",
          folder_match_names=["my_project"], on_conflict="newer", verbose=True)
# If '/backups/my_project' was older than '/dev_drive/projects/my_project',
# the old '/backups/my_project' is deprecated, and the new one is copied.

# Example: Copy all folders related to 'docs' or 'reports', excluding sensitive ones,
# and use dry_run to see what would happen.
copy_dirs(src="/shared_drive/department_data", dest="/archive/department_docs",
          folder_match_regex="^(docs|reports)_.*",
          folder_exclude_names=["docs_sensitive", "reports_internal_only"],
          dry_run=True, verbose=True)
# This command will only print logs about which directories *would* be copied and where.
```
##
#### `move_dirs`: Smart Directory Moving

`move_dirs` works identically to `copy_dirs` but deletes the source directory after successful transfer and verification.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `src`            | **Required**   | Source directory path. |
| `dest`           | **Required**   | Target directory path. |
| `no_create`      | `False`        | Raise error if destination doesn't exist. |
| `interactive`    | `False`        | Prompt user before copying each folder or file. |
| `dry_run`        | `False`        | Simulate the directory copy without changes. |
| `match_regex`    | `None`         | Include files matching regex pattern. |
| `match_names`    | `None`         | Include files with specific names. |
| `match_glob`     | `None`         | Include files matching glob pattern. |
| `exclude_regex`  | `None`         | Exclude files matching regex. |
| `exclude_names`  | `None`         | Exclude files with specific names. |
| `exclude_glob`   | `None`         | Exclude files matching glob pattern. |
| `summary`        | `None`         | Store summary/logging messages. |
| `on_conflict`    | `"rename"`     | Strategy for existing files or directories. |
| `max_workers`    | `4`            | Number of worker threads. |
| `recursive_check`| `False`        | Recursively apply filters during directory traversal. |
| `verbose`        | `False`        | Enable detailed output. |

#### Example
```python
from fylex import move_dirs

# Example: Move a completed project folder from "in progress" to "completed" archives.
# If a folder with the same name exists in '/archive/completed_projects',
# the larger one will be kept. If the incoming folder is smaller or equal,
# the source folder will be moved to 'fylex.deprecated/'.
move_dirs(src="/project_workspace/in_progress", dest="/archive/completed_projects",
          folder_match_names=["ProjectX_Final"], on_conflict="larger", verbose=True)
# If '/archive/completed_projects/ProjectX_Final' was smaller than or equal to
# '/project_workspace/in_progress/ProjectX_Final', the source folder
# '/project_workspace/in_progress/ProjectX_Final' would be moved to 'fylex.deprecated/'.
# Otherwise, the existing one in '/archive/completed_projects' would be deprecated,
# and the source would be moved.
```
##
#### `super_copy`: Unified Smart Copy (Files and Directories)

`super_copy` allows you to copy both files and directories simultaneously from a source to a destination, applying distinct filtering and conflict resolution rules for each.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `src`            | **Required**   | Source path (file or directory). |
| `dest`           | **Required**   | Target path. |
| `no_create`      | `False`        | Raise error if destination doesn't exist. |
| `interactive`    | `False`        | Prompt before copying. |
| `dry_run`        | `False`        | Run in preview-only mode. |
| `file_match_regex`    | `None`         | File inclusion pattern. |
| `file_match_names`    | `None`         | Files to include by name. |
| `file_match_glob`     | `None`         | Files to include using glob. |
| `folder_match_regex`    | `None`         | Folder inclusion pattern. |
| `folder_match_names`    | `None`         | Folders to include by name. |
| `folder_match_glob`     | `None`         | Folders to include using glob. |
| `file_exclude_regex`  | `None`         | File exclusion regex. |
| `file_exclude_names`  | `None`         | Files to exclude by name. |
| `file_exclude_glob`   | `None`         | Files to exclude using glob. |
| `folder_exclude_regex`  | `None`         | Folder exclusion regex. |
| `folder_exclude_names`  | `None`         | Folders to exclude by name. |
| `folder_exclude_glob`   | `None`         | Folders to exclude using glob. |
| `summary`        | `None`         | Collects operation summaries. |
| `file_on_conflict`    | `"rename"`     | How to resolve naming conflicts for files. |
| `folder_on_conflict`    | `"rename"`     | How to resolve naming conflicts for folders. |
| `max_workers`    | `4`            | Parallel thread pool size. |
| `recursive_check`| `False`        | Traverse and filter recursively. |
| `verbose`        | `False`        | Enable verbose mode. |

#### Example
```python
from fylex import super_copy

# Example: Copy a mixed-content project folder to a backup.
# Copy all .py files, and specific 'config' and 'data' folders.
# For files, rename on conflict. For folders, replace if newer.
super_copy(src="/my_dev_project", dest="/backup_dev",
           file_match_glob="*.py", file_on_conflict="rename",
           folder_match_names=["config", "data"], folder_on_conflict="newer",
           file_recursive_check=True, folder_recursive_check=True, verbose=True)
# This will copy all .py files found recursively within /my_dev_project,
# renaming them if they conflict in /backup_dev.
# It will also copy 'config' and 'data' subfolders, recursively, replacing them
# in /backup_dev if the source version is newer (deprecating the old one).

# Example: Copy an entire repository structure, excluding certain files and hidden directories.
super_copy(src="/my_repo", dest="/clean_archive",
           file_exclude_glob="*.log",
           folder_exclude_regex="^\.", # Exclude hidden folders like .git, .vscode etc.
           file_on_conflict="skip",
           folder_on_conflict="skip",
           recursive_check=True, # Apply file filtering recursively
           folder_recursive_check=True, # Apply folder filtering recursively
           dry_run=True, verbose=True)
# This dry run will show which files (excluding .log) and which folders (excluding hidden ones)
# would be copied, skipping any conflicts.
```
##
#### `super_move`: Unified Smart Move (Files and Directories)

`super_move` works identically to `super_copy` but deletes the source files and directories upon successful transfer and verification.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `src`            | **Required**   | Source path (file or directory). |
| `dest`           | **Required**   | Target path. |
| `no_create`      | `False`        | Raise error if destination doesn't exist. |
| `interactive`    | `False`        | Prompt before copying. |
| `dry_run`        | `False`        | Run in preview-only mode. |
| `file_match_regex`    | `None`         | File inclusion pattern. |
| `file_match_names`    | `None`         | Files to include by name. |
| `file_match_glob`     | `None`         | Files to include using glob. |
| `folder_match_regex`    | `None`         | Folder inclusion pattern. |
| `folder_match_names`    | `None`         | Folders to include by name. |
| `folder_match_glob`     | `None`         | Folders to include using glob. |
| `file_exclude_regex`  | `None`         | File exclusion regex. |
| `file_exclude_names`  | `None`         | Files to exclude by name. |
| `file_exclude_glob`   | `None`         | Files to exclude using glob. |
| `folder_exclude_regex`  | `None`         | Folder exclusion regex. |
| `folder_exclude_names`  | `None`         | Folders to exclude by name. |
| `folder_exclude_glob`   | `None`         | Folders to exclude using glob. |
| `summary`        | `None`         | Collects operation summaries. |
| `file_on_conflict`    | `"rename"`     | How to resolve naming conflicts for files. |
| `folder_on_conflict`    | `"rename"`     | How to resolve naming conflicts for folders. |
| `max_workers`    | `4`            | Parallel thread pool size. |
| `recursive_check`| `False`        | Traverse and filter recursively. |
| `verbose`        | `False`        | Enable verbose mode. |

#### Example
```python
from fylex import super_move

# Example: Migrate a project from a staging area to production.
# Move all image files (.jpg, .png) and a specific 'assets' folder.
# Images that conflict will keep the larger version.
# The 'assets' folder will be replaced if the incoming one is newer.
super_move(src="/staging/prod_build", dest="/production/app_data",
           file_match_glob="*.{jpg,png}", file_on_conflict="larger",
           folder_match_names=["assets"], folder_on_conflict="newer",
           file_recursive_check=True, folder_recursive_check=True, verbose=True)
# This will move all specified image files, keeping the larger version on conflict.
# It will move the 'assets' folder, replacing the destination if newer (deprecating the old one).
# Source files and folders will be deleted after successful move.
```

##
#### `spill`: Consolidating Files from Subdirectories

`spill` moves files from nested directories into the `target` root directory.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `target`         | **Required**   | Target directory to refine. |
| `interactive`    | `False`        | Prompts user before moving duplicate files. |
| `dry_run`        | `False`        | Simulates changes without actual deletion or move. |
| `match_regex`    | `None`         | Include files matching regex. |
| `match_names`    | `None`         | Include specific filenames. |
| `match_glob`     | `None`         | Include files by glob pattern. |
| `exclude_regex`  | `None`         | Exclude files by regex. |
| `exclude_names`  | `None`         | Exclude specific filenames. |
| `exclude_glob`   | `None`         | Exclude files using glob pattern. |
| `summary`        | `None`         | Optional log collector list. |
| `on_conflict`    | `"rename"`     | Conflict resolution strategy. |
| `max_workers`    | `4`            | Threads for parallel hashing. |
| `recursive_check`| `False`        | Traverse and check all subfolders. |
| `verbose`        | `False`        | Print each step for transparency. |

#### Example
```python
from fylex import spill
import os
import shutil

# Setup for spill example:
os.makedirs("/data/temp_spill/level1/level2", exist_ok=True)
with open("/data/temp_spill/fileA.txt", "w") as f: f.write("A")
with open("/data/temp_spill/level1/fileB.txt", "w") as f: f.write("B")
with open("/data/temp_spill/level1/level2/fileC.txt", "w") as f: f.write("C")
with open("/data/temp_spill/level1/level2/image.jpg", "w") as f: f.write("C")

# Example 1: Spill all files from subdirectories (infinite levels) into /data/temp_spill.
# If fileB.txt already existed in /data/temp_spill, it would be deprecated based on conflict mode.
spill(target="/data/temp_spill", levels=-1, verbose=True)
# Result: /data/temp_spill/fileA.txt, /data/temp_spill/fileB.txt, /data/temp_spill/fileC.txt, /data/temp_spill/image.jpg
# (fileA.txt is already at root, so not moved)
# The empty subdirectories /data/temp_spill/level1 and /data/temp_spill/level1/level2 will remain.

# Clean up for next example:
shutil.rmtree("/data/temp_spill")
os.makedirs("/data/temp_spill/level1/level2", exist_ok=True)
with open("/data/temp_spill/fileA.txt", "w") as f: f.write("A")
with open("/data/temp_spill/level1/fileB.txt", "w") as f: f.write("B")
with open("/data/temp_spill/level1/level2/fileC.txt", "w") as f: f.write("C")

# Example 2: Spill only files from immediate subdirectories (level 1), excluding .txt files.
spill(target="/data/temp_spill", levels=1, exclude_glob="*.txt", verbose=True)
# Result: Only files from /data/temp_spill/level1 (like fileB.txt if not excluded) would be considered.
# In this specific setup, since only .txt files are present, nothing would move.
# If image.jpg was in level1, it would move.
```

##
#### `flatten`: Flattening Directory Structures

`flatten` is ideal for taking a messy, deeply nested folder and putting all its files into one level, then cleaning up the empty folders.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `target`         | **Required**   | Directory whose files are to be categorized. |
| `categorize_by`  | **Required**   | Mode: `"name"`, `"size"`, or `"ext"`. |
| `grouping`       | `None`         | Mapping of patterns to folder paths. |
| `default`        | `None`         | Path to move unmatched files. |
| `interactive`    | `False`        | Prompts before each categorization. |
| `dry_run`        | `False`        | Preview the changes without modifying anything. |
| `summary`        | `None`         | Collect log summary here. |
| `max_workers`    | `4`            | Number of threads used for sorting. |
| `verbose`        | `False`        | Show per-file operations and logs. |
| `recursive_check`| `False`        | Include subdirectories in file selection. |

#### Example
```python
from fylex import flatten
import os
import shutil

# Setup for flatten example (same as spill setup):
os.makedirs("/data/temp_flatten/level1/level2", exist_ok=True)
with open("/data/temp_flatten/fileX.log", "w") as f: f.write("X") # Will be ignored by default junk filter
with open("/data/temp_flatten/level1/fileY.jpg", "w") as f: f.write("Y")
with open("/data/temp_flatten/level1/level2/fileZ.pdf", "w") as f: f.write("Z")

# Example: Flatten the entire /data/temp_flatten directory.
# Any files in subdirectories that would overwrite an existing file in /data/temp_flatten
# would first cause the existing file to be moved to '/data/temp_flatten/.fylex_deprecated/'.
flatten(target="/data/temp_flatten", verbose=True)
# Result: /data/temp_flatten/fileX.log, /data/temp_flatten/fileY.jpg, /data/temp_flatten/fileZ.pdf
# After operation, /data/temp_flatten/level1/ and /data/temp_flatten/level1/level2/ will be deleted.
```
##
#### Categorizing Files

Fylex offers flexible ways to categorize files into new or existing directories.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `target`         | **Required**   | Directory whose files are to be categorized. |
| `categorize_by`  | **Required**   | Mode: `"name"`, `"size"`, or `"ext"`. |
| `grouping`       | `None`         | Mapping of patterns to folder paths. |
| `default`        | `None`         | Path to move unmatched files. |
| `interactive`    | `False`        | Prompts before each categorization. |
| `dry_run`        | `False`        | Preview the changes without modifying anything. |
| `summary`        | `None`         | Collect log summary here. |
| `max_workers`    | `4`            | Number of threads used for sorting. |
| `verbose`        | `False`        | Show per-file operations and logs. |
| `recursive_check`| `False`        | Include subdirectories in file selection. |

#### Example
```python
from fylex import categorize
import os

# Create dummy files for categorization
os.makedirs("/data/categorize_source", exist_ok=True)
with open("/data/categorize_source/report_april.pdf", "w") as f: f.write("report content")
with open("/data/categorize_source/meeting_notes.txt", "w") as f: f.write("notes content")
with open("/data/categorize_source/photo_2023.jpg", "w") as f: f.write("photo content")
with open("/data/categorize_source/large_video.mp4", "w") as f: f.write("large content" * 1000000) # ~1MB
with open("/data/categorize_source/small_doc.docx", "w") as f: f.write("small content") # ~100 bytes

# Example 1: Categorize by file extension
categorize(
    target="/data/categorize_source",
    categorize_by="ext",
    default="/data/categorize_destination/misc", # Files without common extensions or uncategorized
    dry_run=True,
    verbose=True
)
# Expected Dry Run Output:
# Would move /data/categorize_source/report_april.pdf to /data/categorize_destination/pdf/report_april.pdf
# Would move /data/categorize_source/meeting_notes.txt to /data/categorize_destination/txt/meeting_notes.txt
# etc.

# Example 2: Categorize by file name using regex and glob
grouping_by_name = {
    r"^report_.*\.pdf$": "/data/categorize_destination/Reports", # Regex for reports
    ("photo_*.jpg", "glob"): "/data/categorize_destination/Images" # Glob for photos
}
categorize(
    target="/data/categorize_source",
    categorize_by="name",
    grouping=grouping_by_name,
    default="/data/categorize_destination/Other",
    dry_run=True,
    verbose=True
)
# Expected Dry Run Output:
# Would move /data/categorize_source/report_april.pdf to /data/categorize_destination/Reports/report_april.pdf
# Would move /data/categorize_source/photo_2023.jpg to /data/categorize_destination/Images/photo_2023.jpg
# Others would go to /data/categorize_destination/Other

# Example 3: Categorize by file size (ranges in bytes)
grouping_by_size = {
    (0, 1024): "/data/categorize_destination/SmallFiles", # 0 to 1KB
    (1024 * 1024, "max"): "/data/categorize_destination/LargeFiles" # 1MB and above
}
categorize(
    target="/data/categorize_source",
    categorize_by="size",
    grouping=grouping_by_size,
    default="/data/categorize_destination/MediumFiles",
    dry_run=True,
    verbose=True
)
# Expected Dry Run Output:
# Would move /data/categorize_source/small_doc.docx to /data/categorize_destination/SmallFiles/small_doc.docx
# Would move /data/categorize_source/large_video.mp4 to /data/categorize_destination/LargeFiles/large_video.mp4
# Other files would go to /data/categorize_destination/MediumFiles
```
##
#### Refining Directories (Deduplicating)

`refine` identifies and safely handles duplicate files based on their content.

| Parameter        | Default        | Description |
|------------------|----------------|-------------|
| `target`         | **Required**   | Target directory to refine. |
| `interactive`    | `False`        | Prompts user before moving duplicate files. |
| `dry_run`        | `False`        | Simulates changes without actual deletion or move. |
| `match_regex`    | `None`         | Include files matching regex. |
| `match_names`    | `None`         | Include specific filenames. |
| `match_glob`     | `None`         | Include files by glob pattern. |
| `exclude_regex`  | `None`         | Exclude files by regex. |
| `exclude_names`  | `None`         | Exclude specific filenames. |
| `exclude_glob`   | `None`         | Exclude files using glob pattern. |
| `summary`        | `None`         | Optional log collector list. |
| `on_conflict`    | `"rename"`     | Conflict resolution strategy. |
| `max_workers`    | `4`            | Threads for parallel hashing. |
| `recursive_check`| `False`        | Traverse and check all subfolders. |
| `verbose`        | `False`        | Print each step for transparency. |

#### Example
```python
from fylex import refine
import os
import shutil
import hashlib

# Setup for refine example
os.makedirs("/data/refine_test", exist_ok=True)
with open("/data/refine_test/file1.txt", "w") as f: f.write("unique content A")
with open("/data/refine_test/file2_copy.txt", "w") as f: f.write("unique content A") # Duplicate of file1.txt
with open("/data/refine_test/image.jpg", "w") as f: f.write("image data")
os.makedirs("/data/refine_test/sub_folder", exist_ok=True)
with open("/data/refine_test/sub_folder/file1_in_sub.txt", "w") as f: f.write("unique content A") # Duplicate of file1.txt

# Example 1: Find and deprecate duplicates in /data/refine_test (dry run)
refine(
    target="/data/refine_test",
    recursive_check=True, # Check subdirectories
    dry_run=True,
    verbose=True
)
# Expected Dry Run Output:
# [DRY RUN] Duplicate: /data/refine_test/file2_copy.txt would have been safely backed up at /data/refine_test/fylex.deprecated
# [DRY RUN] Duplicate: /data/refine_test/sub_folder/file1_in_sub.txt would have been safely backed up at /data/refine_test/fylex.deprecated
# File retained: /data/refine_test/file1.txt
# File retained: /data/refine_test/image.jpg

# Example 2: Actual deduplication (remove dry_run=True to execute)
# This would create /data/refine_test/.fylex_deprecated/ and move duplicates into it.
# refine(
#     target="/data/refine_test",
#     recursive_check=True,
#     verbose=True
# )
```

##
#### Handling Junk Files

Fylex comes with a predefined list of common "junk" file extensions and names. You can leverage this via the `exclude_names` and `exclude_glob` parameters or modify the `JUNK_EXTENSIONS` dictionary in the source.

```python
from fylex import copy_files, JUNK_EXTENSIONS

# Combine all junk extensions and names into lists for exclusion
all_junk_extensions = [ext for sublist in JUNK_EXTENSIONS.values() for ext in sublist if ext.startswith(".")]
all_junk_names = [name for sublist in JUNK_EXTENSIONS.values() for name in sublist if not name.startswith(".")]

# Example: Copy all files from /data/temp to /archive, excluding all known junk.
# Note: You'd typically want to specify target directory for JUNK_EXTENSIONS if using.
# For simplicity, let's use common examples.
copy_files(src="/data/temp", dest="/archive",
           exclude_glob="*.tmp", # Exclude temporary files
           exclude_names=["thumbs.db", "desktop.ini"], # Exclude specific names
           recursive_check=True, verbose=True)
# Result: .tmp, old_data.bak, report.log would be excluded based on these specific exclusions.
```
##
#### Dry Run and Interactive Modes

```python
from fylex import copy_files

# Example: See what would happen if you were to copy all .txt files without actually doing it.
copy_files(src="/data/project_A", dest="/backup",
           match_glob="*.md", dry_run=True, verbose=True)
# Output in log/console: "[DRY RUN] Would have copied: /data/project_A/docs/readme.md -> /backup/readme.md"
# No files are actually copied.

# Example: Be prompted for every action
copy_files(src="/data/project_A", dest="/backup",
           match_glob="*.ini", interactive=True, verbose=True)
# Console: "Copy /data/project_A/config.ini to /backup/config.ini? [y/N]:"
# User input determines if the copy proceeds.
```
##
#### Working with Regex and Glob Patterns

Fylex allows you to combine regex and glob patterns for precise filtering.

```python
from fylex import copy_files

# Example 1: Copy files that are either .jpg OR start with 'report'
copy_files(src="/data/my_files", dest="/backup",
           match_regex=r".*\.jpg$", # Matches any .jpg
           match_glob="report*", # Matches files starting with 'report'
           verbose=True)

# Example 2: Exclude files that are either log files or contain 'temp' in their name
copy_files(src="/data/", dest="/filtered_data",
           recursive_check=True,
           exclude_regex=r".*\.log$",
           exclude_glob="*temp*", # Matches files containing 'temp'
           verbose=True)
```


## 5\. Why Fylex is Superior

Compared to standard shell commands (`cp`, `mv`, `rm`, `find`, `robocopy` / `rsync`) or even basic scripting, Fylex offers significant advantages:

1.  **Intelligent Conflict Resolution (Beyond Overwrite/Rename) *with Accident Prevention***:

      * **Shell**: `cp -f` overwrites, `cp -n` skips. `robocopy` offers more, but still lacks integrated safe-guards.
      * **Fylex**: Provides `rename`, `replace`, `larger`, `smaller`, `newer`, `older`, `skip`, and `prompt`. **Crucially, when Fylex replaces an existing file at the destination or skips a source file (due to a conflict), it first moves the affected file into a dedicated, timestamped `.fylex_deprecated/` folder.** This virtually eliminates the risk of accidental data loss, allowing users to review and retrieve superseded or skipped files later. This safety net is a major leap beyond simple overwrite/skip options in other tools.

2.  **Built-in Data Integrity Verification (Hashing):**

      * OS commands perform a basic copy. You'd need to manually run `md5sum` or `sha256sum` after the copy and compare.
      * `Fylex` uses `xxhash` for fast post-copy verification, ensuring that the copied file is an exact, uncorrupted duplicate of the source. This is crucial for critical data.

3.  **Unified and Advanced Filtering:**

      * `find` combined with `grep`, `xargs`, and `egrep` is powerful but often requires complex, multi-stage commands. Glob patterns are simpler but less flexible than regex.
      * `Fylex` integrates regex, glob, and exact name matching/exclusion directly into its functions, allowing for highly specific and readable filtering with a single API call.

4.  **Specialized Directory Reorganization (`spill`, `flatten`):**

      * Achieving "spill","flatten" or "categorize" with OS commands means chaining `find`, `mv`, `rmdir`, and potentially `xargs` with very specific and often platform-dependent syntax. This is notoriously difficult to get right and can lead to accidental data loss if a mistake is made.
      * `Fylex` provides these as high-level, single-function operations with built-in safety (like dry run and empty directory cleanup), making them much safer and easier to use.

5.  **Intelligent Duplicate Management (`refine`):**

      * Dedicated deduplication tools like `fdupes` exist but often perform direct deletion or require additional scripting for safe archiving.
      * `Fylex`'s `refine` function provides content-based duplicate detection using `xxhash` and, most importantly, safely moves duplicates to a `.fylex_deprecated/` folder, offering a non-destructive alternative to immediate deletion.

6.  **Concurrency Out-of-the-Box:**

      * Basic OS commands are single-threaded. Parallelization requires advanced shell scripting with `xargs -P` or similar, which adds complexity.
      * `Fylex` automatically utilizes a `ThreadPoolExecutor` to process files concurrently, significantly boosting performance for large datasets without any extra effort from the user.

7.  **Comprehensive Logging & Dry Run Safety Net:**

      * OS commands typically dump output to stdout/stderr. Comprehensive logging requires redirection and parsing. Dry run is often simulated or requires specific flags that may not exist for all commands.
      * `Fylex` generates detailed `fylex.log` for every operation, providing an auditable trail. The `dry_run` mode is a built-in safeguard, allowing you to preview complex operations safely.

8.  **Python Integration & Extensibility:**

      * While powerful, shell scripts can be less maintainable and harder to integrate into larger software systems.
      * `Fylex`, being a Python library, is easily callable from any Python application, making it highly extensible and automatable within existing Python workflows.

9.  **User Interactivity:**

      * Shell: Limited options for user prompts during bulk operations.
      * `Fylex`: `interactive` mode provides a safety net by prompting for confirmation before each file transfer, giving you granular control.

In essence, Fylex transforms common, complex, and risky file management scenarios into straightforward, reliable, and efficient operations, saving time, preventing data loss, and simplifying automation.

## 6\. Error Handling

Fylex implements robust error handling to ensure operations are performed safely and to provide clear feedback when issues arise.

  * `InvalidPathError`: Raised if a specified source path does not exist, or if `no_create` is `True` and the destination path does not exist.
  * `PermissionDeniedError`: Raised if Fylex lacks the necessary read or write permissions for a given path.
  * `ValueError`: Raised for logical inconsistencies, such as trying to copy a directory into itself when `recursive_check` is enabled, or unsupported categorization modes.
  * **Retry Mechanism**: Transient errors during file copy/move operations are automatically retried up to `MAX_RETRIES` (default: 5). If retries are exhausted, an error is logged.

## 7\. Logging

Fylex provides detailed logging to `fylex.log` in the current working directory by default.

  * **INFO**: Records successful operations, dry run simulations, and significant events, including deprecation actions.
  * **WARNING**: Indicates potential issues, such as hash mismatches requiring retries.
  * **ERROR**: Logs failures, permissions issues, or unhandled exceptions.

You can control log output:

  * `verbose=True`: Prints log messages to the console in real-time, in addition to the file.
  * `summary="path/to/my_log.log"`: Copies the `fylex.log` file to the specified summary path upon completion.

## 8\. Development & Contributing

Fylex is open to contributions\! If you have ideas for new features, bug fixes, or improvements, feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Write clear commit messages.
5.  Submit a Pull Request.

## 9\. License

Fylex is released under the [MIT License](https://www.google.com/search?q=LICENSE)

xxHash used under BSD License
##

## 10\. Author

**Sivaprasad Murali** —
[sivaprasad.off@gmail.com](mailto:sivaprasad.off@gmail.com)


##
<center>Your files. Your rules. Just smarter.</center>

## 


