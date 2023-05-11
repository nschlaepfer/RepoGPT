import os

def read_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"): # assuming we're only interested in Python files
                with open(os.path.join(root, file), "r") as f:
                    content = f.read()
                # Here, you could add your code to comment the code, create README, etc.
                # ...


def get_user_input():
    print("Welcome to the GitHub Repository Analyzer!")
    repo_link = input("Please enter the link to the GitHub repo you want to analyze: ")
    print("Select an operation: ")
    print("1. Convert the code into embeddings and upload to Pinecone.")
    print("2. Comment all files, create README, and a file structure guide.")
    print("3. Perform both operations.")
    user_choice = input("Your choice (1/2/3): ")
    
    return repo_link, user_choice

from git import Repo

def clone_repo(repo_link, repo_dir):
    Repo.clone_from(repo_link, repo_dir)
