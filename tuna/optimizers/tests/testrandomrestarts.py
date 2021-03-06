
# python standard library
import unittest

# third-party
from mock import MagicMock

# this package
from optimization.optimizers.randomrestarts import RandomRestarts


class TestRandomRestarts(unittest.TestCase):
    def setUp(self):
        self.stop_conditions = MagicMock()
        self.stop_condition = MagicMock()
        self.stop_conditions.__iter__.return_value = self.stop_condition
        self.solution_storage = MagicMock()
        self.candidates = MagicMock()
        self.candidates.__iter__.return_value = xrange(10)
        self.quality = MagicMock()
        self.tweak = MagicMock()
        self.global_stop_condition = MagicMock()
        self.optimizer = RandomRestarts(stop_conditions=self.stop_conditions,
                                        is_ideal=self.global_stop_condition,
                                        solution_storage=self.solution_storage,
                                        candidates=self.candidates,
                                        quality=self.quality,
                                        tweak=self.tweak)
        return

    def test_constructor(self):
        """
        Does it build correctly?
        """
        self.assertEqual(self.stop_conditions, self.optimizer.stop_conditions)
        self.assertEqual(self.solution_storage, self.optimizer.solutions)
        self.assertEqual(self.candidates, self.optimizer.candidates)
        self.assertEqual(self.quality, self.optimizer.quality)
        self.assertEqual(self.tweak, self.optimizer.tweak)
        self.assertEqual(self.global_stop_condition, self.optimizer.is_ideal)
        return

    def test_call(self):
        """
        Does the call follow the random-restarts algorithm?
        """
        solution = self.optimizer()
        return
