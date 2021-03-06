
# python standard library
import unittest
import random

# third-party
from mock import MagicMock

# this package
from tuna.components.composite import SimpleComposite


class TestSimpleComposite(unittest.TestCase):
    def setUp(self):
        self.composite = SimpleComposite()
        return
    
    def test_constructor(self):
        """
        Does it build correctly?
        """
        components = [MagicMock() for component in xrange(random.randrange(1, 100))]
        composite = SimpleComposite(components)
        self.assertIs(components, composite.components)
        return

    def test_add(self):
        """
        Does it add components correctly?
        """
        leaf = MagicMock()
        self.assertNotIn(leaf, self.composite)
        self.composite.add(leaf)
        self.assertIn(leaf, self.composite)
        return

    def test_remove(self):
        """
        Does it remove components?
        """
        leaf = MagicMock()
        self.composite.add(leaf)
        self.assertIn(leaf, self.composite)
        self.composite.remove(leaf)
        self.assertNotIn(leaf, self.composite)
        return

    def test_remove_non_existent_leaf(self):
        """
        Is it safe to try to remove a leaf not in the composites?
        """
        leaf = MagicMock()
        self.assertNotIn(leaf, self.composite)
        self.composite.remove(leaf)
        return

    def test_call(self):
        """
        Does it pass on the call to components?
        """
        leafs = [MagicMock() for leaf in xrange(random.randrange(100))]
        composite = SimpleComposite(components=leafs)
        value = random.randrange(100)
        argy = random.randrange(100)
        composite(argy=argy)
        for leaf in leafs:
            leaf.assert_called_with(argy=argy)

        # only keyword arguments are allowed
        with self.assertRaises(TypeError):
            composite(value, argy=argy)
        return
