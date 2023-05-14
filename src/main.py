from code_processing import comment_files, create_readme

def main():
    directory = "/Users/nico/RepoGPT/REPO"  # replace this with the directory of the repo you want to analyze
    gpt_version = "3.5-turbo"  # replace with "4" if GPT-4 is available and you want to use it

    # Test the comment_files function
    comment_files(directory, gpt_version)

    # Test the create_readme function
    create_readme(directory)

if __name__ == "__main__":
    main()
