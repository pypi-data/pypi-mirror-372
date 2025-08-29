import pandas as pd
import random


class Data():
    def __init__(self, name: str, X: pd.DataFrame, y: pd.Series):
        self.name = name
        self.X = X.reindex(sorted(X.columns), axis=1)
        self.y = y
        self.all = pd.merge(self.X, y, right_index=True, left_index=True)

    def sort(self):
        names = self.X

    def __len__(self):
        return self.y.size

    def __str__(self):
        return self.name

    def __getitem__(self, item):
        #  item is a slice object of three ints
        X = self.X.iloc[item]
        y = self.y.iloc[item]
        # todo fix name
        return Data(f"{self.name}_learning", X, y)

    def bootstrap(self):
        btstr_X = pd.DataFrame(columns=self.X.columns)
        btstr_y = pd.Series(name=self.y.name)
        for a_data in range(self.X.shape[0]):
            selected_num = random.choice(range(self.X.shape[0]))
            btstr_X = pd.concat([btstr_X, self.X[selected_num: selected_num + 1]])
            btstr_y = pd.concat([btstr_y, self.y[selected_num: selected_num + 1]])
        # btstr_X.reset_index(inplace=True)
        # btstr_y.reset_index(inplace=True)
        btstrp_data = Data(name=self.name + "_btstrp", X=btstr_X, y=btstr_y)
        return btstrp_data
