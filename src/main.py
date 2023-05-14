# src/main.py
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from git_operations import clone_repo
from code_processing import comment_files, create_readme
from embedding_generation import generate_embeddings
from pinecone_operations import upload_to_pinecone

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        repo_link = request.form.get('repo_link')
        user_choice = request.form.get('user_choice')
        pinecone_api_key = request.form.get('pinecone_api_key')
        open_api_key = request.form.get('open_api_key')

        if not pinecone_api_key:
            pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if not open_api_key:
            open_api_key = os.getenv('OPEN_API_KEY')

        # Clone the repository
        directory = clone_repo(repo_link)

        result_text = ""

        if user_choice in ['1', '3']:
            # Convert the code into embeddings and upload to Pinecone
            embeddings = generate_embeddings(directory)
            upload_to_pinecone(embeddings, pinecone_api_key)
            result_text += "Embeddings generated and uploaded to Pinecone.\n"

        if user_choice in ['2', '3']:
            # Comment all files and create README
            comment_files(directory, "3.5-turbo", open_api_key)  # or "4" if GPT-4 is available
            create_readme(directory)
            result_text += "Files commented and README created.\n"

        return render_template('result.html', result_text=result_text)
    
    return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
