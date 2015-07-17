__author__ = 'V'


'''
Need to test tokeniser on all kinds of expected inputs

TODO


'''
import unittest
from MovieBot.tokeniser import *
from MovieBot.knowledge import get_theatres

class TestTokeniser(unittest.TestCase):
    inps = ["some slang tix jatiks wnt u to ty thx " +
            "pls plz 2moro 2nite ok gr8", "ra.#@^ndom puncti.f:ftion.",
            " c   ut wh  ite spa  ce",
            "keep 9.30 10:45 time intact."]
    anss = [('some slang tickets jatiks want you to thanks thanks please please tomorrow tonight ok great',
             ['some', 'slang', 'tickets', 'jatiks', 'want',
              'you', 'to', 'thanks', 'thanks', 'please', 'please',
              'tomorrow', 'tonight', 'ok', 'great']),
            ('ra ndom puncti f ftion', ['ra', 'ndom', 'puncti', 'f', 'ftion']),
            ('c ut wh ite spa ce', ['c', 'ut', 'wh', 'ite', 'spa', 'ce']),
            ('keep 9.30 10:45 time intact',
             ['keep', '9.30', '10:45', 'time', 'intact'])]

    def test_tokeniser(self):
        for i, j in zip(self.inps, self.anss):
            self.assertTrue(tokeniser(i) == j)

    def test_times(self):
        self.assertTrue(re.match(time,"9") is not None)
        self.assertTrue(re.match(time,"9 30") is not None)
        self.assertTrue(re.match(time,"930") is not None)
        self.assertTrue(re.match(time,"9.30") is not None)
        self.assertTrue(re.match(time,"9 pm") is not None)
        self.assertTrue(re.match(time,"1930") is not None)
        self.assertTrue(re.match(time,"1930 pm") is not None)
        self.assertTrue(re.match(time,"9 00 am") is not None)
        self.assertTrue(re.match(time,"11 30 am") is not None)
        self.assertTrue(re.match(time,"11") is not None)
        self.assertTrue(re.match(time,"9") is not None)
        self.assertTrue(re.match(time,"9 ") is None)
        self.assertTrue(re.match(time,"99999") is None)

    tokens = ["i'm", 'going', 'at', 'ten', 'o', 'clock', 'to', 'the',
              '9.45', 'showing', 'and', 'then', 'the', 'ten-thirty', 'showing']
    #ans2 = ['10', '9.45', 'ten-thirty']
    ans2 = ['10', '9.45']

    def test_tags_tokens(self):
        question = -1
        self.assertTrue(tag_tokens_number(self.tokens, question)[0] == self.ans2)
        self.assertTrue(tag_tokens_number(self.tokens, question)[2] == -1)

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
        k = self.ntm.keys()[4:8]
        movies = [k1.split() for k1 in k]

        starts = [tokeniser('i want to see')[1], tokeniser('please')[1], tokeniser('tickets for')[1]]

        tokens = [starts[0]+movies[0], movies[1]+starts[1], starts[2]+movies[2]+starts[1]]
        q = -1
        r0 = tag_tokens_movies(tokens[0], self.ntm, self.ntt, q)
        r1 = tag_tokens_movies(tokens[1], self.ntm, self.ntt, q)
        r2 = tag_tokens_movies(tokens[2], self.ntm, self.ntt, q)

        self.assertEqual(r0[0], [k[0]])
        self.assertEqual(r1[0], [k[1]])
        self.assertEqual(r2[0], [k[2]])



def main():
    unittest.main()


if __name__ == '__main__':
    main()
