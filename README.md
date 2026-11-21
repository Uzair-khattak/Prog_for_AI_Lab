# Programming for AI – Mid-Term Lab (Open-Book) · Complete Solution Package

> **Using VS Code? Read `VSCODE_GUIDE.md` first** – the folder is pre-configured (cmd terminal, interpreter, tasks).

Everything is organised so you can run it **step by step**. Follow the numbers.

```
Prog_for_AI_Lab/
├── README.md                 <- this guide
├── requirements.txt          <- all packages (fresh environment)
├── setup_env.bat / .sh       <- creates the environment + installs packages
├── check_env.py              <- checks packages and datasets
├── data/                     <- YOU put the datasets here (4 sub-folders)
├── src/                      <- shared Python modules (from-scratch regression, helpers, report builder)
├── Q1/  (3 notebooks)        <- Multiple linear regression
├── Q2/  (3 notebooks)        <- Random forests (Heart Disease + Intel Images)
├── Q3/  (5 notebooks + api/ + app/)  <- Adult Income: baseline, TPOT, FastAPI, Streamlit, deployment
├── results/                  <- figures + json produced by the notebooks (do not edit)
├── models/                   <- saved models (Q3)
└── reports/                  <- Build_Reports.ipynb -> Q1_Report.docx, Q2_Report.docx, Q3_Report.docx
```

Report format: **Word (.docx)**. It is the better choice here because the reports need your scanned handwritten pages, many figures and tables, and you will edit the text before submission – Word handles this easily and can be exported to PDF in one click.

---

## STEP 0 – One-time setup (≈ 10–15 min)

1. Install **Python 3.11** from python.org if you do not have it (tick *“Add python.exe to PATH”*). TPOT supports Python 3.10–3.13, Python 3.14 will **not** work.
2. Open the folder `Desktop\Prog_for_AI_Lab` and copy this whole package into it.
3. **Double-click `setup_env.bat`** (or in a terminal: `setup_env.bat`).
   It creates a **fresh virtual environment `venv`**, installs all packages from `requirements.txt` and registers the Jupyter kernel *“Python (Prog_for_AI_Lab)”*.
4. Every time you work, open a terminal in the project folder and run:
   ```
   venv\Scripts\activate
   jupyter lab
   ```
   (Mac/Linux: `source venv/bin/activate`). If you use VS Code, choose the interpreter `venv\Scripts\python.exe` / kernel *Python (Prog_for_AI_Lab)*.
5. Check: `python check_env.py` – all packages must say **OK**.

## STEP 1 – Download the datasets (manual)

| Question | Dataset | Put it in | Note |
|---|---|---|---|
| Q1 | *Multiple linear regression dataset* – click the link in the exam paper | `data/q1/` | any `.csv` (last column = target; otherwise set `TARGET_COL` in notebook 02) |
| Q2 | Heart Disease UCI (Kaggle, `heart_disease_uci.csv` or `heart.csv`) | `data/q2_heart/` | |
| Q2 | Intel Image Classification (Kaggle) – unzip | `data/q2_intel/` | must contain `seg_train` and `seg_test` folders (inside, one folder per class) |
| Q3 | Adult Income (`adult.csv` from Kaggle/UCI) | `data/q3_adult/` | optional: if the folder is empty the notebook downloads it from OpenML |

Run `python check_env.py` again – the dataset lines must say **OK**.

## STEP 2 – Run the notebooks in THIS order

Open each notebook, choose the kernel **Python (Prog_for_AI_Lab)**, then **Run → Run All Cells**. Wait until a notebook finishes before opening the next.

| # | Notebook | What it does | Time |
|---|---|---|---|
| 1 | `Q1/01_Q1_Derivation.ipynb` | typed derivation + numerical gradient check | 1 min |
| 2 | `Q1/02_Q1_Implementation.ipynb` | scaling, cost, gradient descent, convergence plot, θ, comparison with scikit-learn (MSE) | 1 min |
| 3 | `Q1/03_Q1_Experiments.ipynb` | experiments on α, scaling, λ, under/over-fitting | 1 min |
| 4 | `Q2/01_Q2_Heart_Disease.ipynb` | tree-count sweep, DT vs RF, SVM, tuning, CV | 2–5 min |
| 5 | `Q2/02_Q2_Intel_Images.ipynb` | same experiments on images | 10–25 min |
| 6 | `Q2/03_Q2_Comparative_Analysis.ipynb` | combined comparison, framework figure, end-to-end analysis | 1 min |
| 7 | `Q3/01_EDA.ipynb` | exploratory data analysis | 1 min |
| 8 | `Q3/02_Baseline_Model.ipynb` | Logistic Regression baseline (+ RF reference) | 1–2 min |
| 9 | `Q3/03_AutoML_TPOT.ipynb` | **TPOT search – `TPOT_MINUTES = 30`** (run it last of the day / overnight) | 30–60 min |
| 10 | `Q3/04_Comparison_and_Save_Model.ipynb` | compares models, feature importance, saves `models/best_model.joblib` | 2–3 min |
| 11 | `Q3/05_Deployment_Prep.ipynb` | tests the API in-process and builds `Q3/deploy_hf/` | 1 min |
| 12 | `reports/Build_Reports.ipynb` | creates the three Word reports | 1 min |

