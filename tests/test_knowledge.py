__author__ = 'V'

import unittest

from MovieBot.knowledge import *

'''
Check that get_titles returns a set of strings which are of the
right length for a movie title
'''


class Test(unittest.TestCase):
    titles = get_titles()

    def test_returned_set(self):
        self.assertTrue(isinstance(self.titles, set))

    def test_size_of_titleset(self):
        self.assertTrue(len(self.titles) > 5)
        self.assertTrue(len(self.titles) < 70)

    def test_movie_names_are_strings(self):
        for item in self.titles:
            self.assertTrue(isinstance(item, basestring))
            self.assertTrue(len(item) > 0)
            self.assertTrue(len(item) < 60)

class Test1(unittest.TestCase):
    def test_special_in(self):
        self.assertTrue(special_in("kajinagar", "kajinagar"))
        self.assertTrue(special_in("raji nagar", "rajinagar"))
        self.assertTrue(special_in("rajinagar", "raji nagara"))
        # other way doesn't work rajinagar != raji nagar

        self.assertFalse(special_in("banerghatta", "dannerghatta"))
        self.assertTrue(special_in("banerghatta", "bannerghatta"))
        self.assertTrue(special_in("bannerghatta", "banerghatta"))


class Test2(unittest.TestCase):
    ntm, ntt, orig_scraped = get_theatres()

    def test_returned_dicts(self):
        self.assertTrue(isinstance(self.ntm, dict))
        self.assertTrue(isinstance(self.ntt, dict))

    def test_dicts_right_size(self):
        self.assertTrue(len(self.ntm.keys()) > 5)
        self.assertTrue(len(self.ntm.keys()) < 70)
        self.assertTrue(len(self.ntt.keys()) > 3)
        self.assertTrue(len(self.ntt.keys()) < 70)

    # very important
    # make sure the google theatre names mapped to the known static BMS names
    # checks that our bms_names in finished namesToTheatres dictionary
    # match the input returned by
    def test_mapping(self):
        enforce_one2one = {}
        for title in self.orig_scraped:
            check, returned = search_theatres(title)
            if not check:
                # print(title, returned)
                pass
            else:
                # print(title, returned.bms_name)
                # check that we haven't already mapped this title
                if returned.bms_name in enforce_one2one:
                    print ('error', returned.bms_name)
                    self.assertTrue(False)
                enforce_one2one[returned.bms_name] = title

'''
todo:
#don't exist in bms
(u'Movieland', '7D Mastiii: Forum Value Mall, Whitefield')
(u'Sri Renuka Prassana', 'Sri Krishna Theatre: KR Puram')
(u'Olympia Theatre', 'Abhinay Theatre: Gandhi Nagar')
(u'Sri Vinayaka Theatre Marathahalli', 'Sri Krishna Theatre: KR Puram')
(u'Sri Radhakrishna', 'Sri Krishna Theatre: KR Puram')
(u'Keshava Theatre Bangalore', '7D Mastiii: Forum Value Mall, Whitefield')

#existing in bms and wrongly mapped
(u'Gopalan Cinemas Arch Mall', 'Gopalan Grand Mall: Old Madras Road')
(u'Pvr Koramangala Gold Cinemas', 'PVR Pepsi IMAX: Koramangala')
(u'Srinivasa Theatre', 'Sri Srinivasa Theatre: Padmanabanagara')


'''
def main():
    unittest.main()


if __name__ == '__main__':
    main()
