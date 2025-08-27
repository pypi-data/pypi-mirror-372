import json
import warnings
from statistics import mean
import time

import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer, load_iris, load_wine
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import OrdinalEncoder, label_binarize

from beaverfe import BeaverPipeline, auto_feature_pipeline
from beaverfe.auto_parameters.shared import evaluate_model

warnings.filterwarnings("ignore")

# =============================
# Dataset loading
# =============================


def load_dataset(dataset):
    datasets = {
        "adult": load_adult,
        "bank": load_bank,
        "breast": lambda: load_breast_cancer(return_X_y=True, as_frame=True),
        "credit": load_credit,
        "heart": load_heart,
        "iris": lambda: load_iris(return_X_y=True, as_frame=True),
        "sonar": load_sonar,
        "wine": lambda: load_wine(return_X_y=True, as_frame=True),
    }

    if dataset not in datasets:
        raise ValueError(
            f"Dataset '{dataset}' no soportado. Usa uno de {list(datasets)}"
        )

    return datasets[DATASET]()


def load_adult():
    df = pd.read_csv("examples/datasets/adult.csv")
    X = df.drop("income", axis=1)
    y = df["income"].apply(lambda x: 1 if ">50K" in str(x) else 0)
    return X, y


def load_bank():
    df = pd.read_csv("examples/datasets/bank.csv")
    X = df.drop("y", axis=1)
    y = df["y"].apply(lambda x: 1 if x == "yes" else 0)
    return X, y


def load_credit():
    df = pd.read_csv("examples/datasets/default_of_credit_card_clients.csv")
    X = df.drop(columns=["ID", "default"], axis=1)
    y = df["default"]
    return X, y


def load_heart():
    df = pd.read_csv("examples/datasets/heart_disease.csv")
    X = df.drop("target", axis=1)
    y = df["target"]
    return X, y


def load_sonar():
    column_names = [f"feature_{i}" for i in range(60)] + ["target"]
    df = pd.read_csv("examples_2/sonar.csv", header=None, names=column_names)
    X = df.drop("target", axis=1)
    y = df["target"]
    return X, y


# =============================
# Model factory
# =============================


def get_model(model_name: str, is_binary: bool):
    base_models = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "random_forest": RandomForestClassifier(n_estimators=100),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=100),
    }
    if not is_binary:
        base_models["logistic_regression"] = OneVsRestClassifier(
            base_models["logistic_regression"]
        )

    if model_name not in base_models:
        raise ValueError(
            f"Modelo '{model_name}' no soportado. Usa uno de {list(base_models)}"
        )

    return base_models[model_name]


# =============================
# Preprocessing & Evaluation
# =============================


def preprocess_categorical(X: pd.DataFrame) -> pd.DataFrame:
    cat_cols = X.select_dtypes(include=["object", "category"]).columns
    if not cat_cols.empty:
        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        X[cat_cols] = encoder.fit_transform(X[cat_cols])
    return X


def train_and_evaluate(X, y, scoring, model_name, use_beaver=False):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y)

    is_binary = len(np.unique(y)) == 2
    model = get_model(model_name, is_binary)

    if use_beaver:
        transformations = auto_feature_pipeline(
            X_train,
            y_train,
            model,
            scoring,
            preprocessing=True,
            feature_generation=True,
            normalization=True,
            dimensionality_reduction=True,
        )
        pipeline = BeaverPipeline(transformations)
        X_train_transformed = pipeline.fit_transform(X_train, y_train)
        X_test_transformed = pipeline.transform(X_test, y_test)
    else:
        transformations = None
        pipeline = None
        X_train_transformed = X_train.copy()
        X_test_transformed = X_test.copy()

    model.fit(X_train_transformed, y_train)
    y_score = model.predict_proba(X_test_transformed)

    y_test_bin = label_binarize(y_test, classes=np.unique(y_test))
    auc_score = (
        roc_auc_score(y_test, y_score[:, 1])
        if is_binary
        else roc_auc_score(y_test_bin, y_score, multi_class="ovr", average="weighted")
    )

    eval_score = evaluate_model(
        X_test, y_test, model, scoring, cv=3, transformer=pipeline
    )

    return auc_score, eval_score, transformations


# =============================
# Main
# =============================

if __name__ == "__main__":
    DATASET = "adult"  # adult, bank, breast, credit, heart, iris, sonar, wine
    MODEL_NAME = (
        "logistic_regression"  # logistic_regression, random_forest, gradient_boosting
    )
    N_TRIALS = 1

    X, y = load_dataset(DATASET)
    is_binary = len(np.unique(y)) == 2
    scoring = "roc_auc" if is_binary else "roc_auc_ovr"

    lst_base_score = []
    lst_base_score_2 = []
    lst_bfe_score = []
    lst_bfe_score_2 = []

    for _ in range(N_TRIALS):
        # Baseline
        X_baseline = preprocess_categorical(X.copy())
        base_score, base_score_2, _ = train_and_evaluate(
            X_baseline, y, scoring, MODEL_NAME
        )
        lst_base_score.append(base_score)
        lst_base_score_2.append(base_score_2)

        # BeaverFE
        bfe_score, bfe_score_2, transformations = train_and_evaluate(
            X.copy(), y, scoring, MODEL_NAME, use_beaver=True
        )
        lst_bfe_score.append(bfe_score)
        lst_bfe_score_2.append(bfe_score_2)

    base_score = mean(lst_base_score)
    base_score_2 = mean(lst_base_score_2)
    bfe_score = mean(lst_bfe_score)
    bfe_score_2 = mean(lst_bfe_score_2)

    # Results
    print("\n\n", "-" * 80, "\n")
    print(json.dumps(transformations, indent=4))

    print(
        f"\n[Baseline] {MODEL_NAME} AUC: {base_score:.4f} - ",
        ", ".join([f"{x:.4f}" for x in lst_base_score]),
    )
    print(
        f"[BeaverFE ] {MODEL_NAME} AUC: {bfe_score:.4f} - ",
        ", ".join([f"{x:.4f}" for x in lst_bfe_score]),
    )
    print(
        f"\n[Baseline] Evaluated score: {base_score_2:.4f} - ",
        ", ".join([f"{x:.4f}" for x in lst_base_score_2]),
    )
    print(
        f"[BeaverFE ] Evaluated score: {bfe_score_2:.4f} - ",
        ", ".join([f"{x:.4f}" for x in lst_bfe_score_2]),
    )
