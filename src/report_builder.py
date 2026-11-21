"""Builds the three Word reports (Q1, Q2, Q3) from the results/ folder (numbers, tables, figures).
Texts marked as 'draft' are generated from your real results – read them, understand them and rewrite
them in your own words before submitting."""
import json
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = None
for _p in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
    if (_p / "requirements.txt").exists():
        ROOT = _p
        break
RES, REP = ROOT / "results", ROOT / "reports"


def _load(path, default=None):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def config():
    return _load(REP / "report_config.json", {}) or {}


# --------------------------------------------------------------------------- docx helpers
def new_doc(title, subtitle):
    d = Document()
    for s in d.sections:
        s.left_margin = s.right_margin = Inches(0.9)
        s.top_margin = s.bottom_margin = Inches(0.8)
    st = d.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    for lvl, size in [(1, 16), (2, 13), (3, 11.5)]:
        h = d.styles[f"Heading {lvl}"]
        h.font.name = "Calibri"
        h.font.size = Pt(size)
        h.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    c = config()
    t = d.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run(title)
    r.bold = True
    r.font.size = Pt(22)
    r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    s = d.add_paragraph()
    s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s.add_run(subtitle).font.size = Pt(13)
    info = d.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.add_run(f"{c.get('course', '')} · Mid-Term Lab (Open-Book) · Teacher: {c.get('teacher', '')}\n"
                 f"Student: {c.get('student_name', '')} · Roll No: {c.get('roll_number', '')}").font.size = Pt(10.5)
    return d


def para(d, text, bold=False, italic=False, size=None):
    p = d.add_paragraph()
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    if size:
        r.font.size = Pt(size)
    p.paragraph_format.space_after = Pt(6)
    return p


def bullets(d, items):
    for it in items:
        d.add_paragraph(it, style="List Bullet")


def _shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def table(d, rows, columns=None, fmt=None, font=9):
    """rows: list of dicts or DataFrame"""
    df = pd.DataFrame(rows) if not isinstance(rows, pd.DataFrame) else rows
    if columns:
        df = df[columns]
    t = d.add_table(rows=1, cols=len(df.columns))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, c in enumerate(df.columns):
        cell = t.rows[0].cells[i]
        cell.text = ""
        r = cell.paragraphs[0].add_run(str(c))
        r.bold = True
        r.font.size = Pt(font)
        _shade(cell, "DCE6F1")
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for i, v in enumerate(row):
            if isinstance(v, float):
                txt = f"{v:.4g}" if fmt is None else fmt(v)
            else:
                txt = "" if v is None else str(v)
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(txt).font.size = Pt(font)
    d.add_paragraph()
    return t


def figure(d, path, caption, width=6.2):
    path = Path(path)
    if path.exists():
        d.add_picture(str(path), width=Inches(width))
        d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        para(d, f"[MISSING FIGURE: {path.name} – run the notebook that creates it]", italic=True)
    p = para(d, caption, italic=True, size=9.5)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def images_from(d, folder, caption_prefix, width=6.0):
    exts = {".jpg", ".jpeg", ".png"}
    files = sorted(f for f in Path(folder).glob("*") if f.suffix.lower() in exts) if Path(folder).exists() else []
    if not files:
        para(d, f"[INSERT YOUR SCANNED / PHOTOGRAPHED IMAGES HERE – put them in {Path(folder).relative_to(ROOT)} and re-run the builder]",
             bold=True)
    for i, f in enumerate(files, 1):
        d.add_picture(str(f), width=Inches(width))
        d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        para(d, f"{caption_prefix} {i}", italic=True, size=9.5).alignment = WD_ALIGN_PARAGRAPH.CENTER


