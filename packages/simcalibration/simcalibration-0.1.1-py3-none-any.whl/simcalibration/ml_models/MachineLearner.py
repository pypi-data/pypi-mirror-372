from abc import ABC, abstractmethod
from src.simcalibration.utils.Data import Data
import pandas as pd


class MachineLearner(ABC):
    def __init__(self, name, MLClss, preproc_class=None, **kwargs):
        self.name = name
        self.MLClss = MLClss
        self.model = None
        if preproc_class is not None:
            self.preprocess = True
        self.trained = False
        self.kwargs = kwargs

    @abstractmethod
    def instantiate(self) -> None:
        self.model = self.MLClss(**self.kwargs)

    @abstractmethod
    def preprocessing(self, train_data: Data) -> Data:
        pass

    @abstractmethod
    def learn(self, train_data: Data) -> None:  # make sure to re-instantiate the model each time you train it
        pass

    @abstractmethod
    def predict(self, test_data: Data) -> pd.Series:
        pass
