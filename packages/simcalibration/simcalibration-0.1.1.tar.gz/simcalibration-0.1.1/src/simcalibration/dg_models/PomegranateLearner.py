from src.simcalibration.dg_models.DGModel import DGModel
from pomegranate.BayesianNetwork import BayesianNetwork
from src.simcalibration.utils.Data import Data
from abc import ABC, abstractmethod


class PomegranateLearner(DGModel):
    def __init__(self, name,SLClass: str, algorithm: str = "greedy", **kwargs):
        super().__init__(name=name, SLClass=SLClass,**kwargs)
        self.algorithm = algorithm

    def instantiate(self):
        pass

    def fit(self, data, **kwargs):
        data = data.all
        output = BayesianNetwork.from_samples(X=data,algorithm="greedy")
        self.model = BayesianNetwork.from_samples(X=data)#, algorithm='exact-dp')#, state_names=data.columns.values)
        self.model = self.model.fit(X=data)

    def _generate(self, num_samples, outcome_name: str, world: str = "real", dataset: str = "train"):
        data = self.model.sample(n=num_samples)
        data = Data(name=world + self.name + dataset, X=data.drop(outcome_name, axis=1),y=data.loc[:, outcome_name])
        return data

class SomeAbstractClass(ABC):
    @abstractmethod
    def get(self, *args, **kwargs):
        """
        Returns smth
        """

    @abstractmethod
    def set(self, key, value):
        """
        Sets smth
        """


class Implementation(SomeAbstractClass):
    def set(self, key, value):
        pass

    def get(self, some_var, another_one):
        pass
# if __name__ == "__main__":
#