# =========================================================================== Q1
def build_q1():
    R = _load(RES / "q1" / "results.json")
    E = _load(RES / "q1" / "experiments.json")
    if not R or not E:
        raise FileNotFoundError("Run the Q1 notebooks first (results/q1/*.json missing).")
    f = RES / "q1"
    cfg, ds = R["config"], R["dataset"]
    d = new_doc("Question 1 – Multiple Linear Regression", "Derivation, implementation from scratch and experiments")

    d.add_heading("1. Problem statement", 1)
    para(d, "The task is to derive, implement and experiment with multiple linear regression with L2 regularisation. "
            "The hypothesis is h(x) = θ0 + θ1x1 + … + θnxn and the cost function is "
            "J(θ) = 1/(2m)·[ Σ (h(x⁽ⁱ⁾) − y⁽ⁱ⁾)² + λ Σⱼ≥₁ θⱼ² ] (the intercept θ0 is not regularised).")

    d.add_heading("2. Part A – Mathematical derivation", 1)
    para(d, "Handwritten derivation (scanned pages):", bold=True)
    images_from(d, REP / "handwritten_q1", "Handwritten derivation – page")
    para(d, "Typed summary of the result:", bold=True)
    bullets(d, [
        "∂J/∂θ0 = (1/m) Σ (h(x⁽ⁱ⁾) − y⁽ⁱ⁾)   (because x0 = 1 and the regularisation term does not contain θ0).",
        "∂J/∂θj = (1/m) [ Σ (h(x⁽ⁱ⁾) − y⁽ⁱ⁾) xj⁽ⁱ⁾ + λ θj ]   for j ≥ 1.",
        "Component form: θ0 := θ0 − (α/m) Σ (h − y);  θj := θj (1 − αλ/m) − (α/m) Σ (h − y) xj  (j ≥ 1).",
        "Vector form: θ := θ − (α/m) [ Xᵀ(Xθ − y) + λ θ̃ ], where θ̃ = [0, θ1, …, θn]ᵀ.",
        "Verification: the analytic gradient was compared with a numerical (central-difference) gradient and matched to about 1e-9 "
        "(notebook 01_Q1_Derivation).",
    ])

    d.add_heading("3. Part B – Implementation and choices", 1)
    para(d, f"Dataset: {ds['file']} – {ds['rows']} rows, {ds['n_features']} features ({', '.join(ds['features'])}), target = {ds['target']}. "
            f"Split: {ds['n_train']} training / {ds['n_test']} test examples (random_state = {cfg['seed']}). Everything (scaling, hypothesis, cost, "
            "gradient descent) was implemented from scratch with NumPy; scikit-learn was used only for the train/test split and for the comparison model.")
    d.add_heading("Explanation of the choices", 2)
    sc_name = "standardisation (z-score)" if cfg["scaling"] == "standard" else "min-max scaling"
    sc_rows = {r["scaling"]: r for r in E["scaling"]}
    s_it = sc_rows.get("standard", {}).get("iterations to reach 1% of optimum")
    n_it = sc_rows.get("none", {}).get("iterations to reach 1% of optimum")
    bullets(d, [
        f"Feature scaling – {sc_name}: the features have very different ranges; with scaling every feature has comparable magnitude, the cost surface is "
        f"round instead of elongated and a much larger learning rate can be used. Scaling parameters are learned on the training set only (no leakage). "
        f"In our experiment standardisation needed {s_it} iterations to get within 1 % of the optimum, without scaling more than {n_it if n_it != '>5000' else '5000'} were needed.",
        f"Learning rate α = {cfg['alpha']}: chosen from the learning-rate experiment – it converges quickly and smoothly and is safely below the value at which the cost diverges.",
        f"Regularisation λ = {cfg['lambda']}: a small value that stabilises the weights without noticeably biasing them (see the λ experiment).",
        f"Iterations: {cfg['n_iters']} – the cost curve is flat long before that (final cost {R['gd']['final_cost']:.6g}).",
    ])

    d.add_heading("4. Results", 1)
    figure(d, f / "convergence.png", "Figure 1 – Convergence curve (cost vs iterations), linear and log scale.")
    para(d, f"The cost decreased from {R['gd']['initial_cost']:.6g} to {R['gd']['final_cost']:.6g}. The final θ is identical to the closed-form solution "
            f"(maximum difference {R['gd']['max_diff_vs_closed_form']:.2e}), which proves that gradient descent converged to the true minimum.")
    para(d, "Final parameter values θ (in scaled space as learned, and converted back to original units for comparison):", bold=True)
    rows = [{"parameter": k, "θ (scaled space)": R["theta_scaled"][k], "θ (original units)": R["theta_original_units"][k],
             "θ λ=0 (original)": R["theta_lambda0_original_units"][k], "scikit-learn": R["theta_sklearn_original_units"][k]} for k in R["theta_scaled"]]
    table(d, rows)
    para(d, "Mean Squared Error (MSE) – ours vs scikit-learn:", bold=True)
    table(d, [{"model": k, "train MSE": v["train_mse"], "test MSE": v["test_mse"], "test R²": v["test_r2"]} for k, v in R["metrics"].items()])
    figure(d, f / "comparison.png", "Figure 2 – Predicted vs actual values on the test set and test-MSE comparison.")

    d.add_heading("5. Experiments", 1)
    figure(d, f / "exp_learning_rate.png", "Figure 3 – Effect of the learning rate α.")
    table(d, E["learning_rate"])
    figure(d, f / "exp_scaling.png", "Figure 4 – Feature scaling vs convergence speed (each method with its largest stable α).")
    table(d, E["scaling"])
    figure(d, f / "exp_lambda.png", "Figure 5 – Effect of λ on train/test MSE and on the size of the weights.")
    table(d, E["lambda"])
    figure(d, f / "exp_overfit.png", "Figure 6 – Over-fitting stress test (polynomial features, small training set).")
    st = E["overfit_stress_test"]
    para(d, f"Stress test set-up: polynomial degree {st['degree']}, {st['n_train']} training examples, {st['n_params']} parameters.")
    table(d, st["rows"])

    d.add_heading("6. Discussion (draft – rewrite in your own words)", 1)
    lr = E["learning_rate"]
    div = [r["alpha"] for r in lr if r["status"] == "DIVERGED"]
    slow = lr[0]
    best_lam = min(E["lambda"], key=lambda r: r["test MSE"])
    big_lam = E["lambda"][-1]
    lam0 = E["lambda"][0]
    s0 = st["rows"][0]
    sbest = min(st["rows"], key=lambda r: r["test MSE"])
    m = R["metrics"]
    ours = m[[k for k in m if k.startswith("Ours (GD, λ=") and "λ=0" not in k][0]]
    ours0, skm = m["Ours (GD, λ=0)"], m["scikit-learn LinearRegression"]
    para(d, "Learning rate. ", bold=True)
    para(d, f"A very small α (= {slow['alpha']}) is stable but slow – after 300 iterations the cost was still {slow['final cost after 300 it.']:.4g}. "
            f"Moderate values (about 0.03–1 for scaled data) reach the minimum within a few hundred iterations. "
            + (f"Values of α ≥ {min(div)} made the cost explode (divergence), because the steps overshoot the minimum. " if div else "")
            + "The learning rate must therefore be large enough to be fast and small enough to be stable.")
    para(d, "Feature scaling. ", bold=True)
    para(d, f"Scaling changes the shape of the cost surface. Without scaling the largest stable learning rate is tiny "
            f"({sc_rows['none']['largest stable alpha']:.2g}) and the algorithm needs {sc_rows['none']['iterations to reach 1% of optimum']} iterations, "
            f"with min-max scaling {sc_rows['minmax']['iterations to reach 1% of optimum']} and with standardisation only "
            f"{sc_rows['standard']['iterations to reach 1% of optimum']}. The final solution is the same, only the speed differs.")
    para(d, "Regularisation λ and under-/over-fitting. ", bold=True)
    para(d, f"On the original data a linear model has few parameters, so it is not over-fitted: with λ = 0 the test MSE is {lam0['test MSE']:.4g}, the best λ ({best_lam['lambda']}) gives "
            f"{best_lam['test MSE']:.4g}. When λ is far too large (λ = {big_lam['lambda']}) all weights are pushed towards 0, train and test MSE rise to "
            f"{big_lam['train MSE']:.4g} / {big_lam['test MSE']:.4g} – this is UNDER-fitting (high bias). "
            f"In the stress test (many polynomial features, few examples) λ = 0 gives train MSE {s0['train MSE']:.3g} but test MSE {s0['test MSE']:.4g} – clear OVER-fitting (high variance); "
            f"the best λ ({sbest['lambda']}) reduces the test MSE to {sbest['test MSE']:.4g}.")
    para(d, "Comparison with scikit-learn. ", bold=True)
    para(d, f"With λ = 0 our gradient-descent model reaches test MSE {ours0['test_mse']:.6g} versus {skm['test_mse']:.6g} for LinearRegression – practically identical, and the "
            f"parameters coincide. With λ = {cfg['lambda']} our test MSE is {ours['test_mse']:.6g}; the small difference is the (intended) bias introduced by regularisation. "
            f"scikit-learn is faster because it solves the least-squares problem directly instead of iterating.")

    d.add_heading("7. Conclusion", 1)
    para(d, "The derived gradients were verified numerically, the from-scratch implementation converges to the closed-form optimum and matches scikit-learn, "
            "and the experiments show how α, feature scaling and λ affect convergence and generalisation.")
    out = REP / "Q1_Report.docx"
    d.save(out)
    return out


