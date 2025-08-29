from typing import Union
from src import Data
from src import DGModel
from pgmpy.models import BayesianModel
from pgmpy.estimators import *


class PgmpyModel(DGModel):
    def __init__(self, name, SLClass: Union[HillClimbSearch, TreeSearch, MmhcEstimator, ExhaustiveSearch],
                 outcome_name, **kwargs):
        super().__init__(name=name,SLClass=SLClass, outcome_name=outcome_name, **kwargs)

    def instantiate(self, data=None):#self, data=None):
        pass#self.model = self.SLClass(data=data)

    def fit(self, data, **kwargs):
        est = self.SLClass(data.all)
        best_model = est.estimate()
        self.model = BayesianModel(best_model)
        self.model.fit(data.all)
        self.learned = True
        self.num_vars = len(self.model.nodes)

    def _generate(self, num_samples: int, outcome_name: str, world: str = "real", dataset: str = "train"):

        data = self.model.simulate(n_samples=num_samples)
        data = Data(name=world + self.name + dataset, X=data.drop(outcome_name, axis=1),
                    y=data.loc[:, outcome_name])
        return data
