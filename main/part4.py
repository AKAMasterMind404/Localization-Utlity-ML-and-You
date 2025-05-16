import multiprocessing
import os
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from collections import defaultdict
import tqdm
from sklearn.pipeline import Pipeline
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import constants as cnt
from game.auto_game import auto_game
from graph.sample.sample1 import currently_open_1


def worker(_):
    """Worker to run one episode of π1 data generation."""
    try:
        L = random.sample(list(currently_open_1), random.randint(20, 80))
        g = auto_game(bot_type=cnt.CURRENT_PART, isUseIpCells=True, open_cells=L)
        return f"{len(L)},{g.t}\n"
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def generate_pi1_data_parallel(num_points=100):
    """Generate π1 data points in parallel and save to file."""
    with multiprocessing.Pool() as pool, open(DATA_PATH, "a+") as f:
        for result in tqdm.tqdm(pool.imap(worker, range(num_points)), total=num_points, desc="Generating π₁ data"):
            if result:
                f.write(result)
                f.flush()
    print(f"[DONE] Saved {num_points} episodes to {DATA_PATH}")

def train_pi1_model():
    df = pd.read_csv(DATA_PATH, header=None, names=["L_size", "steps"])
    X = df[["L_size"]].values
    y = df["steps"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline([
        ("scale", StandardScaler()),
        ("poly", PolynomialFeatures(degree=DEGREE)),
        ("ridge", RidgeCV(alphas=np.logspace(-3, 3, 7), cv=5))
    ])
    model.fit(X_train, y_train)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("Model trained and saved to", MODEL_PATH)
    print("Train MSE:", mean_squared_error(y_train, model.predict(X_train)))
    print("Test MSE :", mean_squared_error(y_test, model.predict(X_test)))


# --- MODE: Plot Predicted vs Actual ---
def plot_pi1_predictions():
    df = pd.read_csv(DATA_PATH, header=None, names=["L_size", "steps"])
    X = df[["L_size"]].values
    y = df["steps"].values

    model = joblib.load(MODEL_PATH)

    binned = defaultdict(list)
    for xi, yi in zip(X.flatten(), y):
        binned[int(xi)].append(yi)

    sizes = sorted(binned.keys())
    avg_actual = [np.mean(binned[k]) for k in sizes]
    avg_predicted = [np.mean(model.predict(np.full((10, 1), k))) for k in sizes]

    plt.figure(figsize=(8, 6))
    plt.plot(sizes, avg_actual, 'b-o', label='Actual Avg Steps')
    plt.plot(sizes, avg_predicted, 'r--o', label='Predicted Avg Steps')
    plt.xlabel("L Size")
    plt.ylabel("Steps to Localize")
    plt.title("π₁ Model: Predicted vs Actual")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    DATA_PATH = "../data/data_p4.txt"
    MODEL_PATH = "../model/model2.joblib"
    MODE = "plot"  # Options: "generate", "train", "plot"
    ITERATIONS = 10
    DEGREE = 3

    if MODE == "generate":
        generate_pi1_data_parallel(num_points=10000)
    elif MODE == "train":
        train_pi1_model()
    elif MODE == "plot":
        plot_pi1_predictions()
    else:
        raise ValueError("Invalid MODE. Choose from: generate, train, plot.")
