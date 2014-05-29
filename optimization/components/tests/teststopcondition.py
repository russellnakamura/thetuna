
# python standard library
import unittest
import random

# third-party
from mock import MagicMock, patch

# this package
from optimization.components.stopcondition import StopCondition, StopConditionIdeal


class TestStopCondition(unittest.TestCase):
    def setUp(self):
        self.time_mock = MagicMock(name='time')
        self.end_time = random.randrange(100)
        self.time_limit = random.randrange(100)
        self.condition = StopCondition(end_time=self.end_time,
                                       time_limit=self.time_limit)
        return
        
    def test_constructor(self):
        """
        Does it build?
        """
        self.assertEqual(self.time_limit, self.condition.time_limit)
        self.assertEqual(self.condition.end_time, self.end_time)
        return

    def test_end_time(self):
        """
        Does it set the end-time?
        """
        current_time = random.randrange(100)
        self.time_mock.return_value = current_time
        self.condition._end_time = None
        with patch('time.time', self.time_mock):
            self.assertEqual(self.time_limit + current_time,
                             self.condition.end_time)
        return

    def test_call(self):
        """
        Does it stop when it's out of time?
        """
        # is it callable?
        solution = random.randrange(10)
        self.condition(solution)

        # does it time out?
        self.condition._end_time = random.randrange(100)
        
        self.time_mock.return_value = self.condition._end_time - 1
        with patch('time.time', self.time_mock):
            self.assertFalse(self.condition())

        self.time_mock.return_value = self.condition._end_time + 1
        with patch('time.time', self.time_mock):
            self.assertTrue(self.condition())
        return

    def test_set_time(self):
        """
        Does setting the total time reset the time?
        """
        new_time = random.randrange(100)
        ctime = random.randrange(20)
        self.condition.time_limit = new_time
        self.time_mock.return_value = ctime
        with patch('time.time', self.time_mock):
            self.assertEqual(self.condition.end_time,
                             new_time + ctime)
        return


class TestStopConditionIdeal(unittest.TestCase):
    def setUp(self):
        self.time_mock = MagicMock(name='time')
        self.end_time = random.randrange(100)
        self.time_limit = random.randrange(100)
        self.ideal_value = random.randrange(100)
        self.condition = StopConditionIdeal(end_time=self.end_time,
                                       time_limit=self.time_limit,
            ideal_value=self.ideal_value)

        return
    
    def test_constructor(self):
        """
        Does it build?
        """
        self.assertIsInstance(self.condition, StopCondition)
        return

    def test_timeout(self):
        """
        Does it stop if it times-out?
        """
        # does it time out?
        self.condition._end_time = random.randrange(100)
        
        self.time_mock.return_value = self.condition._end_time - 1

        # make sure it doesn't reach a good solution
        solution = MagicMock()
        solution.output = self.condition.ideal_value + 2
        solution.delta = 0
        with patch('time.time', self.time_mock):
            self.assertFalse(self.condition(solution))

        self.time_mock.return_value = self.condition._end_time + 1
        with patch('time.time', self.time_mock):
            self.assertTrue(self.condition(solution))
        return

    def test_ideal_reached(self):
        """
        Does it stop if the ideal-value is reached?
        """
        # make sure it doesn't time out
        self.condition.delta = 0.1
        self.time_mock.return_value = self.condition._end_time - 1
        candidate = MagicMock()
        candidate.output = self.condition.ideal_value - 1
        
        with patch('time.time', self.time_mock):
            msg = "Candidate: {0}, Ideal: {1}".format(candidate.output,
                                                      self.condition.ideal_value)
            self.assertFalse(self.condition(candidate),
                             msg=msg)

            self.condition.delta = 10
            candidate.output = random.choice((self.condition.ideal_value,
                                       self.condition.ideal_value + 1))
            msg = "Candidate: {0}, Ideal: {1}".format(candidate.output,
                                                      self.condition.ideal_value)

            self.assertTrue(self.condition(candidate), msg=msg)            
        return


# this package
from optimization.components.stopcondition import StopConditionGenerator


class TestStopConditionGenerator(unittest.TestCase):
    def setUp(self):
        self.time_limit = random.randrange(1, 100)
        self.maximum_time = random.randrange(100, 200)
        self.minimum_time = random.randrange(100)

        self.end_time = random.randrange(100)
        self.ideal = random.randrange(100)
        self.delta = random.random()
        self.random_uniform = MagicMock()
        self.generator = StopConditionGenerator(time_limit=self.time_limit,
                                                end_time=self.end_time,
                                                minimum_time=self.minimum_time,
                                                maximum_time=self.maximum_time,
                                                ideal=self.ideal,
                                                delta=self.delta,
                                                random_function=self.random_uniform,
                                                use_singleton=False)
        return
    
    def test_constructor(self):
        """
        Does it build correctly?
        """
        self.assertEqual(self.time_limit, self.generator.time_limit)
        self.assertEqual(self.minimum_time, self.generator.minimum_time)
        self.assertEqual(self.end_time, self.generator.end_time)
        self.assertEqual(self.ideal, self.generator.ideal)
        self.assertEqual(self.delta, self.generator.delta)
        self.assertFalse(self.generator.use_singleton)
        self.assertEqual(self.random_uniform, self.generator.random_function)
        self.assertEqual(self.maximum_time, self.generator.maximum_time)
        return

    def test_stop_condition(self):
        """
        Does it create a stop-condition?
        """
        # default is to create a singleton
        # with no ideal given, it should be the time-based one only
        generator = StopConditionGenerator(time_limit=self.time_limit,
                                           maximum_time=self.maximum_time,
                                           minimum_time=self.minimum_time,
                                           random_function=self.random_uniform)
        #condition = generator.stop_condition
        return

    def test_end_time(self):
        """
        Does it set a ctime based on the time-limit?
        """
