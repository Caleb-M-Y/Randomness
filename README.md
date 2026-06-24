# Randomness
making this late at night to mess w AI

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


TO ACTIVATE PYTHON 3.12.13 VENV 
& ".\.venv312\Scripts\Activate.ps1"