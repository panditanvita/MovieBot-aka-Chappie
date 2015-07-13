__author__ = 'V'


'''
Need to test tokeniser on all kinds of expected inputs

TODO


'''
import unittest
from MovieBot.tokeniser import *
from MovieBot.knowledge import get_theatres

class Test(unittest.TestCase):
    inps = ["some slang tix jatiks wnt u to ty thx " +
            "pls plz 2moro 2nite ok gr8", "ra.#@^ndom puncti.f:ftion.",
            " c   ut wh  ite spa  ce",
            "keep 9.30 10:45 time intact."]
    anss = [['some slang tickets jatiks want you to thanks thanks please please tomorrow tonight ok great',
             ['some', 'slang', 'tickets', 'jatiks', 'want',
              'you', 'to', 'thanks', 'thanks', 'please', 'please',
              'tomorrow', 'tonight', 'ok', 'great']],
            ['ra ndom puncti f ftion', ['ra', 'ndom', 'puncti', 'f', 'ftion']],
            ['c ut wh ite spa ce', ['c', 'ut', 'wh', 'ite', 'spa', 'ce']],
            ['keep 9.30 10:45 time intact',
             ['keep', '9.30', '10:45', 'time', 'intact']]]

    def test_tokeniser(self):
        for i, j in zip(self.inps, self.anss):
            self.assertTrue(tokeniser(i) == j)

    tokens = ["i'm", 'going', 'at', 'ten', 'o', 'clock', 'to', 'the',
              '9.45', 'showing', 'and', 'then', 'the', 'ten-thirty', 'showing']
    ans2 = ['ten', '9.45', 'ten-thirty']

    def test_tags_tokens(self):
        self.assertTrue(tag_tokens_number(self.tokens) == self.ans2)

    t1 = ['i', 'want', 'to', 'see', 'Spy']
    t2 = ["give", "tickets", "for", "jurassic", "world", "please"]
    t3 = ["halli", "malli", "walli"]

    def test_look(self):
        self.assertTrue(look("spy".split(), self.t1))
        self.assertTrue(look("jurassic world".split(), self.t2))
        self.assertTrue(look("halli malli walli".split(), self.t3))
        self.assertFalse(look("spy".split(), self.t2))
        self.assertFalse(look("jurassic world".split(), self.t1))

    ntm, ntt, tl = get_theatres()

    def test_tagMoviesAndTheatres(self):
        self.assertTrue()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
