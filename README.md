# Flask Starter

A minimal Flask starter project.

## Requirements
- Python 3.12+ (or latest installed)

## Quick start (PowerShell)

```powershell
# create a virtual environment
python -m venv .venv

# activate the venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# install dependencies
pip install -r requirements.txt

# run the app
python run.py
```

Open http://127.0.0.1:5000/ in your browser. The root path returns a JSON message.

## Tests

With the venv activated:

```powershell
pip install -r requirements.txt
pytest -q
```
