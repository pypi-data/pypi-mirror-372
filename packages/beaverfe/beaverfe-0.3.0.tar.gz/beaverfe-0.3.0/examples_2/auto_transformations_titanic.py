import json

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from beaverfe import BeaverPipeline, auto_feature_pipeline
from beaverfe.auto_parameters.shared import evaluate_model


def load_data():
    # data = load_iris()

    # df = pd.DataFrame(data.data, columns=data.feature_names)
    # df["target"] = data.target

    # # Wine
    # data = load_wine()

    # df = pd.DataFrame(data.data, columns=data.feature_names)
    # df["target"] = data.target

    # TITANIC
    df = pd.read_csv("examples_2/titanic.csv")
    df = df.rename(columns={"Survived": "target"})
    df = df.drop(columns=["PassengerId", "Name", "Ticket"])

    # BTC
    # df = pd.read_csv("examples/BTC-Hourly.csv")
    # df = df.rename(columns={"close": "target"})
    # df = df.drop(columns=["unix"])

    # df["date"] = pd.to_datetime(df["date"])
    # df = df[:1000]

    return df


def duplicate_random_rows_and_remove_values(
    df, target_column=None, duplicates_percentage=0.0, missing_percentage=0.05
):
    # Step 1: Randomly duplicate x% rows
    # Select random indices to duplicate
    duplicate_indices = np.random.choice(
        df.index, size=int(len(df) * duplicates_percentage), replace=True
    )

    # Duplicate those rows and add them to the DataFrame
    df_duplicates = df.loc[duplicate_indices]
    df_extended = pd.concat([df, df_duplicates], ignore_index=True)

    # Step 2: Remove x% of the values in each column except the target column
    # Create a mask to mark the values to remove
    mask = np.random.rand(*df_extended.shape) < missing_percentage

    # If a target column is specified, ensure that we do not set NaNs in that column
    if target_column and target_column in df_extended.columns:
        target_index = df_extended.columns.get_loc(target_column)
        mask[:, target_index] = False

    # Apply the mask, setting NaN in the selected locations
    df_extended = df_extended.mask(mask)

    return df_extended


if __name__ == "__main__":
    df = load_data()
    df = duplicate_random_rows_and_remove_values(df, target_column="target")
    x, y = df.drop(columns="target"), df["target"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.33, random_state=42
    )

    model = KNeighborsClassifier()
    # model = RandomForestClassifier()
    scoring = "roc_auc"  # "accuracy"
    direction = "maximize"

    # Evalute baseline model
    x_base = x.copy()
    # x_base = x_base.fillna(0)
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
