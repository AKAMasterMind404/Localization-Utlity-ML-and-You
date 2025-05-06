import multiprocessing
import random
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
import constants as cnt
from game.auto_game import auto_game
from graph.sample.sample1 import currently_open_1


def worker(args):
    """Standalone worker function for parallel processing"""
    try:
        open_cells, L_size = args
        L = random.sample(open_cells, L_size)
        g = auto_game(bot_type=cnt.CURRENT_PART, isUseIpCells=False, open_cells=L)
        return f"{L_size},{g.t}\n"
    except Exception as e:
        print(f"Worker error: {e}")
        return ""


class DataService:
    def __init__(self, isGenerateData: bool, points: int):
        """
        Initialize data service
        :param isGenerateData: True to generate data, False to plot
        :param points: Number of runs per parameter combination
        """
        self.points = points
        self.isGenerateData = isGenerateData
        self.df = pd.DataFrame(columns=['timesteps', 'alpha', 'bot_number', 'is_rat_moving'])

    @staticmethod
    def generate_data(rounds = 0):
        min_size = 20
        max_size = 100
        trials_per_size = 10

        open_cells = list(currently_open_1)
        file = open("../data/data.txt", "a+")
        # Prepare argument list: one entry per trial
        params = []
        for L_size in range(min_size, max_size + 1):
            for _ in range(trials_per_size):
                params.append((open_cells, L_size))

        # Launch pool
        with multiprocessing.Pool() as pool, file:
            for result in tqdm(pool.imap(worker, params),
                               total=len(params),
                               desc="Generating part3 data"):
                if result:
                    file.write(result)
                    file.flush()

        if rounds > 0:
            DataService.generate_data(rounds-1)

    @staticmethod
    def plot_data():
        data = defaultdict(list)
        file = open("../data/data.txt", "r")
        for line in file:
            parts = line.strip().split(",")
            L_size = int(parts[0])
            steps = int(parts[1])
            data[L_size].append(steps)

        L_sizes = sorted(data.keys())
        avg_steps = [sum(data[k]) / len(data[k]) for k in L_sizes]

        plt.figure(figsize=(10, 6))
        plt.plot(L_sizes, avg_steps, marker="o")
        plt.xlabel("L Size")
        plt.ylabel("Average Steps to Localize")
        plt.title("Average Localization Steps vs Initial Uncertainty Set Size (|L|)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
