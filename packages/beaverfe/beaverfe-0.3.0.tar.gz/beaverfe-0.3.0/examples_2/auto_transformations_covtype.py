import json

import pandas as pd
from sklearn.datasets import fetch_covtype
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

from beaverfe import BeaverPipeline, auto_feature_pipeline
from beaverfe.auto_parameters.shared import evaluate_model


def load_data():
    data = fetch_covtype()
    df = pd.DataFrame(data.data)
    y = pd.Series(data.target)

    df["target"] = y

    return df


if __name__ == "__main__":
    df = load_data()
    x, y = df.drop(columns="target"), df["target"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.33, random_state=42
    )

    # model = KNeighborsClassifier()
    model = RandomForestClassifier()
    scoring = "roc_auc_ovr"  # "accuracy"
    direction = "maximize"

    # Evalute baseline model
    x_base = x.copy()
    x_base = x_base.fillna(0)
    score = evaluate_model(x_base, y, model, scoring)
    print(f"Baseline score: {score}")

    # Auto transformations
    transformations = auto_feature_pipeline(x_train, y_train, model, scoring, direction)

    # Evalute model with transformation
    transformer = BeaverPipeline(transformations)
    x_train = transformer.fit_transform(x_train, y_train)
    x_test = transformer.transform(x_test, y_test)

    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    score = f1_score(y_test, y_pred)
    score2 = evaluate_model(x, y, model, scoring, transformer=transformer)

    print(f"Transformations score: {score} - {score2}")

    print(json.dumps(transformations, indent=4))
