import json

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

from beaverfe import BeaverPipeline, auto_feature_pipeline
from beaverfe.auto_parameters.shared import evaluate_model


def load_data():
    df = pd.read_csv("examples_2/BTC-Hourly.csv")
    df = df.rename(columns={"close": "target"})
    df = df.drop(columns=["unix"])

    df["date"] = pd.to_datetime(df["date"])
    df = df[:1000]

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
    # df = duplicate_random_rows_and_remove_values(df, target_column="target")
    df["target"] = np.where(df["target"] > np.roll(df["target"], 1), 1, 0)
    x, y = df.drop(columns="target"), df["target"]
    # y = np.where(y > np.roll(y, 1), 1, 0)

    model = KNeighborsClassifier()
    scoring = "accuracy"
    direction = "maximize"

    # Evalute baseline model
    x_base = x.fillna(0)
    score = evaluate_model(x_base, y, model, scoring)
    print(f"Baseline score: {score}")

    # Auto transformations
    transformations = auto_feature_pipeline(x, y, model, scoring, direction)

    # Evalute model with transformations
    transformer = BeaverPipeline(transformations)

    score = evaluate_model(x, y, model, scoring, transformer=transformer)
    print(f"Transformations score: {score}")

    print(json.dumps(transformations, indent=4))
