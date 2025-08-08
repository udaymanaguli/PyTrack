import os
import shutil
import sys
import hashlib
import time
import uuid
import json
from datetime import datetime

# --- PHASE 1: init ---
def init():
    MINIGIT_DIR = ".minigit"
    if not os.path.exists(MINIGIT_DIR):
        os.makedirs(MINIGIT_DIR)
        os.makedirs(os.path.join(MINIGIT_DIR, "staging"))
        os.makedirs(os.path.join(MINIGIT_DIR, "committed"))
        with open(os.path.join(MINIGIT_DIR, "log.txt"), "w") as f:
            f.write("")
        print("Initialized empty MiniGit repository.")
    else:
        # Still ensure required subfolders exist
        os.makedirs(os.path.join(MINIGIT_DIR, "staging"), exist_ok=True)
        os.makedirs(os.path.join(MINIGIT_DIR, "committed"), exist_ok=True)
        log_path = os.path.join(MINIGIT_DIR, "log.txt")
        if not os.path.exists(log_path):
            with open(log_path, "w") as f:
                f.write("")
        print("Repository already initialized.")


def ensure_minigit_directory():
    MINIGIT_DIR = ".minigit"
    os.makedirs(MINIGIT_DIR, exist_ok=True)
    os.makedirs(os.path.join(MINIGIT_DIR, "commits"), exist_ok=True)
    os.makedirs(os.path.join(MINIGIT_DIR, "staging"), exist_ok=True)

# --- PHASE 2: add ---
def hash_file(content):
    return hashlib.sha1(content.encode()).hexdigest()

def add(file_path):
    MINIGIT_DIR = ".minigit"
    staging_path = os.path.join(MINIGIT_DIR, "staging")
    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist.")
        return
    shutil.copy2(file_path, staging_path)
    print(f"Added '{file_path}' to staging area.")




def commit(message):
    MINIGIT_DIR = ".minigit"
    ensure_minigit_directory()

    # Paths
    commits_path = os.path.join(MINIGIT_DIR, "commits")
    staging_path = os.path.join(MINIGIT_DIR, "staging")
    commits_json_path = os.path.join(MINIGIT_DIR, "commits.json")

    # Create new commit ID with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    commit_id = f"commit_{timestamp}"
    commit_dir = os.path.join(commits_path, commit_id)
    os.makedirs(commit_dir)

    # Copy staged files to commit folder
    committed_files = []
    for filename in os.listdir(staging_path):
        src = os.path.join(staging_path, filename)
        dst = os.path.join(commit_dir, filename)
        shutil.copy2(src, dst)
        committed_files.append(filename)

    # Load previous commits (if any)
    if os.path.exists(commits_json_path):
        with open(commits_json_path, "r") as f:
            commits = json.load(f)
    else:
        commits = []

    # Add this commit to commits list
    commits.append({
        "id": commit_id,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": committed_files
    })

    # Save back to commits.json
    with open(commits_json_path, "w") as f:
        json.dump(commits, f, indent=4)

    # Clear staging
    for filename in os.listdir(staging_path):
        os.remove(os.path.join(staging_path, filename))

    print(f"Committed: {message}")



def log():
    MINIGIT_DIR = ".minigit"
    commits_path = os.path.join(MINIGIT_DIR, "commits.json")

    if not os.path.exists(commits_path):
        print("No commits found.")
        return

    with open(commits_path, "r") as f:
        commits = json.load(f)

    if not commits:
        print("No commits found.")
        return

    for i, commit in reversed(list(enumerate(commits))):
        print(f"Commit {i + 1}: {commit['id']}")
        print(f"Message   : {commit['message']}")
        print(f"Timestamp : {commit['timestamp']}")
        print(f"Files     : {', '.join(commit['files'])}")
        print("-" * 40)


def status():
    MINIGIT_DIR = ".minigit"
    staging_path = os.path.join(MINIGIT_DIR, "staging")
    commits_json_path = os.path.join(MINIGIT_DIR, "commits.json")

    # Get all working directory files excluding internal files
    working_dir_files = set(os.listdir(".")) - {".minigit", "minigit.py", "__pycache__"}

    # Staged files
    staging_files = set(os.listdir(staging_path)) if os.path.exists(staging_path) else set()

    # Get latest committed files from commits.json
    committed_files = set()
    if os.path.exists(commits_json_path):
        with open(commits_json_path, "r") as f:
            commits = json.load(f)
            if commits:
                committed_files = set(commits[-1]["files"])

    # === Staged for commit ===
    print("\n=== Staged for commit ===")
    for file in staging_files:
        print(f"  {file}")

    # === Modified but not staged ===
    print("\n=== Modified but not staged ===")
    for file in staging_files:
        if file in working_dir_files:
            with open(file, "rb") as f1, open(os.path.join(staging_path, file), "rb") as f2:
                if f1.read() != f2.read():
                    print(f"  {file}")

    # === Untracked files ===
    print("\n=== Untracked files ===")
    for file in working_dir_files:
        if file not in staging_files and file not in committed_files:
            print(f"  {file}")

    # === Deleted files ===
    if committed_files:
        deleted_files = set()
        for file in committed_files:
            if not os.path.exists(file):
                deleted_files.add(file)

        if deleted_files:
            print("\n=== Deleted files ===")
            for file in deleted_files:
                print(f"  {file}")




# --- Main entry point ---
def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [arguments]")
        return

    command = sys.argv[1]

    if command == "init":
        init()
    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: python main.py add <filename>")
        else:
            add(sys.argv[2])
    elif command == "commit":
        if len(sys.argv) < 3:
            print("Usage: python main.py commit <message>")
        else:
            commit(sys.argv[2])
    elif command == "log":
        log()
    elif command == "status":
        status()
    elif command == "help":
        print("""
Available commands:
  init                 Initialize a new Mini Git repo
  add <filename>       Add a file to staging area
  commit <message>     Commit staged changes with a message
  log                  Show commit history
  status               Show status of working directory
  help                 Show this help message
""")
    else:
        print(f"Unknown command: {command}. Use 'help' to see available commands.")


if __name__ == "__main__":
    main()

