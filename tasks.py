import os
import subprocess
from llm_client import query_llm
import requests
import shutil
import re
import os
from datetime import datetime
from dateutil import parser
import json
import glob
import os
import pytesseract
from PIL import Image
from llm_client import query_llm
import os
import itertools
import numpy as np
from sentence_transformers import SentenceTransformer
from llm_client import query_llm
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from llm_client import query_llm
import os
from urllib.parse import urlparse
from difflib import get_close_matches

def find_best_task_match(task_description: str):
    """Finds the closest matching task from predefined task_mapping."""
    task_description = task_description.lower().strip()
    
    # Try exact match first
    if task_description in task_mapping:
        return task_mapping[task_description]
    
    # Use fuzzy matching for partial matches
    possible_matches = get_close_matches(task_description, task_mapping.keys(), n=1, cutoff=0.6)
    
    if possible_matches:
        return task_mapping[possible_matches[0]]
    
    return None  # No close match found



def task_a1(user_email: str) -> str:
    """
    Task A1: Install 'uv' if not already installed and run the datagen.py script
    with the provided user email as the only argument.
    """
    # Step 1: Check if 'uv' is installed
    if shutil.which("uv") is None:
        print("uv not found. Installing uv...")
        try:
            # Install uv using pip
            subprocess.run(["pip", "install", "uv"], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception("Failed to install uv: " + str(e))
    else:
        print("uv is already installed.")
    
    # Step 2: Download datagen.py from the provided URL
    datagen_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
    try:
        response = requests.get(datagen_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download datagen.py. Status code: {response.status_code}")
    except Exception as e:
        raise Exception("Error downloading datagen.py: " + str(e))
    
    # Save the downloaded script locally (you can overwrite if it exists)
    script_path = "datagen.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print("datagen.py downloaded successfully.")
    
    # Step 3: Modify the script to use a writable data directory
    # Step 3: Modify the script to use a writable data directory
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Print a snippet to see what the config looks like (for debugging)
        snippet = content[:300]
        print("First 300 characters of datagen.py:\n", snippet)
        
        # Replace any occurrence of '"/data"' with '"./data"'
        if '"/data"' in content:
            print('Found "/data" in the file, replacing with "./data"...')
            modified_content = content.replace('"/data"', '"./data"')
        else:
            # As a fallback, try replacing /data with ./data
            print("'/data' not found in quotes; attempting a broad replacement.")
            modified_content = content.replace('/data', './data')
        
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        
        print("Modified datagen.py to use a writable directory.")
    except Exception as e:
        raise Exception("Error modifying datagen.py: " + str(e))
    
    # Ensure the local data directory exists
    data_dir = "./data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Step 4: Run the modified script with the user email as argument
    try:
        subprocess.run(["python", script_path, user_email], check=True)
    except subprocess.CalledProcessError as e:
        raise Exception("Error running datagen.py: " + str(e))
    
    return "Task A1 completed successfully."


def task_a2():
    filepath = "./data/format.md"
    if not os.path.exists(filepath):
        raise ValueError("File not found: " + filepath)
    try:
        # Run prettier@3.4.2 using npx to format the file in-place
        subprocess.run(["npx", "prettier@3.4.2", "--write", filepath], check=True)
        return "File formatted successfully."
    except subprocess.CalledProcessError as e:
        raise Exception("Formatting failed: " + str(e))


def task_a3():
    input_file = "./data/dates.txt"
    output_file = "./data/dates-wednesdays.txt"
    
    if not os.path.exists(input_file):
        raise ValueError(f"Input file not found: {input_file}")
    
    wednesday_count = 0
    with open(input_file, "r") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            try:
                # Parse the date from any format
                date_obj = parser.parse(line)
                
                # Convert to standard format (YYYY-MM-DD) if needed
                formatted_date = date_obj.strftime("%Y-%m-%d")
                
                # Check if it's a Wednesday (Monday=0, Tuesday=1, Wednesday=2)
                if date_obj.weekday() == 2:
                    wednesday_count += 1
            except Exception as e:
                print(f"Skipping line with invalid date format: {line}")

    # Write the count to the output file
    with open(output_file, "w") as outfile:
        outfile.write(str(wednesday_count))
    
    return f"Found {wednesday_count} Wednesdays in {input_file} and wrote to {output_file}"

def task_a4():
    input_file = "./data/contacts.json"
    output_file = "./data/contacts-sorted.json"
    
    if not os.path.exists(input_file):
        raise ValueError(f"Input file not found: {input_file}")
    
    with open(input_file, "r", encoding="utf-8") as infile:
        contacts = json.load(infile)
    
    if not isinstance(contacts, list):
        raise ValueError("Invalid JSON format: Expected a list of contacts")
    
    sorted_contacts = sorted(contacts, key=lambda c: (c.get("last_name", ""), c.get("first_name", "")))
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(sorted_contacts, outfile, indent=4)
    
    return f"Sorted contacts written to {output_file}"


def task_a5():
    log_dir = "./data/logs/"
    output_file = "./data/logs-recent.txt"

    # Get a list of all .log files in the directory, sorted by modified time (most recent first)
    log_files = sorted(glob.glob(os.path.join(log_dir, "*.log")), key=os.path.getmtime, reverse=True)

    # Take the 10 most recent files
    recent_logs = log_files[:10]

    first_lines = []
    
    for log_file in recent_logs:
        try:
            with open(log_file, "r") as f:
                first_line = f.readline().strip()  # Read the first line
                if first_line:
                    first_lines.append(first_line)
        except Exception as e:
            print(f"Skipping {log_file} due to error: {e}")

    # Write the collected first lines to the output file
    with open(output_file, "w") as out:
        out.write("\n".join(first_lines))

    return f"Wrote first lines of {len(first_lines)} most recent log files to {output_file}"

def task_a6():
    docs_dir = "./data/docs/"
    output_file = "./data/docs/index.json"
    
    index = {}

    # Get all markdown files
    md_files = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True)

    for md_file in md_files:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# "):  # H1 header
                        filename = os.path.relpath(md_file, docs_dir)  # Get filename relative to /data/docs/
                        index[filename] = line[2:].strip()  # Extract title after "# "
                        break  # Only take the first H1
        except Exception as e:
            print(f"Skipping {md_file} due to error: {e}")

    # Write index to JSON file
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(index, out, indent=4)

    return f"Created index file with {len(index)} entries in {output_file}"

import os
from llm_client import query_llm

def task_a7():
    input_file = "./data/email.txt"
    output_file = "./data/email-sender.txt"

    if not os.path.exists(input_file):
        raise ValueError(f"Input file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as infile:
        email_content = infile.read().strip()

    if not email_content:
        raise ValueError(f"Email file '{input_file}' is empty")

    # Construct the LLM prompt
    prompt = f"""
    Extract the sender's email address from the following email message. 
    Only return the email address, nothing else.

    Email content:
    {email_content}
    """

    try:
        sender_email = query_llm(prompt).strip()

        # Validate LLM response (Basic check for email format)
        if "@" not in sender_email or "." not in sender_email:
            raise ValueError(f"Invalid email extracted: {sender_email}")

        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write(sender_email)

        return f"Extracted sender's email: {sender_email} and wrote to {output_file}"

    except Exception as e:
        raise RuntimeError(f"Failed to extract email: {e}")



def task_a8():
    input_file = "./data/credit_card.png"
    output_file = "./data/credit_card.txt"

    if not os.path.exists(input_file):
        raise ValueError(f"Input file not found: {input_file}")

    # Open image and extract text using OCR
    image = Image.open(input_file)
    extracted_text = pytesseract.image_to_string(image).strip()

    if not extracted_text:
        raise ValueError("No text detected in the image.")

    # Send the extracted text to LLM to refine the credit card number
    prompt = f"""
    Extract the credit card number from the following OCR result.
    Return only the card number as a continuous string with no spaces or dashes.

    OCR extracted text:
    {extracted_text}
    """

    try:
        card_number = query_llm(prompt).strip()

        # Validate extracted card number
        if not card_number.isdigit() or len(card_number) not in [13, 14, 15, 16, 19]: 
            raise ValueError(f"Invalid credit card number extracted: {card_number}")

        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write(card_number)

        return f"Extracted credit card number and wrote to {output_file}"

    except Exception as e:
        raise RuntimeError(f"Failed to extract credit card number: {e}")


def task_a9():
    input_file = "./data/comments.txt"
    output_file = "./data/comments-similar.txt"

    if not os.path.exists(input_file):
        raise ValueError(f"Input file not found: {input_file}")

    # Read comments from file
    with open(input_file, "r", encoding="utf-8") as infile:
        comments = [line.strip() for line in infile if line.strip()]

    if len(comments) < 2:
        raise ValueError("Not enough comments to find a similar pair.")

    # Load pre-trained sentence embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight, fast model

    # Compute embeddings
    embeddings = model.encode(comments, convert_to_numpy=True)

    # Compute cosine similarity matrix
    num_comments = len(comments)
    max_similarity = -1
    most_similar_pair = None

    for (i, j) in itertools.combinations(range(num_comments), 2):
        similarity = np.dot(embeddings[i], embeddings[j]) / (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]))

        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_pair = (comments[i], comments[j])

    if not most_similar_pair:
        raise RuntimeError("No similar comment pair found.")

    # Write most similar pair to file
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(f"{most_similar_pair[0]}\n{most_similar_pair[1]}")

    return f"Most similar comments written to {output_file}"

