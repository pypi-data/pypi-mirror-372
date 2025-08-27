import sys
import os
import unittest

# python -m unittest test_pythagore.py

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from pythagore import Pythagore


class TestHypotenuse(unittest.TestCase):

    def setUp(self):
        self.a = 3
        self.b = 4
        self.pythagore = Pythagore()
        self.hypotenuse = self.pythagore.hypotenus(self.a, self.b)

    def test_hypotenuse(self):

        self.assertEqual(self.pythagore.hypotenus(self.a, self.b), 5)

    def test_other_side(self):

        self.assertEqual(self.pythagore.adjacent_side(self.hypotenuse, self.a), self.b)
    
    def test_is_rectangle(self):
        
        self.assertEqual(self.pythagore.is_rectangle(self.hypotenuse, self.a, self.b), True)

        self.assertNotEqual(self.pythagore.is_rectangle(self.hypotenuse, self.a, self.b), False)



if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)