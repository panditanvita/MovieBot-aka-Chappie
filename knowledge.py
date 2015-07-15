"""
Knowledge base for movie bot

Created by web scraping google movie results.
Only *need* to run it once a day, to update. This file doesn't call anything, all methods are called in other
places

WATCH OUT:American spelling is 'theater', so google html code uses that.
Indian/British spelling is 'theatre' and my code uses this!

Speed: takes about five seconds to finish

Testing: Looks right. todo...
"""

from bs4 import BeautifulSoup
import requests
import re
from classes import Movie
from classes import Theatre

start = "http://www.google.com/movies?near=bangalore&date=0&sort=1"

'''
get_titles()

iterate through pages of google 'near bangalore' movie listings.
add all movie titles on page to list of titles.
attempt to continue to next page as long as there
have been new movies added on this page

returns set of title names for movies playing Today
'''


def get_titles(startUrl=start):
    url = startUrl
    title_num = 0
    titles = set()
    c = 1

    while len(titles) != title_num or c:
        c = 0
        title_num = len(titles)
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            print("Err: Failed to connect to the internet")
            return
        soup = BeautifulSoup(r.text, from_encoding="utf-8")

        movies_html = soup.find_all("div", attrs={'class': 'movie'})
        mov1 = [mov.find('h2') for mov in movies_html if mov.find('h2')]
        [titles.add(m1.text) for m1 in mov1]
        url = startUrl + "&start=" + str(len(titles))
    return titles

# list of titles by date. example of parsed titles from June 30th
titles0630 = set([u'Pandaga Chesko', u'Krishna Leela', u'Yagavarayinum Naa Kaakka', u'Inside Out 3d',
                  u'Jurassic World', u'Vajrakaya', u'Indru Netru Naalai', u'Dil Dhadakne Do', u'Hamari Adhuri Kahani',
                  u'Tiger', u'Abcd 2', u'Tanu Weds Manu Returns', u'Miss Tanakpur Haazir Ho', u'Me', u'Kaaka Muttai',
                  u'Where Is Vidya Balan', u'Spy', u'Jadoogadu', u'Romeo Juliet', u'Ganapa', u'Insidious Chapter 3',
                  u'Labour Of Love', u'Lodukku Pandi', u'Entourage', u'Goolihatti', u'Mr And Mrs Ramachari', u'Ranna',
                  u'Aata Paata', u'Premam', u'Bela Sheshe', u'Thinkal Muthal Velli Vare'])


'''
parse_theatres()

all 81 known theatres in bangalore are saved in bms_theatres.txt.
file is edited for uniformity (Theatre name: Address, Region, whatever)
open file and parse titles into Theatre objects
-removes the word bangalore/bengaluru from title
(file has been edited: banerghatta to bannerghatta, rajajinagar to
rajaji nagar)

deletes current set of theatres before starting

This is the only time that Theatre instances are initialised.
All other accesses are to modify the movies attribute
of a particular theatre
Must be called before anything else references to Theatres

example lines from bms_theatres:
Innovative Multiplex: Marathahalli
INOX Lido: Off MG Road, Ulsoor
INOX: Forum Value Mall, Whitefield
INOX: Jayanagar - Garuda Swagath Mall
'''
def parse_theatres():
    Theatre.theatres = []
    with open('bms_theatres', mode='r') as f:
        line = f.readline().strip()
        while line:
            if len(line) > 15:
                ind = re.match(r"^(\w+(\s?))+", line).end()
                company = line[:ind]
                # split the address into list of region, mall, street
                address = re.split("\s\-\s|,\s", line[ind+2:])
                address = [a for a in address if a.lower() != ("bengaluru" or "bangalore")]

                theatre = Theatre(line, address, company)
            line = f.readline().strip()
    return


'''
helper function for get_theatres

'''
def clean_inp(inp):
    inp = inp.lower()
    # manual special cases
    known_not_in_bms = set([u.lower() for u in [u'Sri Radhakrishna',
    u'Sri Vinayaka Theatre Marathahalli', u'Olympia Theatre',
    u'Sri Renuka Prassana', u'Movieland']])
    if inp in known_not_in_bms:
        return False, "Err: Not in the book my show theatre listing"
    # special cases,
    # rockline cinema means rockline mall
    if "rockline" in inp:
        inp += " carnival"

    return True, inp

'''
sometimes address names have gaps, cannot directly do
a string comparison. promoting uniformity in bms_theatres file,
hence must be lenient with scraping names
ex: rajajinagar == rajaji nagar
banerghatta == bannerghatta
function checks if String addr is in String check_in, returns boolean
'''
def special_in(addr, check_in):
    if addr in check_in:
        return True
    i1 = re.search(r"\Snagar|\snagar", addr)
    if i1 is not None:
        i = i1.start()
        if addr[:i + 1] + ' ' + addr[i + 1:] in check_in:
            return True
        if addr[:i] + addr[i + 1:] in check_in:
            return True
    i2 = re.search(r"banerghatta|bannerghatta", addr)
    if i2 is not None:
        i = i2.start()
        if addr[:i] + "banerghatta" in check_in:
            return True
        if addr[:i] + "bannerghatta" in check_in:
            return True
    return False


