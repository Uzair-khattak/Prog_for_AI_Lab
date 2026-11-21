# VS Code guide (Windows + Command Prompt terminal)

The folder already contains a `.vscode/` configuration, so VS Code is pre-set to:
* use **Command Prompt (cmd)** as the integrated terminal,
* use the interpreter `venv\Scripts\python.exe`,
* run notebooks with the right working folder and find `src/` for imports,
* offer ready-made **Tasks** (setup, check, start API, start Streamlit) and **Debug** configurations.

## 1. Open the folder
1. Start VS Code → **File → Open Folder…** → choose `Desktop\Prog_for_AI_Lab` (the folder that directly contains `README.md` and `requirements.txt`).
2. Click **Yes, I trust the authors** if asked.
3. Bottom-right: **Install** the recommended extensions (Python, Pylance, Jupyter). If no popup appears: `Ctrl+Shift+X`, search and install **Python** and **Jupyter** (Microsoft).

## 2. Open the terminal and check it is cmd
`Ctrl+`` (backtick) opens the terminal. The prompt must look like `C:\Users\you\Desktop\Prog_for_AI_Lab>`.
If it says `PS C:\...>` it is PowerShell: click the small arrow next to **+** in the terminal panel → **Command Prompt**.

## 3. Create the fresh environment (one time)
Choose ONE way:
* **Task:** `Ctrl+Shift+P` → type `Tasks: Run Task` → **1) Setup environment (create venv + install packages)**
* **or type in the terminal:** `setup_env.bat`

Wait 5–15 min until you see `Done.` The new folder `venv` appears.

## 4. Select the interpreter / kernel (important)
1. `Ctrl+Shift+P` → **Python: Select Interpreter** → pick `.\venv\Scripts\python.exe` (Recommended / venv).
   If it is not listed: **Enter interpreter path… → Find…** → `Prog_for_AI_Lab\venv\Scripts\python.exe`.
2. Open any notebook (e.g. `Q1/01_Q1_Derivation.ipynb`). Top-right click **Select Kernel → Python Environments → venv (Python 3.x)**.
   VS Code remembers it per notebook – repeat once for each notebook the first time.
3. Open a **new** terminal (trash-can the old one, then `Ctrl+Shift+``). The prompt should start with `(venv)`.

## 4b. Check everything
`Ctrl+Shift+P` → Tasks: Run Task → **2) Check environment and datasets**
(or `python check_env.py` in the terminal). All packages must say OK; dataset lines turn OK after the next step.

## 5. Put the datasets in `data/` (drag and drop in the VS Code Explorer)
`data/q1` · `data/q2_heart` · `data/q2_intel` (with `seg_train` and `seg_test`) · `data/q3_adult`. Run the check task again.

## 6. Run the notebooks (in this order)
Open the notebook → click **Run All** (top toolbar). Wait until every cell has a number `[n]` and no red error.

| Order | Notebook |
|---|---|
| 1–3 | `Q1/01_…`, `02_…`, `03_…` |
| 4–6 | `Q2/01_Heart…`, `02_Intel…`, `03_Comparative…` |
| 7–11 | `Q3/01_EDA`, `02_Baseline`, `03_AutoML_TPOT`, `04_Comparison_and_Save_Model`, `05_Deployment_Prep` |
| 12 | `reports/Build_Reports.ipynb` |

Useful VS Code notebook tips
* A cell failed? Fix it, then **Restart** (toolbar) → **Run All** so everything runs from a clean state.
* Long outputs are collapsed: click “Open in text editor / scrollable element” on the output.
* `03_AutoML_TPOT`: set `TPOT_MINUTES = 2` for a dry run, then 30. **Do not close VS Code or let the laptop sleep** while it runs (Windows: Settings → Power → Screen and sleep → Never while plugged in).
* Do not edit the same notebook in two windows.

## 7. Run the API and the Streamlit app (after Q3 notebooks 01–05)
* `Ctrl+Shift+P` → Tasks: Run Task → **5) Start API + Streamlit together** (two terminals open side by side), or run tasks 3 and 4 separately.
* API docs: <http://127.0.0.1:8000/docs> · App: <http://localhost:8501> (Ctrl+click the links in the terminal).
* Stop a server: click in its terminal and press `Ctrl+C`.
* Manual commands (if you prefer): `venv\Scripts\python -m uvicorn main:app --port 8000 --app-dir Q3/api` and `venv\Scripts\python -m streamlit run Q3/app/streamlit_app.py`.
* Debugging: **Run and Debug** (`Ctrl+Shift+D`) → *Debug FastAPI (Q3 API)* → green play button (breakpoints work).

## 8. Reports and manual items
1. Edit `reports/report_config.json` (name, roll number, links).
2. Put handwritten scans in `reports/handwritten_q1/` and screenshots in `reports/screenshots/` (drag & drop).
3. Run `reports/Build_Reports.ipynb` → the `.docx` files appear in `reports/` (right-click → *Reveal in File Explorer* → open in Word).

## 9. Git / GitHub from VS Code (Q2 needs a GitHub link)
1. Install Git for Windows if needed (git-scm.com).
2. Source Control icon (`Ctrl+Shift+G`) → **Initialize Repository** → type a message → **Commit**.
3. **Publish Branch / Publish to GitHub** → sign in → choose *public repository*. Copy the URL into `reports/report_config.json`.
(`.gitignore` already skips `venv`, datasets and big files.)

## Common VS Code problems
| Problem | Fix |
|---|---|
| Terminal shows `PS ...` and activation errors | switch the terminal profile to **Command Prompt** (section 2) |
| Kernel list does not show `venv` | run the Setup task again, then `Ctrl+Shift+P` → *Developer: Reload Window*, or use *Select Another Kernel → Python Environments → Enter interpreter path* |
| `ModuleNotFoundError` in a notebook | the wrong kernel is selected (must be `venv`) |
| `Project root not found` | you opened a parent/other folder – use **File → Open Folder** on `Prog_for_AI_Lab` itself |
| Import squiggles for `lab_utils` / `q3_common` | harmless; `src` is already in `python.analysis.extraPaths` – reload the window |
| Task says `setup_env.bat is not recognized` | the terminal is not in the project folder – open the folder correctly (section 1) |
