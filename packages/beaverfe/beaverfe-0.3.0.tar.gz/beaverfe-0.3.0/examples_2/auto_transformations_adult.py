import json

from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from beaverfe import BeaverPipeline, auto_feature_pipeline
from beaverfe.auto_parameters.shared import evaluate_model


def load_data():
    data = fetch_openml("adult", version=2, as_frame=True)
    df = data.data
    y = data.target
    df["target"] = y

    le = LabelEncoder()
    df["target"] = le.fit_transform(df["target"])

    df["workclass"] = df["workclass"].astype(str)
    df["education"] = df["education"].astype(str)
    df["marital-status"] = df["marital-status"].astype(str)
    df["occupation"] = df["occupation"].astype(str)
    df["relationship"] = df["relationship"].astype(str)
    df["race"] = df["race"].astype(str)
    df["sex"] = df["sex"].astype(str)
    df["native-country"] = df["native-country"].astype(str)

    return df


if __name__ == "__main__":
    df = load_data()
    x, y = df.drop(columns="target"), df["target"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.33, random_state=42
    )

    # model = KNeighborsClassifier()
    model = RandomForestClassifier()
    scoring = "roc_auc"  # "accuracy"
    direction = "maximize"

    # Evalute baseline model
    x_base = x.copy()

    # # Primero: rellena categóricas con "Unknown"
    # for col in x_base.select_dtypes(include="category").columns:
    #     if "Unknown" not in x_base[col].cat.categories:
    #         x_base[col] = x_base[col].cat.add_categories(["Unknown"])
    #     x_base[col] = x_base[col].fillna("Unknown")

    # # Luego: rellena numéricas con 0
    # for col in x_base.select_dtypes(include=["float", "int"]).columns:
    #     x_base[col] = x_base[col].fillna(0)

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
    score2 = evaluate_model(x, y, model, scoring, transformer=transformer)

    print(f"Transformations score: {score} - {score2}")

    print(json.dumps(transformations, indent=4))
