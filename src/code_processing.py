import openai
import os
from dotenv import load_dotenv
import textwrap


load_dotenv()  # take environment variables from .env.

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

load_dotenv()  # take environment variables from .env.

OPEN_API_KEY = os.getenv("OPEN_API_KEY")

# Use the OpenAI API key from environment variables
openai.api_key = OPEN_API_KEY
def comment_files(directory, gpt_version):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()

                # Split the content into chunks of approximately 2000 tokens each
                # Note: This is not a precise split, as tokens in GPT-3 can vary in length
                chunks = textwrap.wrap(content, 2000)

                analysis = ""

                # Send each chunk to the OpenAI API for analysis
                for chunk in chunks:
                    response = openai.ChatCompletion.create(
                      model=f"gpt-{gpt_version}",  # Change the model according to the GPT version
                      messages=[
                        {"role": "system", "content": "You are a helpful assistant that analyzes and comments Python code. List any issues you find and suggest improvements and fixes. You can also suggest new features."},
                        {"role": "user", "content": f"Analyze this code:\n{chunk}"}
                      ],
                      max_tokens=1000  # Adjust this as needed
                    )

                    chunk_analysis = response['choices'][0]['message']['content'].strip()
                    analysis += chunk_analysis + "\n"

                # Write the analysis to a new markdown file
                new_file_path = file_path.replace(".py", "_repoGPT.md")
                with open(new_file_path, "w") as f:
                    f.write(analysis)

                print(f"Analysis written to {new_file_path}")


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

    readme_filename = "README.md" if "README.md" not in os.listdir(directory) else "readme_repoGPT.md"
    readme_file_path = os.path.join(directory, readme_filename)
    with open(readme_file_path, "w") as f:
        f.write(final_readme_content)

    print(f"README file written to {readme_file_path}")  # Add this line


if __name__ == "__main__":
    directory = "REPO"  # replace this with your directory
    print(f"Directory is: {directory}")  # Add this line
    create_readme(directory)
