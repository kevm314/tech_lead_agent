from urllib.parse import urlparse
from typing import List, Optional
from pathlib import Path

generic_ignored_extensions = [
    '.json',
    '.md',
    '.gitignore',
    '.svg',
    '.ico',
    '.png',
    '.editorconfig',
    '.flake8',
    '.yaml',
    '.toml',
    '.idx',
    '.pack',
    '',
    'lock'
]


def list_files(directory: str, ignore_extensions=None) -> List[Path]:
    """
    Lists all files in a specified directory and its subdirectories,
    ignoring files with specified extensions.

    Parameters:
    directory (str): The directory to search.
    ignore_extensions (List[str], optional): A list of file extensions to ignore.
        Defaults to generic list stored in this file

    Returns:
    List[Path]: A list of Path objects representing the filtered files.
    """
    if ignore_extensions is None:
        ignore_extensions = generic_ignored_extensions

    # Convert extensions to lowercase for case-insensitive comparison
    ignore_extensions = [ext.lower() for ext in ignore_extensions]
    # Get a list of all files in the specified directory and its subdirectories
    all_files = Path(directory).rglob('*')
    # Filter out the undesired file extensions
    filtered_files = [
        f for f in all_files
        if f.is_file()
        and f.suffix.lower() not in ignore_extensions
        and '.git' not in f.parts
    ]

    return filtered_files


def extract_repo_name(url: str) -> str:
    """
    Extracts the repository name from a GitHub URL.

    Parameters:
    url (str): The GitHub URL from which to extract the repository name.

    Returns:
    str: The repository name extracted from the URL, or None if an error occurs.
    """
    try:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2:
            repo_name_with_extension = path_parts[-1]
            repo_name, _, _ = repo_name_with_extension.rpartition('.')
            return repo_name if repo_name else repo_name_with_extension  # handle case where there's no '.git' extension
        else:
            raise ValueError('Invalid Git URL')
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
