
# python standard library
import unittest
import random

# third-party
from mock import MagicMock, call
import numpy

# this package
from tuna.components.iperfquality import IperfMetric


class TestIperfMetric(unittest.TestCase):
    def setUp(self):
        self.aggregator = MagicMock()
        self.iperf = MagicMock()
        self.directions = 'up down'.split()
        self.repetitions = random.randrange(1, 100)
        self.im = IperfMetric(repetitions=self.repetitions,
                              directions=self.directions,
                              iperf=self.iperf,
                              aggregator=self.aggregator)
        return
    
    def test_constructor(self):
        """
        Does it build correctly?
        """
        self.assertEqual(self.repetitions,
                         self.im.repetitions)
        self.assertEqual(self.directions,
                         self.im.directions)
        self.assertEqual(self.iperf,
                         self.im.iperf)
        self.assertEqual(self.aggregator,
                         self.im.aggregator)
        return

    def test_one_call(self):
        """
        Does it act as expected?
        """
        target = MagicMock()
        target.output = None
        target.inputs = [random.randrange(1, 100),
                         random.randrange(2, 100)]
        

        bandwidth = random.randrange(100)
        self.im._aggregator = numpy.median
        self.iperf.return_value = bandwidth        
        # one repetition
        # one direction
        self.im.repetitions = 1
        self.im.directions = 'e'
        outcome = self.im(target)

        arguments = self.get_arguments(target.inputs,
                                       1,
                                       'e')
        self.assertEqual(self.iperf.mock_calls, arguments)
        self.assertEqual(bandwidth, outcome)
        self.assertEqual(target.output, bandwidth)

        # if the output is set, it should ignore
        self.iperf.reset_mock()
        self.im(target)
        self.assertEqual(0, len(self.iperf.mock_calls))
        return

    def test_multiple_calls(self):
        """
        Does it repeat all directions?
        """
        target = MagicMock()
        target.output = None
        outcome = self.im(target)
        self.assertEqual(len(self.iperf.mock_calls),
                         self.repetitions * len(self.directions))
        return

    def test_aggregator(self):
        """
        Does it aggregate the iperf output?
        """
        outputs = list(numpy.random.choice(self.repetitions,
                                           self.repetitions * len(self.directions)))
        expected = list(reversed(outputs))

        def iperf_outputs(*args, **kwargs):
            return outputs.pop()

        self.iperf.side_effect = iperf_outputs
        self.aggregator.return_value = random.randrange(100)
        target = MagicMock()
        target.output = None
        outcome = self.im(target)
        self.assertEqual(outcome, self.aggregator.return_value)
        self.aggregator.assert_called_with(expected)
        return

    def test_filename(self):
        """
        Does it send a sensible filename to the IperfClass?
        """
        target = MagicMock()
        target.inputs = [3, 5]
        target.output = None

        outcome = self.im(target)
        arguments = self.get_arguments(target.inputs, self.repetitions, self.directions)
        self.assertEqual(self.iperf.mock_calls, arguments)
        return

    def get_arguments(self, inputs, repetitions, directions):
        arguments = []
        inputs = "_".join([str(item) for item in inputs])
        for repetition in xrange(repetitions):
            for direction in directions:
                arguments.append(call(direction, 'input_{2}_rep_{0}_{1}'.format(repetition,
                                                            direction,
                                                            inputs)))
        return arguments

