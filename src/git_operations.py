# src/git_operations.py

from git import Repo
import os

def clone_repo(repo_link, repo_dir):
    # Check if the directory already exists
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)
    # Clone the repo
    Repo.clone_from(repo_link, repo_dir)

# testing
if __name__ == "__main__":
    clone_repo("https://github.com/peterw/Chat-with-Github-Repo", "/Users/nico/RepoGPT/REPO")
