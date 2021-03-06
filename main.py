"""
This is the main functtion for the files.

It should contain functions that
* Load the dataset or datasets to be used
* Initialize the genetic algorithm and its population
* Train on the dataset
"""
import numpy as np
import pandas as pd
import genetic_algorithm
import neural_network
from sklearn.metrics import mean_squared_error

SEED = 42
OUTPUT_SIZE = [1]
HIDDEN_LAYER_SIZES = [5, 25]  # , 10, 25, 50, 100, 250]
LEARNING_RATES = [1e-3]

np.random.seed(SEED)


def load_dataset(name):
    frame = pd.read_csv(name, index_col=0)
    return frame


def calculate_input_size(data):
    return data.shape[1] - 1


def plot_comparison():
    import matplotlib.pyplot as plt

    pass


def cross_validate_on_data(estimator, param_grid, data):
    from sklearn.model_selection import GridSearchCV

    grid = GridSearchCV(
        estimator,
        param_grid,
        scoring="neg_mean_squared_error",
        cv=3,
        n_jobs=1,
        verbose=4,
    )
    X, y = split_data(data)
    grid.fit(X, y)
    return grid


def make_nn_grid(data):
    estimator = neural_network.NeuralNetwork()
    param_grid = {
        "input_size": [calculate_input_size(data)],
        "hidden_layer_size": HIDDEN_LAYER_SIZES,
        "output_size": OUTPUT_SIZE,
        "learning_rate": LEARNING_RATES,
        "epochs": [10],
        "verbose": [0],  # ****** REMEMBER TO TOGGLE VERBOSITY ******
    }
    print("\n\n***** Training Neural Networks *****\n\n")
    return cross_validate_on_data(estimator, param_grid, data)


def make_ga_grid(data, hybrid):
    # init ga
    estimator = genetic_algorithm.GeneticAlgorithm()
    param_grid = {
        "hybrid": [hybrid],
        "input_size": [data.shape[1] - 1],
        "hidden_layer_size": HIDDEN_LAYER_SIZES,
        "output_size": OUTPUT_SIZE,
        "population_size": [5],
        "selection_size": [3],
        "learning_rate": LEARNING_RATES,
        "epochs": [5],
        "generations": [2],
        "cases": [["mse", "l2", "l1"]],
        "verbose": [0],  # ****** REMEMBER TO TOGGLE VERBOSITY ******
    }
    if hybrid is True:
        print("\n\n***** Training Hybrid GA *****\n\n")
    else:
        print("\n\n***** Training GA *****\n\n")
    return cross_validate_on_data(estimator, param_grid, data)


def split_data(data):
    input_cols = list(data.columns)
    input_cols.remove("y")
    y = data["y"].values
    X = data[input_cols].values
    return X, y


def analyze_grids(grids, data):
    X, y = split_data(data)
    print("X.shape", X.shape)
    print("y.shape", y.shape)
    # extract best models for each grid
    hybrid_model = grids["hybrid"].best_estimator_
    nn_model = grids["nn"].best_estimator_
    ga_model = grids["ga"].best_estimator_
    if hybrid_model == nn_model or ga_model == hybrid_model or nn_model == ga_model:
        raise ValueError("The best estimators aren't supposed to be the same!")
    # predict with models
    y_hybrid = hybrid_model.predict(X)
    y_nn = nn_model.predict(X)
    y_ga = ga_model.predict(X)
    # calculate MSE
    hybrid_mse = mean_squared_error(y, y_hybrid)
    nn_mse = mean_squared_error(y, y_nn)
    ga_mse = mean_squared_error(y, y_ga)
    # print each MSE values
    print("Hybrid GA MSE:", hybrid_mse)
    print("Neural Network MSE:", nn_mse)
    print("GA MSE:", ga_mse)


if __name__ == "__main__":
    # load data
    data = load_dataset("data/uball_0.0_50_200").sample(frac=1)
    split = int(len(data) * 0.8)
    train = data[:split]
    test = data[split:]
    grids = {
        "nn": make_nn_grid(train),
        "hybrid": make_ga_grid(train, True),
        "ga": make_ga_grid(train, False),
    }
    analyze_grids(grids, test)