# =========================================================================== Q2
BREIMAN = [
    "Leo Breiman (2001) defines a random forest as a collection of tree-structured classifiers h(x, Θk), where the Θk are independent, identically distributed random vectors "
    "and every tree casts one vote for the most popular class at input x.",
    "Main theoretical claim: as the number of trees grows, the generalisation error converges almost surely to a limit (law of large numbers), so adding trees does not cause over-fitting.",
    "Upper bound: PE* ≤ ρ̄ (1 − s²) / s², where s is the strength of the individual trees (expected margin) and ρ̄ is the mean correlation between the trees' raw margin functions. "
    "A good forest has strong trees that are weakly correlated.",
    "Randomness is injected by bagging (each tree is grown on a bootstrap sample) and by random feature selection at each node (Forest-RI) or random linear combinations of features (Forest-RC).",
    "Out-of-bag (OOB) samples give internal, unbiased estimates of the error, strength, correlation and variable importance without a separate test set.",
    "Empirically the forests are as accurate as AdaBoost, more robust to noise in the labels, faster, and simple to parallelise.",
]
PART_A = [
    ("Ingredient 1 – the strength of the individual trees.",
     "Strength measures how much better than random guessing a single tree is, i.e. how often it votes for the correct class by a clear margin. "
     "If the individual trees are weak (for example because at every split only an uninformative subset of features is allowed), the vote of many weak trees is still poor: "
     "the bound PE* ≤ ρ̄(1−s²)/s² gets worse as s approaches 0. Strong trees mean a high expected margin, so for most inputs the majority of the trees point to the correct class "
     "and the ensemble error is small."),
    ("Ingredient 2 – low correlation between the trees.",
     "If all trees make the same mistakes, averaging them gives nothing. For N predictors, each with variance σ² and pairwise correlation ρ, the variance of the average is "
     "ρσ² + (1 − ρ)σ²/N. Increasing N removes only the second term – what remains is ρσ², so the only way to improve further is to make the trees less correlated. "
     "Random forests do this by training every tree on a different bootstrap sample and by letting each split see only a random subset of the features, so the trees make different, "
     "partly independent errors that cancel in the vote."),
    ("How the two interact (trade-off).",
     "Using fewer random features per split (smaller m) lowers the correlation but also lowers the strength of each tree; using all features gives strong but highly correlated trees (bagging). "
     "The best forest balances the two, which is why max_features is the most important tuning parameter."),
    ("Why combining many trees improves stability and performance.",
     "A single fully-grown tree has low bias but very high variance – a small change of the training data gives a different tree. Averaging many de-correlated high-variance trees keeps the low bias "
     "while the variance shrinks, so predictions become smoother and more repeatable (smaller spread between random seeds) and the test accuracy is higher on average. "
     "Because the error converges when the number of trees grows, the accuracy curve rises quickly and then flattens instead of turning down – more trees never hurt generalisation, they only cost time."),
]