def task_a10():
    db_file = "./data/ticket-sales.db"
    output_file = "./data/ticket-sales-gold.txt"

    if not os.path.exists(db_file):
        raise ValueError(f"Database file not found: {db_file}")

    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Query total sales for "Gold" tickets
    query = """
    SELECT SUM(units * price) 
    FROM tickets 
    WHERE type = 'Gold'
    """
    cursor.execute(query)
    result = cursor.fetchone()
    total_sales = result[0] if result[0] is not None else 0

    conn.close()  # Close the connection

    # Write result to file
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(str(total_sales))

    return f"Total sales for 'Gold' tickets: {total_sales}, written to {output_file}"






# Detailed task mapping for robust instruction matching
app = FastAPI()

# Detailed task mapping for robust instruction matching
task_mapping = {
    # Existing Tasks (A1 - A10)
    "install uv and run datagen": "task_a1",
    "run datagen.py": "task_a1",
    "format markdown file": "task_a2",
    "count wednesdays in file": "task_a3",
    "sort contacts by name": "task_a4",
    "fetch recent log entries": "task_a5",
    "create markdown index": "task_a6",
    "extract email sender": "task_a7",
    "extract credit card number": "task_a8",
    "find most similar comments": "task_a9",
    "calculate gold ticket sales": "task_a10",
    
    # **New Tasks (B3 - B10)**
    "fetch data from ": "task_b3",
    "retrieve data via ": "task_b3",
    "fetch and save api response": "task_b3",

    "clone git repo and commit": "task_b4",
    "make a commit in git repository": "task_b4",
    "clone repository and push changes": "task_b4",

    "run sql query on database": "task_b5",
    "execute query in sqlite or duckdb": "task_b5",
    "fetch data from database": "task_b5",

    "scrape website for data": "task_b6",
    "extract information from webpage": "task_b6",
    "web scraping task": "task_b6",

    "compress or resize image": "task_b7",
    "reduce image size": "task_b7",
    "convert image format": "task_b7",

    "transcribe mp3 audio": "task_b8",
    "convert speech to text": "task_b8",
    "generate transcription from audio": "task_b8",

    "convert markdown to html": "task_b9",
    "render markdown as webpage": "task_b9",
    "transform md to html": "task_b9",

    "filter csv and return json": "task_b10",
    "apply conditions to csv and output json": "task_b10",
    "query csv file as json api": "task_b10"
}

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_task_from_llm_response(llm_response):
    """Extracts the best-matching predefined task using cosine similarity."""
    
    llm_response = llm_response.lower()
    task_names = list(task_mapping.keys())

    # Compute TF-IDF vectors
    vectorizer = TfidfVectorizer().fit(task_names + [llm_response])
    vectors = vectorizer.transform(task_names + [llm_response])

    # Compute cosine similarity between LLM response and predefined tasks
    similarities = cosine_similarity(vectors[-1:], vectors[:-1]).flatten()

    # Get the best-matching task
    best_match_index = similarities.argmax()
    best_match_score = similarities[best_match_index]

    # Set a threshold (adjustable) to ensure valid match
    if best_match_score > 0.3:  # 30% similarity is a safe threshold
        return task_mapping[task_names[best_match_index]]

    return None  # No good match found



