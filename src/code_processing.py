import openai
import os
from dotenv import load_dotenv
import textwrap
import libcst as cst


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

    def visit_FunctionDef(self, node):
        self.offsets.append(node.lines[0].start.line)

    def visit_ClassDef(self, node):
        self.offsets.append(node.lines[0].start.line)

def split_code_into_chunks(code):
    module = cst.parse_module(code)
    visitor = FunctionAndClassVisitor()
    module.visit(visitor)

    lines = code.split('\n')
    chunks = []
    start = 0
    for end in visitor.offsets:
        chunks.append('\n'.join(lines[start:end]))
        start = end
    chunks.append('\n'.join(lines[start:]))
    return chunks




def comment_files(directory, gpt_version):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()

                # Split the content into chunks based on function and class boundaries
                chunks = split_code_into_chunks(content)

                analysis = ""
                commented_content = content  # Start with the original content

                # Send each chunk to the OpenAI API for analysis
                for chunk in chunks:
                    response = openai.ChatCompletion.create(
                        # Change the model according to the GPT version
                        model=f"gpt-{gpt_version}",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that analyzes and comments Python code. List any issues you find and suggest improvements and fixes. You can also suggest new features."},
                            {"role": "user", "content": f"Analyze this code:\n{chunk}"}
                        ],
                        max_tokens=1000  # Adjust this as needed
                    )

                    chunk_analysis = response['choices'][0]['message']['content'].strip(
                    )
                    analysis += chunk_analysis + "\n"

                    # Insert the analysis as a comment at the start of the chunk
                    start_line = content[:content.find(chunk)].count('\n') + 1
                    comment = "\n".join("# " + line for line in chunk_analysis.split("\n"))
                    commented_content = commented_content[:start_line] + comment + commented_content[start_line:]

                # Write the analysis to a new markdown file
                new_file_path = file_path.replace(".py", "_repoGPT.md")
                with open(new_file_path, "w") as f:
                    f.write(analysis)

                print(f"Analysis written to {new_file_path}")

                # Write the commented code to a new Python file
                # This makes a new file. Can change maybe a setting to choose new file or overwrite old one.
                new_file_path = file_path.replace(".py", "_commented.py")
                with open(new_file_path, "w") as f:
                    f.write(commented_content)

                print(f"Commented code written to {new_file_path}")


def create_readme(directory):
    print(f"Creating README for directory: {directory}")  # Add this line

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

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if available
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates a README.md file for Python projects."},
            {"role": "user", "content": f"Create a README for this project:\n{readme_content}"}
        ],
        max_tokens=1000  # Adjust this as needed
    )

    final_readme_content = response['choices'][0]['message']['content'].strip()

    readme_filename = "README.md" if "README.md" not in os.listdir(
        directory) else "readme_repoGPT.md"
    readme_file_path = os.path.join(directory, readme_filename)
    with open(readme_file_path, "w") as f:
        f.write(final_readme_content)

    print(f"README file written to {readme_file_path}")  # Add this line


if __name__ == "__main__":
    directory = "REPO"  # replace this with your directory
    print(f"Directory is: {directory}")  # Add this line
    create_readme(directory)
