from src.simcalibration.utils.Data import Data
from src.simcalibration.dg_models.DGModel import DGModel


class Bnlearner(DGModel):
    def __init__(self, name, SLClass: str, **kwargs):
        super().__init__(name=name,SLClass=SLClass, **kwargs)

    def instantiate(self):
        pass

    def fit(self, data, **kwargs):
        self.learned = True

    def _generate(self, num_samples: int, outcome_name: str, world: str = "real", dataset: str = "train"):
        data = self.model.simulate(n_samples=num_samples)
        data = Data(name=world + self.name + dataset, X=data.drop(outcome_name, axis=1),y=data.loc[:, outcome_name])
        return data
