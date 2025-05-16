import os
import pandas as pd
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


def loadDataFromFile(file_path="../data/data.txt"):
    df = pd.read_csv(file_path, header=None, names=["L_size", "steps"])
    X = df[["L_size"]].values
    y = df["steps"].values
    return X, y


def trainModel(X, y, degree=3):
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("poly", PolynomialFeatures(degree=degree)),
        ("regressor", RidgeCV(alphas=np.logspace(-3, 3, 7), scoring='neg_mean_squared_error', cv=5))
    ])
    model.fit(X, y)
    return model


def plotTrainingVSTestLoss(model, X, y):
    losses_train, losses_test = [], []
    percentages = np.linspace(0.1, 0.9, 9)

    for frac in percentages:
        X_train_part, _, y_train_part, _ = train_test_split(X, y, train_size=frac, random_state=42)
        model.fit(X_train_part, y_train_part)
        y_pred_train = model.predict(X_train_part)
        y_pred_test = model.predict(X)
        losses_train.append(mean_squared_error(y_train_part, y_pred_train))
        losses_test.append(mean_squared_error(y, y_pred_test))

    plt.figure(figsize=(8, 6))
    plt.plot(percentages * 100, losses_train, marker='o', label="Train MSE")
    plt.plot(percentages * 100, losses_test, marker='o', label="Test MSE", color='orange')
    plt.xlabel("Training Data Used (%)")
    plt.ylabel("MSE")
    plt.title("Training vs Test Loss Curve")
    plt.legend()
    plt.grid(True)
    plt.ylim(min(losses_train + losses_test) * 0.95, max(losses_train + losses_test) * 1.05)  # tight zoom
    plt.tight_layout()
    plt.show()


def plotActualVsPredictedStepsToLocalize(model, X, y):
    from collections import defaultdict

    data = defaultdict(list)
    for xi, yi in zip(X.flatten(), y):
        data[int(xi)].append(yi)

    L_sizes = sorted(data.keys())
    avg_actual = [np.mean(data[k]) for k in L_sizes]
    avg_predicted = [np.mean(model.predict(np.full((10, 1), k))) for k in L_sizes]

    plt.figure(figsize=(8, 6))
    plt.plot(L_sizes, avg_actual, 'b-', marker='o', label='Actual Avg Steps')
    plt.plot(L_sizes, avg_predicted, 'r-', marker='o', label='Predicted Avg Steps')
    plt.xlabel("L Size")
    plt.ylabel("Average Steps to Localize")
    plt.title("Predicted vs Actual Steps to Localize vs L Size")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    x, y = loadDataFromFile()
    DATA_PATH = "../data/data.txt"
    MODEL_PATH = "../model/model1.joblib"
    isTrain = False  # Toggle this to False to run plots

    if isTrain:
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        model = trainModel(X_train, y_train, degree=3)
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        print("Train MSE:", mean_squared_error(y_train, model.predict(X_train)))
        print("Test MSE:", mean_squared_error(y_test, model.predict(X_test)))
    else:
        try:
            model = joblib.load(MODEL_PATH)
            plotTrainingVSTestLoss(model, x, y)
            plotActualVsPredictedStepsToLocalize(model, x, y)
        except:
            print("Model not found! Run train first!")
            pass