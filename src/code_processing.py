import openai
import os
from dotenv import load_dotenv
import textwrap
import libcst as cst
from tqdm import tqdm
import time
from bs4 import BeautifulSoup
from slimit.parser import Parser
from slimit.visitors import nodevisitor
from slimit import ast


load_dotenv()  # take environment variables from .env.

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")



# Use the OpenAI API key from environment variables
openai.api_key = OPEN_API_KEY


import libcst as cst

class FunctionAndClassVisitor(cst.CSTVisitor):
    def __init__(self):
        self.offsets = []

def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
    self.offsets.append(node.whitespace_before_colon.start.line)

def visit_ClassDef(self, node: cst.ClassDef) -> None:
    self.offsets.append(node.whitespace_before_colon.start.line)


def split_code_into_chunks(code, file_extension):
    lines = code.split("\n")
    offsets = []

    if file_extension == ".py":
        module = cst.parse_module(code)
        visitor = FunctionAndClassVisitor()
        module.visit(visitor)
        offsets = visitor.offsets
    elif file_extension in [".js", ".ts", ".tsx"]:
        parser = Parser()
        tree = parser.parse(code)
        for node in nodevisitor.visit(tree):
            if isinstance(node, (ast.FunctionDeclaration, ast.FunctionExpression, ast.ClassDeclaration)):
                offsets.append(node.location.line)
    elif file_extension == ".html":
        # BeautifulSoup HTML parsing here
        soup = BeautifulSoup(code, 'html.parser')
        offsets = [tag.line for tag in soup]
    else:
        # Add more parsers as needed
        return []

    chunks = []
    start = 0
    for end in offsets:
        chunks.append("\n".join(lines[start:end]))
        start = end
    chunks.append("\n".join(lines[start:]))

    return chunks
 

# Retry configuration
max_retries = 3
retry_delay = 5  # in seconds

def process_chunk_with_openai(chunk, gpt_version):
    retries = 0
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model=f"gpt-{gpt_version}",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes and comments code. List any issues you find and suggest improvements and fixes. You can also suggest new features."},
                    {"role": "user", "content": f"Analyze this code:\n{chunk}"}
                ],
                max_tokens=1000  # Adjust this as needed
            )
            return response['choices'][0]['message']['content'].strip()
        except openai.error.RateLimitError:
            print("Rate limit exceeded. Retrying after delay...")
            time.sleep(retry_delay)
            retries += 1

    return "Unable to process chunk at the moment. Please try again later."



def comment_files(directory, gpt_version, open_api_key=None):
    supported_extensions = [".js", ".py", ".ts", ".tsx", ".c", ".cpp", ".html", ".json"]

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            _, file_extension = os.path.splitext(file)
            if file_extension in supported_extensions:
                with open(file_path, "r") as f:
                    content = f.read()
                    
                try:
                    chunks = split_code_into_chunks(content, file_extension)  # Pass in the file extension
                except Exception as e:
                   print(f"Error processing file: {file_path}")
                   print(e)
                   continue

            
                analysis = ""
                commented_content = content  # Start with the original content

                # Send each chunk to the OpenAI API for analysis
                with tqdm(total=len(chunks), desc="Processing", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
                    for chunk in chunks:
                        chunk_analysis = process_chunk_with_openai(chunk, gpt_version)
                        analysis += chunk_analysis + "\n"

                        # Insert the analysis as a comment at the start of the chunk
                        commented_content = chunk_analysis + "\n" + commented_content

                        pbar.update(1)  # Update the progress bar

                # Write the analysis to a new file
                new_file_path = file_path.replace(file_extension, f"_repoGPT{file_extension}")
                with open(new_file_path, "w") as f:
                    f.write(analysis)

                print(f"Analysis written to {new_file_path}")

                # Write the commented code to a new file
                new_file_path = file_path.replace(file_extension, f"_commented{file_extension}")
                with open(new_file_path, "w") as f:
                    f.write(commented_content)

                print(f"Commented code written to {new_file_path}")



def create_readme(directory):
    print(f"Creating README for directory: {directory}")

    readme_content = f"# Repository Overview\n\n"
    readme_content += f"Repository Path: {directory}\n\n"
    readme_content += "## File Structure\n\n"

    file_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                readme_content += f"- {os.path.join(root, file)}\n"
                file_count += 1

    readme_content = f"Total Python Files: {file_count}\n\n" + readme_content

    with tqdm(total=1, desc="Generating README", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates a README.md file for Python projects."},
                {"role": "user", "content": f"Create a README for this project:\n{readme_content}"}
            ],
            max_tokens=1000  # Adjust this as needed
        )
        pbar.update(1)

        final_readme_content = response['choices'][0]['message']['content'].strip()

        readme_filename = "README.md" if "README.md" not in os.listdir(directory) else "readme_repoGPT.md"
        readme_file_path = os.path.join(directory, readme_filename)
        with open(readme_file_path, "w") as f:
            f.write(final_readme_content)

        print(f"README file written to {readme_file_path}")


if __name__ == "__main__":
    directory = "REPO"  # replace this with your directory
    print(f"Directory is: {directory}")  # Add this line
    create_readme(directory)
