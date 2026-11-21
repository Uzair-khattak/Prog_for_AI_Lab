"""Shared helpers for the Programming-for-AI mid-term lab."""
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = None
for _p in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
    if (_p / "requirements.txt").exists():
        ROOT = _p
        break
if ROOT is None:
    ROOT = Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------- I/O helpers
def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=_default)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def savefig(fig, question, name, dpi=150):
    """Save a matplotlib figure to results/<question>/<name>.png"""
    out = ROOT / "results" / question
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.png", dpi=dpi, bbox_inches="tight")
    return out / f"{name}.png"


# ----------------------------------------------------------------- Q2 helpers
def find_csv(folder):
    files = sorted(Path(folder).glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No .csv file found in {folder}. Download the dataset and put it there.")
    return files[0]


def load_heart(data_dir, drop=("id", "unnamed: 0")):
    """Load the Heart Disease UCI csv. Works for both the Kaggle 'heart.csv' (target 0/1)
    and 'heart_disease_uci.csv' (column 'num' = 0..4). Target is converted to binary: 0 = healthy, 1 = disease."""
    path = find_csv(data_dir)
    df = pd.read_csv(path)
    low = {c.lower(): c for c in df.columns}
    candidates = ["target", "num", "heartdisease", "heart_disease", "condition", "output", "class"]
    target = next((low[c] for c in candidates if c in low), df.columns[-1])
    drop_cols = [low[c] for c in drop if c in low]
    y = (pd.to_numeric(df[target], errors="coerce") > 0).astype(int)
    X = df.drop(columns=[target] + drop_cols)
    # make text/bool columns consistent strings (keep NaN as NaN so the imputer can handle it)
    for c in X.columns:
        if X[c].dtype == object or X[c].dtype == bool:
            X[c] = X[c].map(lambda v: v if pd.isna(v) else str(v))
    return df, X, y, target, path


def make_preprocessor(X, scale_numeric=True):
    """Impute + (scale) numeric columns, impute + one-hot categorical columns."""
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]
    num_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        num_steps.append(("scaler", StandardScaler()))
    transformers = [("num", Pipeline(num_steps), num_cols)]
    if cat_cols:
        transformers.append(("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), cat_cols))
    return ColumnTransformer(transformers), num_cols, cat_cols


def evaluate_model(model, Xtr, ytr, Xte, yte, name, n_repeats=3, average="binary"):
    """Fit `model` (n_repeats times to average the training time) and compute test metrics."""
    from sklearn.base import clone
    from sklearn.metrics import (accuracy_score, f1_score, precision_score, recall_score, roc_auc_score)

    times = []
    fitted = None
    for _ in range(n_repeats):
        m = clone(model)
        t = time.perf_counter()
        m.fit(Xtr, ytr)
        times.append(time.perf_counter() - t)
        fitted = m
    t = time.perf_counter()
    pred = fitted.predict(Xte)
    pred_time = time.perf_counter() - t
    res = {
        "model": name,
        "accuracy": float(accuracy_score(yte, pred)),
        "precision": float(precision_score(yte, pred, average=average, zero_division=0)),
        "recall": float(recall_score(yte, pred, average=average, zero_division=0)),
        "f1": float(f1_score(yte, pred, average=average, zero_division=0)),
        "train_time_s": float(np.mean(times)),
        "predict_time_s": float(pred_time),
        "roc_auc": None,
    }
    try:
        n_classes = len(np.unique(ytr))
        if n_classes == 2:
            score = fitted.predict_proba(Xte)[:, 1] if hasattr(fitted, "predict_proba") else fitted.decision_function(Xte)
            res["roc_auc"] = float(roc_auc_score(yte, score))
        elif hasattr(fitted, "predict_proba"):
            res["roc_auc"] = float(roc_auc_score(yte, fitted.predict_proba(Xte), multi_class="ovr", average="macro"))
    except Exception:
        pass
    return res, fitted, pred


def sweep_n_estimators(Xtr, ytr, Xte, yte, ns=(1, 10, 50, 100, 300), seeds=(0, 1, 2, 3, 4), n_jobs=-1):
    """Train a RandomForest for every n_estimators and every random seed; return a long DataFrame."""
    from sklearn.ensemble import RandomForestClassifier

    rows = []
    for n in ns:
        for s in seeds:
            rf = RandomForestClassifier(n_estimators=n, random_state=s, n_jobs=n_jobs, oob_score=(n >= 10))
            t = time.perf_counter()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                rf.fit(Xtr, ytr)
            fit_t = time.perf_counter() - t
            rows.append({
                "n_estimators": n, "seed": s,
                "test_accuracy": float(rf.score(Xte, yte)),
                "train_accuracy": float(rf.score(Xtr, ytr)),
                "oob_accuracy": float(rf.oob_score_) if n >= 10 else np.nan,
                "train_time_s": fit_t,
            })
        print(f"  n_estimators={n:>4} done")
    return pd.DataFrame(rows)


def summarize_sweep(df):
    g = df.groupby("n_estimators")
    out = g.agg(test_acc_mean=("test_accuracy", "mean"), test_acc_std=("test_accuracy", "std"),
                train_acc_mean=("train_accuracy", "mean"), oob_acc_mean=("oob_accuracy", "mean"),
                train_time_mean=("train_time_s", "mean")).reset_index()
    out["test_acc_std"] = out["test_acc_std"].fillna(0.0)
    return out


# ----------------------------------------------------------------- Intel image loader
def _find_split_dirs(root):
    """Locate the train / test folders (each contains one sub-folder per class)."""
    root = Path(root)
    exts = {".jpg", ".jpeg", ".png"}
    class_dirs = {}
    for d in root.rglob("*"):
        if d.is_dir() and any(f.suffix.lower() in exts for f in d.iterdir() if f.is_file()):
            class_dirs.setdefault(d.parent, []).append(d)
    train = test = None
    for parent, dirs in class_dirs.items():
        if len(dirs) < 2:
            continue
        name = parent.name.lower()
        if "train" in name:
            train = parent
        elif "test" in name:
            test = parent
    if train is None or test is None:
        raise FileNotFoundError(
            f"Could not find seg_train / seg_test folders inside {root}. "
            "Unzip the Kaggle 'Intel Image Classification' archive into that folder.")
    return train, test


def load_intel_images(root, img_size=32, max_per_class=None, seed=0, cache=True):
    """Load the Intel Image Classification dataset (6 classes) as small RGB arrays.
    Returns Xtr, ytr, Xte, yte (uint8 images, N x H x W x 3) and the class-name list.
    Results are cached as .npz so the (slow) loading happens only once."""
    from PIL import Image
    from joblib import Parallel, delayed

    root = Path(root)
    cache_file = root / f"cache_{img_size}px_{max_per_class}.npz"
    if cache and cache_file.exists():
        z = np.load(cache_file, allow_pickle=True)
        return z["Xtr"], z["ytr"], z["Xte"], z["yte"], list(z["classes"])

    train_dir, test_dir = _find_split_dirs(root)
    classes = sorted(d.name for d in train_dir.iterdir() if d.is_dir())
    rng = np.random.default_rng(seed)

    def read(p):
        with Image.open(p) as im:
            return np.asarray(im.convert("RGB").resize((img_size, img_size), Image.BILINEAR), dtype=np.uint8)

    def load_split(split_dir):
        paths, labels = [], []
        for ci, c in enumerate(classes):
            fs = sorted(f for f in (split_dir / c).iterdir() if f.suffix.lower() in {".jpg", ".jpeg", ".png"})
            if max_per_class and len(fs) > max_per_class:
                fs = list(rng.choice(np.array(fs, dtype=object), max_per_class, replace=False))
            paths += fs
            labels += [ci] * len(fs)
        imgs = Parallel(n_jobs=-1, prefer="threads")(delayed(read)(p) for p in paths)
        return np.stack(imgs), np.array(labels)

    print("Loading training images ...")
    Xtr, ytr = load_split(train_dir)
    print("Loading test images ...")
    Xte, yte = load_split(test_dir)
    if cache:
        np.savez_compressed(cache_file, Xtr=Xtr, ytr=ytr, Xte=Xte, yte=yte, classes=np.array(classes))
    return Xtr, ytr, Xte, yte, classes


def image_features(imgs, mode="pixels"):
    """pixels   : raw normalised RGB pixels, flattened (N x H*W*3)
       hog_color: HOG edge features on grey image + 8-bin colour histograms per channel"""
    imgs = np.asarray(imgs)
    if mode == "pixels":
        return imgs.reshape(len(imgs), -1).astype(np.float32) / 255.0
    if mode == "hog_color":
        from skimage.feature import hog
        feats = []
        for im in imgs:
            grey = im.mean(axis=2)
            h = hog(grey, orientations=8, pixels_per_cell=(8, 8), cells_per_block=(1, 1))
            hist = np.concatenate([np.histogram(im[..., c], bins=8, range=(0, 255))[0] / im[..., c].size
                                   for c in range(3)])
            feats.append(np.concatenate([h, hist]))
        return np.array(feats, dtype=np.float32)
    raise ValueError("mode must be 'pixels' or 'hog_color'")
