
# python standard library
import unittest
import random

# third party
from mock import MagicMock, call

# this package
from optimization.optimizers.hillclimber import HillClimber


class TestHillClimber(unittest.TestCase):
    def setUp(self):
        self.solution = random.randrange(1000)
        self.tweak = MagicMock()
        self.quality = MagicMock()
        self.timeout = MagicMock()
        
        self.optimizer = HillClimber(solution=self.solution,
                                tweak=self.tweak,
                                quality=self.quality,
                                stop_condition=self.timeout)
        return

    def test_constructor(self):
        """
        Does it build?
        """
        self.assertEqual(self.solution, self.optimizer.solution)
        self.assertEqual(self.tweak, self.optimizer.tweak)
        self.assertEqual(self.quality, self.optimizer.quality)
        self.assertEqual(self.timeout, self.optimizer.stop_condition)
        return

    def test_one_loop(self):
        """
        Does it execute the hill-climbing algorithm?
        """
        solution = self.optimizer()
        self.assertEqual(solution, self.solution)
        # one-loop
        conditions = [True, False]
        def stop_effect(*args, **kwargs):
            return conditions.pop()
        self.timeout.side_effect = stop_effect

        tweaks = [3]
        def tweak_effects(*args, **kwargs):
            return tweaks.pop()
        self.tweak.side_effect = tweak_effects

        qualities = {self.solution:0, 3:1}
        def quality_effects(*args, **kwargs):
            return qualities[args[0]]
        self.quality.side_effect = quality_effects
        
        solution = self.optimizer()
        
        self.assertEqual([call(self.solution)], self.tweak.mock_calls)
        for called in [call(self.solution), call(3)]:
            self.assertIn(called, self.timeout.mock_calls)

        self.assertEqual(solution, 3)
        return