'''
clean(t)
helper function for search_theatres()
cleaning out unnecessary words from theatre names set
input: list of String theatre names
returns: list of String theatre names
'''
def clean(t):
    superfluous = ["cinema(s?)(\s|\Z)", "theatre(s?)", "digital 2k", "digital 4k"]
    t2 = []
    for word in t:
        word = word.lower()
        for s in superfluous:
            word = re.sub(s, "", word)
        t2.append(word.strip())
    return t2

'''
search_theatres()

takes in String name, s scraped google theatre name, and matches it to a
single known theatre. must match to a single known theatre, otherwise it fails
(not the same as searching customer input theatre, because
there is no option for anyone to narrow down the search, but similar)

returns tuple of (Boolean found_instance, Theatre instance | error message)
'''

def search_theatres(inp):
    theatre_names = [t.company.lower() for t in Theatre.theatres]

    check, inp = clean_inp(inp)
    if not check:
        return check, inp

    theatre_names2 = clean(theatre_names)

    # checking if we can narrow it down by searching for the company name
    # in our input string

    # get the number of maximum matched words
    def add_c(x):
        return sum([1 for j in x.split() if special_in(j, inp)])

    check = [(add_c(x), i) for i, x in enumerate(theatre_names2)]

    m = max([c[0] for c in check])
    if m == 0:
        return False, "Err: Nothing matched"
    # find number of theatres which are equally max. matched
    # create list of such theatres to narrow down further
    # check = (num_occurences, index) []
    check = [c for c in check if c[0] == m]

    if len(check) == 1:
        # got it
        theatre = Theatre.theatres[check[0][1]]
    else:  # len(check) > 1
        # must narrow down further, check locations for all the company names
        # that the input matched to
        theatre_locs = [t.address for t in [Theatre.theatres[i] for num, i in check]]
        theatre_locs = [[a.lower() for a in address] for address in theatre_locs]
        # choose the address which has the most keywords in common
        check2 = [sum([(special_in(i, inp)) for i in t]) for t in theatre_locs]
        # potential bug! if there is more than one option left here,
        # it just chooses the first option
        theatre = Theatre.theatres[check[check2.index(max(check2))][1]]
    return True, theatre

'''
get_theatres():

iterate through google theatre listings
add theatres to dictionary, mapped to the movies they are showing
edits movies in dictionary

must have internet connection, otherwise returns False

invariants for namesToMovies and namesToTheatres:
we want the Movie and Theatres objects to have properly
capitalised names, but the key mappings should
all be lowercase

Movies keep track of String[] theaternames and Theaters keep track of
{String moviename:timings}. Hence getTheatres() returns two dictionaries
with the final dictionaries of Movies and Theatres. All edits should be
made directly to the dictionary, to make sure everything points to a single
instance of a movie/theatre. also returns a list of the original
google-scraped theatre names for testing

'''


def get_theatres():
    parse_theatres()

    namesToMovies = {}
    namesToTheatres = {}
    startUrl = "http://www.google.com/movies?near=bangalore&date=0"
    url = startUrl
    c = 1
    theatres = []
    theatreList = []
    while len(theatres) != 0 or c:
        c = 0
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            print("Err: Failed to connect to the internet")
            return False
        soup = BeautifulSoup(r.text, from_encoding="utf-8")

        # numTheatres = len([m.start() for m in re.finditer('class=theater', r.text)])

        theatres = soup.find_all("div", attrs={'class': 'theater'})
        for t in theatres:
            name = t.find('h2', class_='name')
            try:
                name = name.text
            except AttributeError:
                print("Err: theatre name doesn't exist")
                continue

            theatreList.append(name)

            # match theatres found to a single known theatre
            check, theatre = search_theatres(name)

            if not check:
                #print(name, theatre)
                continue
            known_name = theatre.bms_name.lower()
            namesToTheatres[known_name] = theatre

            # for each movie in the theater
            # create movie if it doesn't exist
            movs = t.find_all("div", class_='movie')

            for mov in movs:
                movieName = mov.find(class_='name')
                try:
                    movieName = movieName.text
                except AttributeError:
                    print("Err: movie name doesn't exist")
                    continue
                if len(movieName) > 80:
                    print('Err: Text too long for movie name')
                    continue  # todo, common known bug, parsed incorrectly somehow

                times = [i.text.replace('&nbsp', '').strip() for i in mov.find_all(attrs={'style': 'color:'})]
                # write something to parse times without am/pm TODO

                if movieName.lower() not in namesToMovies.keys():
                    namesToMovies[movieName.lower()] = Movie(movieName)
                # add theatre to movie listing
                namesToMovies[movieName.lower()].put(known_name)

                # add movie to theatre listing
                # keep timings in theatre listing
                namesToTheatres[known_name].put(movieName.lower(), times)

        url = startUrl + "&start=" + str(len(theatreList))

    print("Knowledge base loaded")
    return namesToMovies, namesToTheatres, theatreList
