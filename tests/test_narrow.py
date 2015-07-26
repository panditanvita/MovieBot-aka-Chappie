__author__ = 'V'

import unittest

from MovieBot.logic import *

from knowledge import get_info

class Test_narrow(unittest.TestCase):
    req1, req2, ntm, ntt = get_info()

    def test_narrow_movies(self):
        tag_movs = []
        r1 = narrow_movies(self.req1,tag_movs,self.ntm)
        self.assertEqual(r1, (0,"What movie?"))

        tag_movs = ['zabod']
        r1_ = narrow_movies(self.req1, tag_movs, self.ntm)
        self.assertEqual(r1_, (0,"What movie?"))

        r1_1 = narrow_movies(self.req2, tag_movs, self.ntm)
        self.assertEqual(r1_1, (1,""))


    def test_narrow_theatres(self):
        tag_theats = ['t1']
        r2 = narrow_theatres(self.req1,tag_theats,self.ntt)

        self.assertTrue(r2, (0, "At which theatre?"))


    def test_narrow_num(self):
        self.assertTrue(True)



def main():
    unittest.main()


if __name__ == '__main__':
    main()