def _time_phrase(dt, rf, n_feat):
    """Honest wording about training time (a single tree is NOT always faster than a forest)."""
    a, b = dt["train_time_s"], rf["train_time_s"]
    r = b / max(a, 1e-9)
    if r >= 1.2:
        return (f"the forest needed about {r:.0f}x more training time ({b:.3f}s vs {a:.3f}s) because it grows 100 trees instead of one")
    if r <= 0.83:
        return (f"surprisingly, the forest trained {1/r:.1f}x FASTER than the single tree ({b:.1f}s vs {a:.1f}s): an unrestricted tree searches all {n_feat} "
                f"features at every split, whereas each forest split searches only a random subset (about sqrt({n_feat})) and the 100 trees are grown in parallel (n_jobs=-1)")
    return f"training times were similar ({b:.3f}s forest vs {a:.3f}s tree)"


def _end_to_end(H, I):
    out = []
    for R, name, nf in [(H, "Heart Disease", H["dataset"]["n_features_after_encoding"]), (I, "Intel Images", I["dataset"]["n_features"])]:
        g = lambda p, k: next(r for r in R["comparison"] if r["model"].startswith(p))[k]
        dt, rf, sv = g("Decision Tree", "accuracy"), g("Random Forest", "accuracy"), g("SVM", "accuracy")
        best = max([("Decision Tree", dt), ("Random Forest", rf), ("SVM", sv)], key=lambda t: t[1])
        s = pd.DataFrame(R["sweep_summary"])
        out.append(f"{name}: test accuracy Decision Tree {dt:.3f}, Random Forest {rf:.3f}, SVM {sv:.3f}; best = {best[0]}. "
                   f"The forest is {100*(rf-dt):+.1f} percentage points better than the single tree; {_time_phrase(R['dt_vs_rf'][0], R['dt_vs_rf'][1], nf)}. "
                   f"SVM training took {g('SVM', 'train_time_s'):.3f}s. With 1 tree the forest reached {s.test_acc_mean.iloc[0]:.3f} (std {s.test_acc_std.iloc[0]:.3f} over seeds); "
                   f"with {int(s.n_estimators.iloc[-1])} trees {s.test_acc_mean.iloc[-1]:.3f} (std {s.test_acc_std.iloc[-1]:.3f}).")
    return out


