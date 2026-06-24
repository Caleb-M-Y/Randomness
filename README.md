# Randomness
making this late at night to mess w AI

## Cross-Machine Setup

This repo should sync source code only. Do not commit or copy virtual environments between machines.

Tracked locally, ignored by git:
- `.venv312/`
- `.venv/`
- `__pycache__/`

## Chess Project Setup (Windows)

1. Clone the repository and open it in VS Code.
2. Create a Python 3.12 virtual environment.
3. Install dependencies from requirements.
4. Run the game.

```powershell
git clone <your-repo-url>
cd Randomness
py -3.12 -m venv .venv312
.\.venv312\Scripts\Activate.ps1
pip install -r games/requirements.txt
python games/chess_pygame.py
```

Notes:
- Python 3.12 is recommended for pygame compatibility.
- If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

To activate the venv later:

```powershell
& ".\.venv312\Scripts\Activate.ps1"
```

If you switch between PC and laptop:
1. Pull the repo.
2. Recreate `.venv312` on that machine if it does not exist or if `python` points to a missing path.
3. Run `pip install -r games/requirements.txt`.

Do not push `.venv312` changes. Virtual environments store absolute paths and are machine-specific.