from app.models import Estimator
from app import db
import unittest

class EstimatorModelTestCase(unittest.TestCase):
    def test_numberical_features(self):
        n_features = ['n_1', 'n_2', 'n_3']
        est = Estimator(numerical_features=n_features, target='duration')
        est2 = Estimator(target='duration')
        self.assertTrue(est.numerical_features is not None)
        self.assertTrue(est2.numerical_features is not None)
        self.assertTrue(est2.numerical_features == [])
        self.assertTrue(est.numerical_features == n_features)

    def test_text_features(self):
        t_features = ['t_1', 't_2', 't_3']
        est = Estimator(text_features=t_features, target='duration')
        est2 = Estimator(target='duration')
        self.assertTrue(est.text_features is not None)
        self.assertTrue(est2.text_features is not None)
        self.assertTrue(est.text_features == t_features)
        self.assertTrue(est2.text_features == [])



