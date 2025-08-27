import pandas as pd
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier

from beaverfe import BeaverPipeline
from beaverfe.auto_parameters.shared import evaluate_model


def load_data():
    data = load_iris()

    df = pd.DataFrame(data.data, columns=data.feature_names)
    df["target"] = data.target

    # Wine
    # data = load_wine()

    # df = pd.DataFrame(data.data, columns=data.feature_names)
    # df["target"] = data.target

    # TITANIC
    # df = pd.read_csv("examples_2/titanic.csv")
    # df = df.rename(columns={"Survived": "target"})
    # df = df.drop(columns=["PassengerId", "Name", "Ticket"])

    # BTC
    # df = pd.read_csv("examples/BTC-Hourly.csv")
    # df = df.rename(columns={"close": "target"})
    # df = df.drop(columns=["unix"])

    # df["date"] = pd.to_datetime(df["date"])
    # df = df[:1000]

    return df


if __name__ == "__main__":
    df = load_data()
    x, y = df.drop(columns="target"), df["target"]

    model = KNeighborsClassifier()
    scoring = "accuracy"
    direction = "maximize"

    # Evalute baseline model
    x_base = x.copy()
    x_base = x_base.fillna(0)
    score = evaluate_model(x_base, y, model, scoring)
    print(f"Baseline score: {score}")

    # Load transformations
    transformer = BeaverPipeline()
    transformer.load_transformations("beaverfe_transformations.pkl")

    # Evalute model with transformations
    x = x.fillna(0)
    score = evaluate_model(x, y, model, scoring, transformer)
    print(f"Transformations score: {score}")
