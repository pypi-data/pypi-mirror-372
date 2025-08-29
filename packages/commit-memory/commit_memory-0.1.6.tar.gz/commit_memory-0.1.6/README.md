# Commit Memory

A Git companion tool that allows you to attach notes and memos to specific commits and file lines in your Git repository. Commit Memory helps you document the reasoning behind code changes, track important decisions, and share knowledge with your team.

## Project Purpose

Commit Memory solves the problem of preserving context and knowledge about code changes that might not be appropriate for commit messages but are still valuable to remember. It allows you to:

- Document the "why" behind code changes
- Leave notes for yourself or team members about specific lines of code
- Create a searchable history of decisions and explanations
- Keep track of important information without cluttering commit messages

## Key Features

- **Commit Memos**: Attach notes to entire commits
- **File Line Memos**: Attach notes to specific lines in files
- **Private & Shared Memos**: Choose whether memos are private to your local repository or shared with your team
- **Rich Search**: Find memos by author, commit, file, or visibility
- **Git Log Integration**: View memos inline with your git log

## Important Note
- **To truly use package functionality, generate a public age key and place in trust.yml. these keys are your collaborators**
- **To whom you want to send some note**

## Installation

### Prerequisites

- Python 3.9 or higher
- Git repository

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/<your-username>/commit-memory.git
   cd commit-memory
   ```

2. Create and activate a virtual environment:

   | OS / Shell      | Command                                  |
   |-----------------|------------------------------------------|
   | macOS / Linux   | `python -m venv .venv && source .venv/bin/activate` |
   | Windows – PowerShell | `python -m venv .venv && .\.venv\Scripts\Activate.ps1` |
   | Windows – cmd   | `python -m venv .venv && .venv\Scripts\activate.bat` |
   | Git Bash (Win)  | `python -m venv .venv && source .venv/bin/activate` |

3. Install the package:
   ```
   pip install -e .
   ```

   This will install the package in development mode with all required dependencies.

## Private vs. Shared Memos

Commit Memory supports two types of memos:

- **Private Memos** (default): Stored in `.commit-memos.private.json`, these memos are only visible to you and aren't typically committed to the repository.
- **Shared Memos**: Stored in `.commit-memos.shared.json`, these memos can be committed to the repository and shared with your team.

To create a shared memo, use the `--shared` flag with the `add` command.

## Usage Examples

### Adding Memos

```bash
# Add a private memo to the current commit (HEAD)
cm add --memo "This refactoring improves performance by 30%"

# Add a private memo to a specific commit
cm add --commit abc1234 --memo "Fixed a critical bug in the authentication flow"

# Add a shared memo to a specific commit (visible to the team when committed)
cm add --commit abc1234 --shared --memo "Team: we should revisit this approach in Q3"

# Add a memo to line 42 of file.py at a specific commit
cm add file.py 42 --commit abc1234 --memo "This was changed to fix issue #123"

# Add a memo to line 42 of file.py at the current commit
cm add file.py 42 --memo "This algorithm has O(n) complexity, be careful with large inputs"

# Add notes for intended collaborator for HEAD
cm add --commit HEAD --memo "silence" --shared --to alice,ilia

# or for specific commit
cm add --commit <commit_id> --memo "silence" --shared --to alice,ilia

```

### Viewing Memos

```bash
# Show all memos for a specific commit
cm show abc1234

# Show a rich-formatted git log with all memos inline
cm log

# Show only the last 5 commits
cm log --max 5

# Show the first page of commits (with default page size)
cm log --page 1

# Show the first page with 2 commits per page
cm log --page 1 --page-size 2
```

### Searching Memos

```bash
# Search by author (partial name matching)
cm search --author "John"
# or
cm search -auth "John"

# Search by commit
cm search --commit abc1234
# or
cm search -c abc1234

# Search by file path
cm search --file "src/components/Button.js"
# or
cm search -f "src/components/Button.js"

# Search by visibility (private or shared)
cm search --visibility "shared"
# or
cm search -vs "shared"

# Limit search results
cm search --author "John" --max 10

# Paginate search results
cm search --author "John" --page 1 --page-size 5
```

### Updating Memos

```bash
# Update a commit memo at index 0
cm update --commit abc1234 --index 0 --memo "Updated explanation of the change"

# Update a file memo at index 0
cm update --commit abc1234 --file --index 0 --memo "Updated note about this code"

or you can also skip using -memo and just type in terminal
```

### Deleting Memos

```bash
# Delete a commit memo at index 0
cm delete --commit abc1234 --index 0

# Delete a file memo at index 0
cm delete --commit abc1234 --file --index 0

# Delete all in commit_memos
cm delete --all

# Delete on files side
cm delete --file --all

```

### Pull/ Fetch Notes
```bash
# Fetch memo notes and index them into the local store so show/log look up to date.
cm pull

```

### Push Notes
```bash

git add .commit-memos/shared
git commit -m "add shared memo blob"
git push
git push origin refs/notes/memos

```


### Groups
```bash

# to create a group use command
cm group create <groupName> --members <person1>,<person2> ...

# This creates an empty group with groupName as indicated
cm group create <groupName>

# Add members to a group
cm group add <groupName> --members <person1>,<person2> ...

# Remove members from a group
cm group rm <groupName> --members <person1>

# List all groups and their members.
cm group list

# Show one group's members.
cm group show <groupName>


# Add a shared commit memo to every member of the ‘dev’ group
cm add -c <commit_id> -m "Heads up: migrating DB on Monday" --shared --group dev

# Mix users and groups
cm add -c <commit_id> -m "Pager rotation notes" --shared --group oncall --to alice

# File+line shared memo to team-infra
cm add src/app.py 120 -c <commit_id> -m "Check for None here" --shared --group team-infra
```

### Steps
```bash

1. # Get public keys
## Linux / MacOS
mkdir -p ~/.config/age
age-keygen -o ~/.config/age/key.txt
# show the public recipient to share:
age-keygen -y ~/.config/age/key.txt

## Windows (PowerShell)
New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\age" | Out-Null
age-keygen -o "$env:USERPROFILE\.config\age\key.txt"
# print the public recipient:
age-keygen -y "$env:USERPROFILE\.config\age\key.txt"

2. # Add to trust.yml file
cm trust <name> --age <public_key>

3. # Make a shared memo to Alice (as an example)
cm add --commit <commit_id> --memo "silence" --shared --to alice

4. # Upload
git add .commit-memos/shared
git commit -m "add shared memo blob"
git push
git push origin refs/notes/memos

5. # Fetch memos/notes
cm pull

```
### Log on a specific branch
```bash

cm log --branch <branchName>

```

## Contributing

Contributions are welcome! Please check out our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started.

### Development Workflow

For developers working on Commit Memory, we use pre-commit hooks to ensure code quality and consistency:

1. Install development dependencies:
   ```
   pip install pre-commit pytest
   ```

2. Set up pre-commit hooks:
   ```
   pre-commit install
   ```

This will automatically run the following checks before each commit:
- Code formatting with Black and isort
- Linting with Ruff
- Type checking with mypy
- Various file checks (trailing whitespace, YAML/TOML validation, etc.)

## License

This project is licensed under the MIT License—see the LICENSE file for details.