from urllib.parse import urlparse
import re
import os

@app.post("/run")
def run_task(task: str = Query(..., description="Task description in plain English")):
    """Executes a task based on the description with security constraints."""
    
    task_name = task_mapping.get(task.lower())

    if not task_name:
        # Use LLM if no exact match is found
        llm_prompt = f"Determine which predefined task best matches: {task}"
        llm_suggestion = query_llm(llm_prompt).strip()
        print(llm_suggestion)
        
        # Extract the actual task name from LLM response
        task_name = extract_task_from_llm_response(llm_suggestion)
        print(task_name)

        if not task_name:
            raise HTTPException(status_code=400, detail=f"Unrecognized task description: {task}")

    # 🚀 Task B3: Extract API URL (No changes here)
    api_url = None
    if task_name == "task_b3":
        words = task.split()
        for word in words:
            if word.startswith("http://") or word.startswith("https://"):
                api_url = word
                break

        if not api_url:
            raise HTTPException(status_code=400, detail="Task B3 requires an API URL in the description")

        # Validate API URL
        parsed_url = urlparse(api_url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise HTTPException(status_code=400, detail="Invalid API URL provided")

    # 🚀 Task B4: Extract Repository URL, Actions & Commit Message
    repo_url = None
    commit_message = "Automated commit"  # Default commit message
    clone_repo = "clone" in task.lower()
    make_commit = "commit" in task.lower()

    if task_name == "task_b4":
        words = task.split()
        for word in words:
            if word.startswith("http://") or word.startswith("https://"):
                repo_url = word
                break

        if not repo_url:
            raise HTTPException(status_code=400, detail="Task B4 requires a repository URL in the description")

        parsed_url = urlparse(repo_url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise HTTPException(status_code=400, detail="Invalid repository URL provided")

        # Extract commit message if committing
        match = re.search(r'commit with message "(.*?)"', task)
        if match:
            commit_message = match.group(1)

    # 🚀 Task B5: Extract Database Name and Query
    db_type = None
    db_name = None
    sql_query = None

    if task_name == "task_b5":
        # Extract database type (SQLite or DuckDB)
        if "sqlite" in task.lower():
            db_type = "sqlite"
        elif "duckdb" in task.lower():
            db_type = "duckdb"

        # Extract database name (e.g., `ticket_sales.db`)
        match_db = re.search(r"on (\S+\.db)", task)
        if match_db:
            db_name = match_db.group(1)

        # Extract SQL query (text inside single or double quotes)
        match_query = re.search(r"with ['\"](.*?)['\"]", task)
        if match_query:
            sql_query = match_query.group(1)

        # Validate required fields
        if not (db_type and db_name and sql_query):
            raise HTTPException(status_code=400, detail="Task B5 requires a valid database type, database name, and SQL query.")

    # 🚀 Task B6: Extract Website URL
    website_url = None

    if task_name == "task_b6":
        words = task.split()
        for word in words:
            if word.startswith("http://") or word.startswith("https://"):
                website_url = word
                break

        if not website_url:
            raise HTTPException(status_code=400, detail="Task B6 requires a valid website URL in the description.")
    


        # 🚫 Ensure task does not attempt deletion (B2)
        if "delete" in task.lower() or "remove" in task.lower():
            raise HTTPException(status_code=403, detail="Deleting data is not allowed")

        # ✅ Execute task
        task_func = globals().get(task_name)
        if not task_func:
            raise HTTPException(status_code=500, detail=f"Task function {task_name} not found in tasks.py")

        try:
            if task_name == "task_b3":
                result = task_func(api_url)  # Pass API URL
            elif task_name == "task_b4":
                result = task_func(repo_url, clone_repo, make_commit, commit_message)  # Pass repo details
            elif task_name == "task_b5":
                result = task_func(db_type, db_name, sql_query)  # Pass database details
            elif task_name == "task_b6":
                result = task_func(website_url)
            else:
                result = task_func()

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Execution error in {task_name}: {str(e)}")

        return {"message": "Task executed successfully", "result": result}


@app.get("/read")
def read_file(path: str = Query(..., description="Path of the file to read")):
    """Reads the content of a file with security restrictions."""
    
    # Ensure access is only within /data/
    if not path.startswith("/data/"):
        raise HTTPException(status_code=403, detail="Access to files outside /data/ is forbidden")
    
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    
    return {"file": path, "content": content}


def task_b3(api_url):
    """Fetches data from an API and saves it to /data/api_data.json."""
    save_path = "./data/api_data.json"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Ensure /data exists

    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
        
        with open(save_path, "w", encoding="utf-8") as file:
            file.write(response.text)
        
        return f"API data fetched and saved to {save_path}"
    
    except requests.exceptions.RequestException as e:
        return f"API request failed: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    

def task_b4(repo_url, clone_repo, make_commit, commit_message):
    """Clones a Git repository and/or makes a commit."""

    base_dir = os.path.abspath("./data/repos")
    os.makedirs(base_dir, exist_ok=True)

    # Extract repo name from URL
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    repo_path = os.path.join(base_dir, repo_name)

    print(f"Base Directory: {base_dir}")
    print(f"Target Repo Path: {repo_path}")

    # Clone the repo if requested
    if clone_repo:
        if os.path.exists(repo_path):
            print(f"Repository {repo_name} already exists at {repo_path}")
        else:
            try:
                print(f"Cloning repository: {repo_url} into {repo_path}")
                subprocess.run(["git", "clone", repo_url, repo_path], check=True)
            except subprocess.CalledProcessError as e:
                return f"Error cloning repository: {e}"

    # Make a commit if requested
    if make_commit:
        if not os.path.exists(repo_path):
            return f"Repository {repo_name} not found. Clone it first before committing."

        try:
            os.chdir(repo_path)
            print(f"Changed working directory to: {os.getcwd()}")

            # Create a dummy file if it doesn't exist
            file_path = os.path.join(repo_path, "dummy.txt")
            if not os.path.exists(file_path):
                print(f"Creating dummy file: {file_path}")
                with open(file_path, "w") as file:
                    file.write("Automated commit entry\n")
            else:
                print(f"Appending to existing dummy file: {file_path}")
                with open(file_path, "a") as file:
                    file.write("\nAnother commit entry\n")

            # Add & commit changes
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            return f"Committed changes in {repo_name} with message: '{commit_message}'"
        except subprocess.CalledProcessError as e:
            return f"Error making commit: {e}"
        finally:
            os.chdir(base_dir)
            print(f"Reverted to base directory: {os.getcwd()}")

    return f"Task completed successfully for {repo_name}"

def task_b5(db_type, db_name, sql_query):
    """
    Runs an SQL query on a SQLite or DuckDB database.
    
    :param db_type: Type of database ("sqlite" or "duckdb").
    :param db_name: Name of the database file.
    :param sql_query: SQL query to execute.
    :return: Query result or error message.
    """
    
    base_dir = "./data"
    os.makedirs(base_dir, exist_ok=True)  # Ensure database directory exists

    db_path = os.path.join(base_dir, db_name)

    if db_type not in ["sqlite", "duckdb"]:
        return f"Error: Unsupported database type '{db_type}'. Use 'sqlite' or 'duckdb'."

    try:
        if db_type == "sqlite":
            conn = sqlite3.connect(db_path)
        else:
            conn = duckdb.connect(db_path)
        
        cursor = conn.cursor()
        cursor.execute(sql_query)

        # Fetch results if it's a SELECT query
        if sql_query.strip().lower().startswith("select"):
            columns = [desc[0] for desc in cursor.description]  # Column names
            data = cursor.fetchall()  # Query result
            result = [dict(zip(columns, row)) for row in data]
        else:
            conn.commit()
            result = "Query executed successfully"

        cursor.close()
        conn.close()
        return result
    
    except Exception as e:
        return f"SQL Execution Error: {str(e)}"
    
import requests
from bs4 import BeautifulSoup

def task_b6(website_url):
    """Scrapes data from the given website URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(website_url, headers=headers)
        response.raise_for_status()  # Raise error for bad response

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract website title
        title = soup.title.string if soup.title else "No title found"

        # Extract all text content
        paragraphs = [p.get_text() for p in soup.find_all("p")]

        return {
            "title": title,
            "paragraphs": paragraphs[:5]  # Limit to first 5 paragraphs
        }

    except requests.RequestException as e:
        return f"Error fetching website: {str(e)}"


if __name__ == "__main__":
    # Replace with your actual email
    #email = "21F1005745@iitm.ac.in"
    result = run_task("scrape data from https://news.ycombinator.com")

    print(result)


