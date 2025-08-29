from ml_models.MachineLearner import MachineLearner
import pandas as pd
from src.simcalibration.utils.Data import Data


class SklearnModel(MachineLearner):
    def __init__(self, name, MLClss, preproc_class=None, **kwargs):
        super().__init__(name, MLClss, preproc_class, **kwargs)
        self.kwargs = kwargs
        self.instantiate()

    def instantiate(self):
        self.model = self.MLClss(**self.kwargs)

    def preprocessing(self, train_data):
        pass

    def learn(self, train_data: Data):
        self.instantiate()
        self.model.fit(X=train_data.X, y=train_data.y)

    def predict(self, test_data: Data):
        data = self.model.predict(test_data.X)
        return pd.Series(data, name=test_data.y.name)