**Tip for Q3-03:** first run it with `TPOT_MINUTES = 2` as a dry run to be sure it works, then set it back to 30 (or up to 60) for the final run. Keep the laptop plugged in and awake.

## STEP 3 – Run the API and the web app locally

Open **two terminals** in the project folder (both with `venv` activated):

```
# terminal 1 – the REST API (docs at http://127.0.0.1:8000/docs)
uvicorn main:app --port 8000 --app-dir Q3/api

# terminal 2 – the Streamlit user interface (http://localhost:8501)
streamlit run Q3/app/streamlit_app.py
```
Try a few inputs in the app. Take **screenshots** (app + `/docs` page) and save them in `reports/screenshots/`.

## STEP 4 – Manual work you must do yourself

1. **Handwritten derivation (Q1 Part A/C)** – write every step of the derivation on paper (use notebook `Q1/01_Q1_Derivation.ipynb` as your guide: ∂J/∂θ₀, ∂J/∂θⱼ for j ≥ 1, component form, vector form of the update). Photograph/scan the pages clearly and save them as `reports/handwritten_q1/page1.jpg`, `page2.jpg`, …
2. **Read Breiman’s “Random Forests” (2001) paper** (Q2) – at least the abstract, Sections 1–2 and the part on strength/correlation. Then rewrite the Part A text of the report in your own words.
3. **GitHub repository (Q2)** – create a public repo, upload the project (the `.gitignore` already excludes data and big files), and put the link in `reports/report_config.json` → `"github_url"`:
   ```
   git init && git add . && git commit -m "Programming for AI mid-term lab"
   git branch -M main && git remote add origin https://github.com/<you>/<repo>.git && git push -u origin main
   ```
4. **Deploy Q3 (step 9)** – follow the instructions at the end of `Q3/05_Deployment_Prep.ipynb` (Hugging Face Space → *Docker* → upload the content of `Q3/deploy_hf/`). Put the live link in `reports/report_config.json` → `"live_url"`.
5. **Fill in `reports/report_config.json`** (name, roll number, links).
6. **Rewrite the discussion paragraphs** in the reports in your own words (they are drafts generated from your real numbers). Check every figure and table.
7. **Q1 notebooks:** if your dataset’s target is not the last column or it has ID columns, set `TARGET_COL` / `DROP_COLS` in notebook 02 **and** 03 (same values).

Then run `reports/Build_Reports.ipynb` again to refresh the reports with the scans, screenshots and links.

## STEP 5 – Before the evaluation (week of 23 November)

Bring the laptop with: this whole folder **with all notebooks already executed (outputs visible)**, `results/`, `models/`, the three Word reports, the running API/app (test it works offline), and the live link.

Be ready to explain (examples of questions):
* **Q1:** Why is θ₀ not regularised? How do you get from ∂J/∂θⱼ to the update rule? Why does scaling speed up gradient descent? What happens if α is too big? Why does your MSE differ slightly from scikit-learn’s? What is weight decay?
* **Q2:** What are strength and correlation (Breiman’s bound)? Why does adding trees not over-fit? What is bagging / OOB error? Why is the single tree unstable? Why PCA before the SVM? Why only 32×32 pixels?
* **Q3:** Why ROC-AUC/F1 instead of accuracy? How does TPOT search (genetic programming)? Why is preprocessing inside the pipeline (no leakage)? What is permutation importance? How does Streamlit talk to FastAPI? Why pin the library versions when deploying a pickle?

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: pkg_resources` when importing TPOT | `pip install "setuptools<81"` (already in requirements.txt) |
| TPOT hangs or errors with parallel jobs on Windows | the notebook automatically retries with `n_jobs=1`; or set `N_JOBS = 1` |
| `FileNotFoundError ... Download the dataset` | the dataset is missing in the right `data/` sub-folder (run `check_env.py`) |
| Intel notebook is too slow | set `MAX_PER_CLASS = 500` and `SWEEP_SEEDS = [0]` (state this in the report if you use it) |
| Notebook uses the wrong Python | choose kernel *Python (Prog_for_AI_Lab)* (or the `venv` interpreter) |
| `Project root not found` | open the notebook from inside the `Prog_for_AI_Lab` folder |
| Streamlit says “Cannot reach the API” | start the API first (terminal 1) |
| Hugging Face build fails | open the *Logs* tab; make sure all files from `Q3/deploy_hf/` (including `models/`) were uploaded |