def _sweep_fig_table(d, R, prefix, label):
    figure(d, RES / "q2" / f"{prefix}_n_estimators.png", f"Figure – {label}: test accuracy vs number of trees (mean ± std over seeds).")
    s = pd.DataFrame(R["sweep_summary"])
    table(d, s.rename(columns={"test_acc_mean": "test acc (mean)", "test_acc_std": "test acc (std)", "train_acc_mean": "train acc",
                               "oob_acc_mean": "OOB acc", "train_time_mean": "train time (s)"}))


def build_q2():
    H = _load(RES / "q2" / "heart_results.json")
    I = _load(RES / "q2" / "intel_results.json")
    A = _load(RES / "q2" / "analysis_text.json", {})
    if not H or not I:
        raise FileNotFoundError("Run the Q2 notebooks first (results/q2/*.json missing).")
    cfg = config()
    f = RES / "q2"
    d = new_doc("Question 2 – Random Forests", "Breiman (2001) – theory and experiments on Heart Disease and Intel Images")

    d.add_heading("1. Summary of Breiman's main ideas and claims", 1)
    bullets(d, BREIMAN)

    d.add_heading("2. Part A – Why Random Forests work (draft – rewrite in your own words)", 1)
    for head, txt in PART_A:
        para(d, head, bold=True)
        para(d, txt)

    d.add_heading("3. Datasets and preprocessing", 1)
    hd, idd = H["dataset"], I["dataset"]
    para(d, "Heart Disease UCI (tabular, binary classification)", bold=True)
    para(d, f"{hd['rows']} patients, {hd['n_features']} features ({len(hd['numeric_features'])} numeric, {len(hd['categorical_features'])} categorical), "
            f"{hd['missing_values']} missing values; class balance: {hd['class_balance']['no_disease']} healthy vs {hd['class_balance']['disease']} with heart disease. "
            f"Preprocessing: {H['preprocessing']} After encoding there are {hd['n_features_after_encoding']} features; {hd['n_train']} training / {hd['n_test']} test samples.")
    figure(d, f / "heart_eda.png", "Figure – Heart Disease: class balance and correlations.", 6.0)
    para(d, "Intel Image Classification (images, 6 classes)", bold=True)
    para(d, f"Classes: {', '.join(idd['classes'])}. {idd['n_train']} training and {idd['n_test']} test images (official split). Preprocessing: {I['preprocessing']}")
    figure(d, f / "intel_samples.png", "Figure – Intel Images: sample images per class.", 6.2)

    d.add_heading("4. Experiment 1 – number of trees", 1)
    d.add_heading("Heart Disease", 2)
    _sweep_fig_table(d, H, "heart", "Heart Disease")
    d.add_heading("Intel Images", 2)
    _sweep_fig_table(d, I, "intel", "Intel Images")
    figure(d, f / "sweep_both.png", "Figure – Random Forest vs the single tree on both datasets.", 6.0)

    d.add_heading("5. Experiment 2 – Decision Tree vs Random Forest (default parameters)", 1)
    cols = ["model", "accuracy", "f1", "train_time_s", "predict_time_s"]
    para(d, "Heart Disease:", bold=True)
    table(d, H["dt_vs_rf"], cols)
    para(d, "Intel Images:", bold=True)
    table(d, I["dt_vs_rf"], cols)

    d.add_heading("6. Experiment 3 – comparison with SVM and Decision Tree", 1)
    para(d, "Experimental results", bold=True)
    para(d, "Heart Disease – default parameters (test set):")
    table(d, H["comparison"], ["model", "accuracy", "precision", "recall", "f1", "roc_auc", "train_time_s", "predict_time_s"])
    para(d, "Heart Disease – 5-fold cross-validation accuracy:")
    table(d, [{"model": k, "mean": v["mean"], "std": v["std"]} for k, v in H["cv"].items()])
    para(d, "Heart Disease – tuned with GridSearchCV:")
    table(d, H["tuned"], ["model", "accuracy", "f1", "roc_auc", "cv_best_score", "train_time_s"])
    para(d, "Best parameters: " + "; ".join(f"{k}: {v}" for k, v in H["best_params"].items()))
    figure(d, f / "heart_cm_roc.png", "Figure – Heart Disease: confusion matrices and ROC curves.", 6.5)
    figure(d, f / "heart_feature_importance.png", "Figure – Random Forest feature importance (Heart Disease).", 4.8)
    para(d, "Intel Images – default parameters (test set):")
    table(d, I["comparison"], ["model", "accuracy", "precision", "recall", "f1", "train_time_s", "predict_time_s"])
    figure(d, f / "intel_confusion.png", "Figure – Intel Images: confusion matrices.", 6.5)
    figure(d, f / "comparison_all.png", "Figure – accuracy, training time and prediction time of all models.", 6.5)
    para(d, "Overall framework", bold=True)
    para(d, "Every model on every dataset goes through the same pipeline: raw data → cleaning/imputation → encoding, scaling or resizing → train/test split "
            "(all transformers fitted on the training data only) → model training (Decision Tree, Random Forest, SVM) → hyper-parameter tuning (GridSearchCV, tabular data) → "
            "evaluation (accuracy, precision, recall, F1, ROC-AUC, confusion matrix, training and prediction time) → comparison and interpretation.")
    figure(d, f / "framework.png", "Figure – end-to-end experimental framework.", 6.5)
    para(d, "End-to-end analysis (auto-generated from the results)", bold=True)
    for chunk in _end_to_end(H, I):
        para(d, chunk)

    d.add_heading("7. Discussion (draft – rewrite in your own words)", 1)
    sh = pd.DataFrame(H["sweep_summary"])
    si = pd.DataFrame(I["sweep_summary"])
    dt_h, rf_h = H["dt_vs_rf"]
    dt_i, rf_i = I["dt_vs_rf"]
    para(d, "Effect of the number of trees on accuracy and stability. ", bold=True)
    para(d, f"On Heart Disease the mean test accuracy rose from {sh.test_acc_mean.iloc[0]:.3f} (1 tree) to {sh.test_acc_mean.iloc[-1]:.3f} ({int(sh.n_estimators.iloc[-1])} trees) and the standard deviation "
            f"across seeds fell from {sh.test_acc_std.iloc[0]:.3f} to {sh.test_acc_std.iloc[-1]:.3f}. On Intel Images accuracy went from {si.test_acc_mean.iloc[0]:.3f} to {si.test_acc_mean.iloc[-1]:.3f} "
            f"(std {si.test_acc_std.iloc[0]:.3f} → {si.test_acc_std.iloc[-1]:.3f}). Most of the gain comes in the first tens of trees; afterwards the curve is flat – more trees mainly buy stability, in line with Breiman's convergence result.")
    para(d, "Random Forest vs a single tree. ", bold=True)
    para(d, f"Heart Disease: accuracy {dt_h['accuracy']:.3f} → {rf_h['accuracy']:.3f}; {_time_phrase(dt_h, rf_h, H['dataset']['n_features_after_encoding'])}. "
            f"Intel Images: accuracy {dt_i['accuracy']:.3f} → {rf_i['accuracy']:.3f}; {_time_phrase(dt_i, rf_i, I['dataset']['n_features'])}. "
            "In both cases the forest is clearly more accurate and less sensitive to the training data, but it is harder to interpret. "
            "Note: on the small Heart dataset one test example is worth about 1.7 percentage points, so single-split numbers are noisy – the 5-fold cross-validation and the repeated seeds are more reliable.")
    para(d, "Insights on randomness and ensemble size. ", bold=True)
    para(d, "Randomness (bootstrap samples + random feature subsets) is what decorrelates the trees; without it all trees would be almost identical. A moderate ensemble (about 100 trees) is usually enough, "
            "larger ensembles give diminishing returns. On raw image pixels all classical models are limited by the weak feature representation – convolutional networks or engineered features (HOG, colour histograms) would be needed for a big jump.")

    d.add_heading("8. Code and reproduction", 1)
    para(d, f"GitHub repository: {cfg.get('github_url', '')}")
    bullets(d, [
        "Create the environment and install the packages (setup_env.bat / setup_env.sh, requirements.txt).",
        "Download the datasets into data/q2_heart and data/q2_intel.",
        "Run Q2/01_Q2_Heart_Disease.ipynb, then Q2/02_Q2_Intel_Images.ipynb, then Q2/03_Q2_Comparative_Analysis.ipynb (all random seeds are fixed).",
        "Results are written to results/q2/ (json + figures); reports/Build_Reports.ipynb regenerates this report.",
    ])
    out = REP / "Q2_Report.docx"
    d.save(out)
    return out


