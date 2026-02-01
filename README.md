# MiniGit

A Python-based minimal version control system inspired by Git, allowing basic repository management from the command line.

## Features
- Initialize a repository (`init`) with `.minigit` folder structure
- Stage files for commit (`add <filename>`)
- Commit staged files with a message (`commit <message>`)
- View commit history (`log`)
- Check repository status (`status`)
- Simple command-line interface, no external dependencies

## Tech Stack
- Python 3.x
- Standard Library: `os`, `shutil`, `sys`, `hashlib`, `json`, `datetime`, `uuid`
