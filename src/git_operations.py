# src/git_operations.py

from git import Repo
import os

import git

def clone_repo(repo_link):
    repo_dir = "./REPO"
    git.Repo.clone_from(repo_link, repo_dir)
    return repo_dir
