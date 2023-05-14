# src/user_interface.py

def get_user_input():
    print("Welcome to the GitHub Repository Analyzer!")
    repo_link = input("Please enter the link to the GitHub repo you want to analyze: ")
    print("Select an operation: ")
    print("1. Convert the code into embeddings and upload to Pinecone.")
    print("2. Comment all files, create README, and a file structure guide.")
    print("3. Perform both operations.")
    user_choice = input("Your choice (1/2/3): ")
    


    
    return repo_link, user_choice


if __name__ == "__main__":
    repo_link, user_choice = get_user_input()
    print(f"Received repo link: {repo_link}")
    print(f"User's choice: {user_choice}")


