import json

import numpy as np
import pandas as pd
from sklearn.datasets import load_wine
from sklearn.neighbors import KNeighborsClassifier

from beaverfe import BeaverPipeline, auto_feature_pipeline
from beaverfe.auto_parameters.shared import evaluate_model


def load_data():
    # Wine
    data = load_wine()

    df = pd.DataFrame(data.data, columns=data.feature_names)
    df["target"] = data.target

    return df


def duplicate_random_rows_and_remove_values(
    df, target_column=None, duplicates_percentage=0.05, missing_percentage=0.05
):
    df = df.copy()

    # Step 1: Randomly duplicate x% rows
    if duplicates_percentage > 0:
        # Select random indices to duplicate
        duplicate_indices = np.random.choice(
            df.index, size=int(len(df) * duplicates_percentage), replace=True
        )

        # Duplicate those rows and add them to the DataFrame
        df_duplicates = df.loc[duplicate_indices]
        df = pd.concat([df, df_duplicates], ignore_index=True)

    # Step 2: Remove x% of the values in each column except the target column
    if missing_percentage > 0:
        # Create a mask to mark the values to remove
        mask = np.random.rand(*df.shape) < missing_percentage

        # If a target column is specified, ensure that we do not set NaNs in that column
        if target_column and target_column in df.columns:
            target_index = df.columns.get_loc(target_column)
            mask[:, target_index] = False

        # Apply the mask, setting NaN in the selected locations
        df = df.mask(mask)

    return df


if __name__ == "__main__":
    df = load_data()

    df = duplicate_random_rows_and_remove_values(
        df, target_column="target", duplicates_percentage=0, missing_percentage=0.05
    )
    x, y = df.drop(columns="target"), df["target"]

    model = KNeighborsClassifier()
    # model = RandomForestClassifier()
    scoring = "roc_auc_ovr"
    direction = "maximize"

    # Evalute baseline model
    x_base = x.fillna(0)
    score = evaluate_model(x_base, y, model, scoring)
    print(f"Baseline score: {score}")

    # Auto transformations
    transformations = auto_feature_pipeline(x, y, model, scoring, direction)

    # Evalute model with transformations
    transformer = BeaverPipeline(transformations)

    score2 = evaluate_model(x, y, model, scoring, transformer=transformer)
    print(f"Transformations score: {score} - {score2}")

    print("\n\n", "-" * 80, "\n")
    print(json.dumps(transformations, indent=4))

    print("\n\n", "-" * 80, "\n")

    point = int(x.shape[0] * 0.66)

    x_train, y_train = x[:point], y[:point]
    x_test, y_test = x[point:], y[point:]

    print(x_test.head())
    print("\n", "-" * 50, "\n")

    transformer.fit(x_train, y_train)
    x_test = transformer.transform(x_test, y_test)
    print(x_test.head())
