__author__ = 'V'

import unittest

from MovieBot.time import *

class Test(unittest.TestCase):
    t0 = Time('9')
    t1 = Time('9 30')
    t2 = Time('09 30')
    t3 = Time('9 30 pm')
    t4 = Time('11 30 am')
    t5 = Time('9 am')
    t = [t0,t1,t2,t3,t4,t5]
    h = [21,21,21,21,11,9]
    m = [0,30,30,30,30,0]

    def test_parser(self):
        [self.assertEqual(t_i.hours,h_i) for t_i,h_i in zip(self.t,self.h)]
        [self.assertEqual(t_i.minutes,m_i) for t_i,m_i in zip(self.t,self.m)]

    def test_frame(self):
        [self.assertTrue(t_i.get_frame(2)) for t_i in self.t[:3]]
        [self.assertTrue(t_i.get_frame(3)) for t_i in self.t[:3]]
        [self.assertFalse(t_i.get_frame(0)) for t_i in self.t[:3]]
        self.assertTrue(self.t[4].get_frame(0))
        self.assertTrue(self.t[5].get_frame(0))


def main():
    unittest.main()


if __name__ == '__main__':
    main()