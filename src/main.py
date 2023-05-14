# src/main.py
from flask import Flask, render_template, request
from git_operations import clone_repo
from code_processing import comment_files, create_readme
from embedding_generation import generate_embeddings
from pinecone_operations import upload_to_pinecone

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        repo_link = request.form.get('repo_link')
        user_choice = request.form.get('user_choice')

        # Clone the repository
        directory = clone_repo(repo_link)

        if user_choice in ['1', '3']:
            # Convert the code into embeddings and upload to Pinecone
            embeddings = generate_embeddings(directory)
            upload_to_pinecone(embeddings)

        if user_choice in ['2', '3']:
            # Comment all files and create README
            comment_files(directory, "3.5-turbo")  # or "4" if GPT-4 is available
            create_readme(directory)

        return 'Operation completed!'
    
    return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
