# analyzer/repository_handler.py

import os
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse

from .utils.temp_dir import temp_directory



class RepositoryHandler:
    """
    Handles source input either from a local directory or a remote GitHub repository.
    """

    def __init__(self, default_branch: str = "main"):
        self.default_branch = default_branch

    def is_github_url(self, source: str) -> bool:
        """
        Check if the source string is a GitHub repository URL.
        """
        parsed = urlparse(source)
        return parsed.netloc == "github.com" and parsed.scheme == "https"

    def _clone_repo_to_temp(self, repo_url: str, branch: str) -> str:
        """
        Clone the GitHub repository to a temporary, persistent directory.

        Args:
            repo_url (str): GitHub repository URL.
            branch (str): Branch to clone.

        Returns:
            str: Path to the cloned repository.
        """
        with temp_directory(prefix="repo_clone_") as temp_dir:
            try:
                subprocess.check_call([
                    "git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir
                ])
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to clone repository: {repo_url}\n{e}")

            # Move to persistent temp directory
            final_temp_dir = tempfile.mkdtemp(prefix="cloned_repo_")
            self._copy_dir(temp_dir, final_temp_dir)
            return final_temp_dir

    def _copy_dir(self, src: str, dst: str):
        """
        Recursively copies contents of one directory to another.

        Args:
            src (str): Source directory.
            dst (str): Destination directory.
        """
        for item in os.listdir(src):
            s_item = os.path.join(src, item)
            d_item = os.path.join(dst, item)
            if os.path.isdir(s_item):
                shutil.copytree(s_item, d_item)
            else:
                shutil.copy2(s_item, d_item)

    def resolve_source(self, source: str, branch: str = None) -> str:
        """
        Determines if the source is a GitHub URL or local path and returns the valid local directory.

        Args:
            source (str): GitHub URL or local file path.
            branch (str, optional): Branch to clone if source is GitHub. Defaults to 'main'.

        Returns:
            str: Absolute path to the resolved codebase.

        Raises:
            ValueError: If the source is neither a valid URL nor existing path.
        """
        branch = branch or self.default_branch

        if self.is_github_url(source):
            return self._clone_repo_to_temp(source, branch)

        if os.path.exists(source) and os.path.isdir(source):
            return os.path.abspath(source)

        raise ValueError(f"Invalid source: '{source}'. Provide a valid local path or GitHub repository URL.")