# =========================================================================== Q3
def build_q3():
    E = _load(RES / "q3" / "eda_summary.json")
    B = _load(RES / "q3" / "baseline_results.json")
    A = _load(RES / "q3" / "automl_results.json")
    C = _load(RES / "q3" / "comparison_results.json")
    if not all([E, B, A, C]):
        raise FileNotFoundError("Run all Q3 notebooks (01–04) first (results/q3/*.json missing).")
    meta = _load(ROOT / "models" / "model_metadata.json", {})
    cfg = config()
    f = RES / "q3"
    d = new_doc("Question 3 – End-to-End ML: Adult Income", "Baseline, AutoML (TPOT), FastAPI and Streamlit deployment")

    d.add_heading("1. Introduction and objective", 1)
    para(d, "The objective is to predict whether a person earns more than $50,000 per year (binary classification) with the Adult Income dataset and to build a complete "
            "ML solution: EDA, preprocessing, a scikit-learn baseline, an automated model search with TPOT, a model comparison, model saving, a REST API (FastAPI), "
            "a web interface (Streamlit) and a public deployment.")

    d.add_heading("2. Exploratory data analysis", 1)
    para(d, f"The dataset has {E['rows']} rows and {E['n_columns']} columns after dropping 2 columns. "
            f"Class balance: {E['class_balance']['<=50K']*100:.1f}% earn ≤50K and {E['class_balance']['>50K']*100:.1f}% earn >50K. "
            f"Duplicate rows: {E['duplicates']}. Missing values (marked '?'): {E['missing'] if E['missing'] else 'none'}.")
    figure(d, f / "eda_numeric.png", "Figure 1 – Distributions of the numeric features by income class.", 6.3)
    figure(d, f / "eda_categorical.png", "Figure 2 – Share of people earning >50K by categorical feature.", 6.3)
    figure(d, f / "eda_correlation.png", "Figure 3 – Correlation matrix.", 4.3)
    para(d, "Key insights:", bold=True)
    bullets(d, E["insights"])

    d.add_heading("3. Preprocessing and feature engineering", 1)
    bullets(d, [
        "Dropped fnlwgt (census sampling weight) and education (duplicate of education_num).",
        "Missing values: numeric → median, categorical → most frequent value.",
        "Numeric features standardised (StandardScaler); categorical features one-hot encoded (unknown categories ignored).",
        "Derived features: capital_net, log_capital_gain, has_capital_gain, has_capital_loss, is_married, is_us, age_group, hours_category.",
        f"Stratified 80/20 split ({B['n_train']} train / {B['n_test']} test, random_state = 42). All steps are inside one scikit-learn pipeline, so they are learned on training data only.",
    ])

    d.add_heading("4. Baseline model (scikit-learn)", 1)
    para(d, "Logistic Regression inside a preprocessing pipeline is the baseline; a Random Forest is shown as an additional reference. "
            "Metrics: accuracy, precision, recall, F1 (positive class >50K) and ROC-AUC – accuracy alone is misleading with a 76/24 class imbalance.")
    table(d, B["table"], ["model", "accuracy", "precision", "recall", "f1", "roc_auc", "train_time_s"])
    para(d, f"5-fold CV ROC-AUC of the baseline: {B['cv_roc_auc_mean']:.4f} ± {B['cv_roc_auc_std']:.4f}.")
    figure(d, f / "baseline_cm_roc.png", "Figure 4 – Baseline confusion matrix and ROC curves.", 6.2)

    d.add_heading("5. Automated machine learning (TPOT)", 1)
    para(d, f"{A['engine']} was run with search space '{A['search_space']}', a time budget of {A['time_budget_min']} minutes, 5-fold cross-validation on the training set "
            f"and ROC-AUC as the objective ({A['n_jobs']} parallel job(s)). The search took {A['search_time_s']/60:.1f} minutes. The preprocessing of the baseline was applied before the search.")
    para(d, "Best pipeline found:", bold=True)
    p = para(d, A["best_pipeline"], size=8)
    p.runs[0].font.name = "Consolas"
    para(d, "Test metrics of the TPOT pipeline: " + ", ".join(f"{k} = {v:.4f}" for k, v in A["test_metrics"].items()))

    d.add_heading("6. Model comparison", 1)
    table(d, C["comparison"])
    figure(d, f / "model_comparison.png", "Figure 5 – Baseline vs AutoML: metrics, ROC curves and training/search time.", 6.5)
    cmp = {r["model"]: r for r in C["comparison"]}
    b, a = cmp["Baseline: Logistic Regression"], cmp["AutoML: TPOT"]
    para(d, "Discussion (draft – rewrite in your own words)", bold=True)
    para(d, f"On the test set the ROC-AUC of the baseline is {b['roc_auc']:.4f} and that of TPOT is {a['roc_auc']:.4f} (F1: {b['f1']:.4f} vs {a['f1']:.4f}). "
            f"The baseline trained in {b['train/search time (s)']:.1f}s, the AutoML search needed {a['train/search time (s)']:.0f}s. Inference cost: {b['inference (ms/row)']:.4f} vs {a['inference (ms/row)']:.4f} ms per row; "
            f"model size {b['file size (MB)']:.2f} MB vs {a['file size (MB)']:.2f} MB. Complexity: {b['complexity']} versus {a['complexity']}.")
    para(d, "Advantages of the baseline: very fast, interpretable (coefficients), small and cheap to serve. Limitations: linear decision boundary, needs manual feature engineering. "
            "Advantages of AutoML: explores many models and hyper-parameters automatically and can find non-linear combinations without manual tuning. "
            "Limitations: long search time, non-deterministic results, possibly complex and hard-to-explain pipelines, and the improvement over a well-engineered baseline can be small.")
    para(d, f"Selected model: {C['best_model']} (highest test ROC-AUC). Note: selecting on the test set is a small optimistic bias; a separate validation set would avoid it.")

    d.add_heading("7. Model saving and feature importance", 1)
    para(d, "The best complete pipeline (preprocessing + model) was saved with joblib (models/best_model.joblib) together with a metadata file (metrics, feature importances, allowed input values). "
            "Feature importance was computed with permutation importance on the raw input features (drop in ROC-AUC when a feature is shuffled), which works for any model.")
    figure(d, f / "feature_importance.png", "Figure 6 – Top 5 most important features.", 4.5)
    table(d, C["top5"])

    d.add_heading("8. REST API (FastAPI)", 1)
    bullets(d, [
        "POST /predict – accepts the feature values as JSON and returns the predicted class, label and probability of income >50K (input validated with Pydantic).",
        "GET /metrics – test performance of the deployed model; GET /feature-importance – top features; GET /schema – allowed values; GET /health.",
        "Interactive documentation is generated automatically at /docs.",
    ])
    para(d, 'Example request: {"age": 39, "workclass": "Private", "education_num": 13, "marital_status": "Married-civ-spouse", "occupation": "Prof-specialty", '
            '"relationship": "Husband", "race": "White", "sex": "Male", "capital_gain": 0, "capital_loss": 0, "hours_per_week": 45, "native_country": "United-States"}', size=9)

    d.add_heading("9. Web interface (Streamlit) and deployment", 1)
    para(d, "The Streamlit app calls the API. It provides an input form for all features, shows the prediction with its probability, the model's test metrics and the top-5 most important features.")
    shots = sorted((REP / "screenshots").glob("*.png")) + sorted((REP / "screenshots").glob("*.jpg")) if (REP / "screenshots").exists() else []
    if shots:
        for i, s in enumerate(shots, 1):
            d.add_picture(str(s), width=Inches(6.0))
            para(d, f"Screenshot {i}", italic=True, size=9.5).alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        para(d, "[INSERT SCREENSHOTS OF THE RUNNING APP – put them in reports/screenshots/ and re-run the builder]", bold=True)
    para(d, f"Live application: {cfg.get('live_url', '')}", bold=True)
    para(d, "Deployment: a Docker Space on Hugging Face runs the FastAPI service and the Streamlit app in one container (package prepared in Q3/deploy_hf).")

    d.add_heading("10. Conclusion and lessons learned", 1)
    para(d, "The project covered the full ML life cycle. The key lessons are: handle the class imbalance with suitable metrics, keep all preprocessing inside one pipeline to avoid leakage "
            "and to make deployment easy, compare AutoML with a strong baseline instead of trusting it blindly, and pin library versions when saving and deploying a model.")
    out = REP / "Q3_Report.docx"
    d.save(out)
    return out


def build_all():
    outs = []
    for fn in (build_q1, build_q2, build_q3):
        try:
            outs.append(fn())
            print("created", outs[-1].name)
        except FileNotFoundError as e:
            print("SKIPPED", fn.__name__, "-", e)
    return outs
