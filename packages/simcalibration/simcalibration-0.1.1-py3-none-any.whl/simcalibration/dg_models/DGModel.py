from abc import ABC, abstractmethod
from src.simcalibration.utils.Data import Data


class DGModel(ABC):
    def __init__(self, name: str, SLClass, num_vars: int = 0, learned: bool = False, *args, **kwargs):
        self.SLClass = SLClass
        self.name = name
        self.kwargs = kwargs
        self.model = None
        self.learned = learned
        self.num_vars = num_vars
        if SLClass is not None:
            self.instantiate()

    @abstractmethod
    def instantiate(self) -> None:
        pass

    @abstractmethod
    def fit(self, data: Data, **kwargs) -> None:
        pass

    def generate(self, num_samples: int, outcome_name: str) -> Data:
        if not self.learned:
            raise RuntimeError(f"generate method of '{self.name}' called before learning a data generating model")
        else:
            return self._generate(num_samples, outcome_name)

    @abstractmethod
    def _generate(self, num_samples: int, outcome_name: str) -> Data:
        pass
