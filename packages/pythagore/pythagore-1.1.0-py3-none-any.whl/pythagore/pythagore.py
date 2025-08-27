import math

class Pythagore:

    """
    The Pythagoras class makes it easier to calculate the Pythagorean theorem.
    """

    # parameter OP the largest side, the other two parameters are the other values ​​of the rectangle
    @staticmethod
    def is_rectangle(hypotenuse, cote_a, cote_b):
        result_op = math.pow(hypotenuse, 2)
        pn = math.pow(cote_a, 2)
        no = math.pow(cote_b, 2)
        result = pn + no
        if result_op != result:
            return False
        return True
        
    # hypotenus parameter, one side to find the missing side
    @staticmethod 
    def adjacent_side(hypotenuse, other_side):
        return math.sqrt(pow(hypotenuse, 2) - pow(other_side, 2))

    # the two sides of the triangle to find the hypotenus
    @staticmethod
    def hypotenus(cote_a, cote_b):
        return math.sqrt(math.pow(cote_a, 2) + math.pow(cote_b, 2))
    

