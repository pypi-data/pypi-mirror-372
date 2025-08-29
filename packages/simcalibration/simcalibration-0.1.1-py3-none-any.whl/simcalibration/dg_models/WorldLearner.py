import unittest
from WorldLearner import WorldLearner
from pgmpy.models import BayesianModel
import numpy as np
from pgmpy.estimators import PC
import pandas as pd
from pomegranate import BayesianNetwork


class MyTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = pd.DataFrame(np.random.randint(0, 2, size=(20, 2)), columns=list('AB'))

    def test_check_package(self):
        model = WorldLearner(BayesianModel)
        self.assertEqual(model.package, "pgmpy")

    def test_learn_pgmpy(self):
        try:
            model = WorldLearner(PC)
            model.learn(self.data)
        except Exception as exc:
            assert False, f"pgmppy learn raised an exception: {exc}"

    def test_learn_pomegranate(self):
        try:
            model = WorldLearner(BayesianNetwork)
            model.learn(self.data.to_numpy())
        except Exception as exc:
            assert False, f"pomegranate learn raised an exception: {exc}"


if __name__ == '__main__':
    unittest.main()
