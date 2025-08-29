import argparse
import sys
import json # Import json for parsing grouping argument
from .fylex import copy_files, move_files, delete_empty_dirs, spill, flatten, categorize, refine, copy_dirs, move_dirs, super_copy, super_move, ON_CONFLICT_MODES
from .exceptions import FylexError

def parse_args():
    parser = argparse.ArgumentParser(
        description="Fylex: A smart file utility tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # ---------------- Copy Subcommand ----------------
    copy_parser = subparsers.add_parser("copy_files", help="Smartly copy files using hashing and filters")

    copy_parser.add_argument("src", help="Source directory or file")
    copy_parser.add_argument("dest", help="Destination directory")
    copy_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    copy_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    copy_parser.add_argument("--dry-run", action="store_true", help="Dry run simulation")
    copy_parser.add_argument("--no-create", action="store_true", help="Don't create destination dirs if they don't exist")
    copy_parser.add_argument("--match-regex", default="", help="Regex to match filenames (e.g., '.*\\.txt$')")
    copy_parser.add_argument("--match-glob", default="", help="Glob to match filenames (e.g., '*.jpg')")
    copy_parser.add_argument("--match-names", nargs="+", default=[], help="List of exact filenames to match (space-separated)")
    copy_parser.add_argument("--exclude-regex", default=None, help="Regex to exclude filenames (e.g., '.*\\.tmp$')")
    copy_parser.add_argument("--exclude-glob", default=None, help="Glob to exclude filenames (e.g., '*.log')")
    copy_parser.add_argument("--exclude-names", nargs="+", default=[], help="List of filenames to exclude (space-separated)")
    copy_parser.add_argument("--on-conflict", choices=ON_CONFLICT_MODES, default="rename",
                             help="Action on filename conflict")
    copy_parser.add_argument("--summary", default=None, help="Path to copy the fylex.log summary file after operation")
    copy_parser.add_argument("--max-workers", type=int, default=4, help="Number of threads to use for concurrent operations")
    copy_parser.add_argument("--recursive-check", action="store_true", help="Scan source and destination subdirectories recursively for matching files")
    copy_parser.add_argument("--has-extension", action="store_true", help="Consider file extension in addition to size for duplicate checks (more precise)")

    # ---------------- Move Subcommand ----------------
    move_parser = subparsers.add_parser("move_files", help="Smartly move files using hashing and filters")

    move_parser.add_argument("src", help="Source directory or file")
    move_parser.add_argument("dest", help="Destination directory")
    move_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    move_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    move_parser.add_argument("--dry-run", action="store_true", help="Dry run simulation")
    move_parser.add_argument("--no-create", action="store_true", help="Don't create destination dirs if they don't exist")
    move_parser.add_argument("--match-regex", default="", help="Regex to match filenames (e.g., '.*\\.txt$')")
    move_parser.add_argument("--match-glob", default="", help="Glob to match filenames (e.g., '*.jpg')")
    move_parser.add_argument("--match-names", nargs="+", default=[], help="List of exact filenames to match (space-separated)")
    move_parser.add_argument("--exclude-regex", default=None, help="Regex to exclude filenames (e.g., '.*\\.tmp$')")
    move_parser.add_argument("--exclude-glob", default=None, help="Glob to exclude filenames (e.g., '*.log')")
    move_parser.add_argument("--exclude-names", nargs="+", default=[], help="List of filenames to exclude (space-separated)")
    move_parser.add_argument("--on-conflict", choices=ON_CONFLICT_MODES, default="rename",
                             help="Action on filename conflict")
    move_parser.add_argument("--summary", default=None, help="Path to copy the fylex.log summary file after operation")
    move_parser.add_argument("--max-workers", type=int, default=4, help="Number of threads to use for concurrent operations")
    move_parser.add_argument("--recursive-check", action="store_true", help="Scan source and destination subdirectories recursively for matching files")
    move_parser.add_argument("--has-extension", action="store_true", help="Consider file extension in addition to size for duplicate checks (more precise)")

    # ---------------- Refine Subcommand ----------------
    refine_parser = subparsers.add_parser("refine", help="Refine a directory (deduplicate files)")

    refine_parser.add_argument("target", help="Target directory to refine")
    refine_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode (prompt before deprecating each duplicate)")
    refine_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    refine_parser.add_argument("--dry-run", action="store_true", help="Dry run simulation")
    refine_parser.add_argument("--match-regex", default="", help="Regex to match filenames for refinement")
    refine_parser.add_argument("--match-glob", default="", help="Glob to match filenames for refinement")
    refine_parser.add_argument("--match-names", nargs="+", default=[], help="List of exact filenames to match for refinement")
    refine_parser.add_argument("--exclude-regex", default=None, help="Regex to exclude filenames from refinement")
    refine_parser.add_argument("--exclude-glob", default=None, help="Glob to exclude filenames from refinement")
    refine_parser.add_argument("--exclude-names", nargs="+", default=[], help="List of filenames to exclude from refinement")
    refine_parser.add_argument("--summary", default=None, help="Path to copy the fylex.log summary file after operation")
    refine_parser.add_argument("--max-workers", type=int, default=4, help="Number of threads to use for concurrent operations")
    refine_parser.add_argument("--recursive-check", action="store_true", help="Scan target directory and its subdirectories recursively for duplicates")

    # ---------------- Spill Subcommand ----------------
    spill_parser = subparsers.add_parser("spill", help="Spills files from subdirectories into the target parent directory")

    spill_parser.add_argument("target", help="Target directory to spill files into")
    spill_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    spill_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    spill_parser.add_argument("--dry-run", action="store_true", help="Dry run simulation")
    spill_parser.add_argument("--match-regex", default="", help="Regex to match filenames to spill")
    spill_parser.add_argument("--match-glob", default="", help="Glob to match filenames to spill")
    spill_parser.add_argument("--match-names", nargs="+", default=[], help="List of exact filenames to spill")
    spill_parser.add_argument("--exclude-regex", default=None, help="Regex to exclude filenames from spilling")
    spill_parser.add_argument("--exclude-glob", default=None, help="Glob to exclude filenames from spilling")
    spill_parser.add_argument("--exclude-names", nargs="+", default=[], help="List of filenames to exclude from spilling")
    spill_parser.add_argument("--on-conflict", choices=ON_CONFLICT_MODES, default="rename",
                             help="Action on filename conflict when spilling")
    spill_parser.add_argument("--summary", default=None, help="Path to copy the fylex.log summary file after operation")
    spill_parser.add_argument("--max-workers", type=int, default=4, help="Number of threads to use for concurrent operations")
    spill_parser.add_argument("--levels", type=int, default=-1, help="Max subdirectory depth to scan (-1 for infinite)")

    # ---------------- Flatten Subcommand ----------------
    flatten_parser = subparsers.add_parser("flatten", help="Flattens a directory structure by moving all files to the root and deleting empty subdirectories")

    flatten_parser.add_argument("target", help="Target directory to flatten")
    flatten_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    flatten_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    flatten_parser.add_argument("--dry-run", action="store_true", help="Dry run simulation")
    flatten_parser.add_argument("--on-conflict", choices=ON_CONFLICT_MODES, default="rename",
                             help="Action on filename conflict when flattening")
    flatten_parser.add_argument("--summary", default=None, help="Path to copy the fylex.log summary file after operation")
    flatten_parser.add_argument("--max-workers", type=int, default=4, help="Number of threads to use for concurrent operations")

    # ---------------- Categorize Subcommand ----------------
    categorize_parser = subparsers.add_parser("categorize", help="Categorizes files within a directory based on name, size, or extension")

    categorize_parser.add_argument("target", help="Target directory to categorize")
    categorize_parser.add_argument("categorize_by", choices=["name", "size", "ext"],
                                   help="Criteria for categorization: 'name', 'size', or 'ext'")
    categorize_parser.add_argument("--grouping", type=str, default="{}",
                                   help="Categorization rules as a JSON string (e.g., '{\"image_.*\": \"./images\", \"*.pdf\": \"./documents\"}'). See README for details.")
    categorize_parser.add_argument("--default", default=None,
                                   help="Default directory to move files that don't match any grouping rule")
    categorize_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    categorize_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    categorize_parser.add_argument("--dry-run", action="store_true", help="Dry run simulation")
    categorize_parser.add_argument("--summary", default=None, help="Path to copy the fylex.log summary file after operation")
    categorize_parser.add_argument("--max-workers", type=int, default=4, help="Number of threads to use for concurrent operations")

    # ---------------- Delete Empty Dirs Subcommand ----------------
    delete_empty_dirs_parser = subparsers.add_parser("delete_empty_dirs", help="Recursively delete empty subdirectories")
    delete_empty_dirs_parser.add_argument("target", help="Target directory to clean up empty subdirectories from")

    return parser.parse_args()

def main():
    args = parse_args()

    # Common arguments for all relevant commands
    # Use hasattr to safely get arguments as not all commands have all common arguments
    common_args = {
        "interactive": getattr(args, "interactive", False),
        "dry_run": getattr(args, "dry_run", False),
        "verbose": getattr(args, "verbose", False),
        "summary": getattr(args, "summary", None),
        "max_workers": getattr(args, "max_workers", 4),
    }

    try:
        # Validate dry-run and interactive conflict for commands that have both
        # This check is now generalized using `common_args`
        if common_args["dry_run"] and common_args["interactive"]:
            raise ValueError("Cannot use --dry-run with --interactive mode simultaneously.")

        if args.command == "copy_files":
            copy_files(
                src=args.src,
                dest=args.dest,
                no_create=args.no_create,
                match_regex=args.match_regex,
                match_names=args.match_names,
                match_glob=args.match_glob,
                exclude_regex=args.exclude_regex,
                exclude_names=args.exclude_names,
                exclude_glob=args.exclude_glob,
                on_conflict=args.on_conflict,
                recursive_check=args.recursive_check,
                has_extension=args.has_extension,
                **common_args
            )

        elif args.command == "move_files":
            move_files(
                src=args.src,
                dest=args.dest,
                no_create=args.no_create,
                match_regex=args.match_regex,
                match_names=args.match_names,
                match_glob=args.match_glob,
                exclude_regex=args.exclude_regex,
                exclude_names=args.exclude_names,
                exclude_glob=args.exclude_glob,
                on_conflict=args.on_conflict,
                recursive_check=args.recursive_check,
                has_extension=args.has_extension,
                **common_args
            )

        elif args.command == "refine":
            refine(
                target=args.target,
                match_regex=args.match_regex,
                match_names=args.match_names,
                match_glob=args.match_glob,
                exclude_regex=args.exclude_regex,
                exclude_names=args.exclude_names,
                exclude_glob=args.exclude_glob,
                recursive_check=args.recursive_check,
                **common_args
            )

        elif args.command == "spill":
            spill(
                target=args.target,
                on_conflict=args.on_conflict,
                match_regex=args.match_regex,
                match_glob=args.match_glob,
                match_names=args.match_names,
                exclude_regex=args.exclude_regex,
                exclude_glob=args.exclude_glob,
                exclude_names=args.exclude_names,
                levels=args.levels,
                **common_args
            )

        elif args.command == "flatten":
            flatten(
                target=args.target,
                on_conflict=args.on_conflict,
                **common_args
            )

        elif args.command == "categorize":
            grouping_data = {}
            if args.grouping != "{}": # Only parse if it's not the default empty dict string
                try:
                    grouping_data = json.loads(args.grouping)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON format for --grouping: {e}")

            # Note: `recursive_check` from CLI for `categorize` is only relevant for
            # `categorize_by_name` internally in fylex.py. The top-level `categorize`
            # function does not directly take `recursive_check` as a parameter.
            # Passing it via **common_args could cause an error if `categorize`'s
            # signature does not allow it.
            # Given the fylex.py code, `categorize` itself does NOT have `recursive_check`
            # in its signature. It's only relevant *inside* `categorize_by_name`.
            # To avoid an error, we should pass `recursive_check` as a named argument
            # only if the called categorize_by_* function supports it,
            # but this cli wraps all via `categorize`.
            # The safest approach is to conditionally add it to kwargs if `categorize_by` is 'name'.
            categorize_kwargs = {
                "target": args.target,
                "categorize_by": args.categorize_by,
                "grouping": grouping_data,
                "default": args.default,
                **common_args
            }
            if args.categorize_by == "name":
                categorize_kwargs["recursive_check"] = args.recursive_check

            categorize(**categorize_kwargs)


        elif args.command == "delete_empty_dirs":
            delete_empty_dirs(target=args.target) # This function does not use common_args

    except FylexError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Argument Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
