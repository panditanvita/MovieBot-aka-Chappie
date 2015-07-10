__author__ = 'V'

import re
from knowledge import clean

'''
helper function to cut out the slang
'''
def cut_slang(words):
    # go through common chat slang
    # still need to look out for: brb
    slang = ["tix", "tiks", "wnt", "u", "ty", "thx",
             "pls", "plz", "2moro", "2nite", "gr8"]
    slang = ["(^|\s)" + s + "(\Z|\s)" for s in slang]
    corrections = ["tickets", "tickets", "want", "you", "thanks", "thanks",
                   "please", "please", "tomorrow", "tonight", "great"]
    corrections = [" " + c + " " for c in corrections]
    for i, j in zip(slang, corrections):
        words = re.sub(i, j, words)
    words = words.strip()
    return words


'''
Tokeniser takes in a line of chat text as a string
It attempts to spell-check the string

Returns a cleaned-up string for the chat line content
Returns list of tokens of the cleaned-up string

'''
def tokeniser(inp):
    words = inp.lower()
    # remove punctuation
    words = re.sub(r'''\[\][,;#"'\?()-_`]''', "", words)
    # don't remove punctuation used for time
    words = re.sub(r'(?<=\D)(\.|:)(?=\D?)', r" ", words)
    # cut down whitespace jic
    words = re.sub("\s+", " ", words)
    # correct slang
    words = cut_slang(words)

    # need the ?: to make sure it doesn't return only the ones in parens
    # sneaky regex
    # keep words that aren't ""
    # keep words with hyphens
    # keep time
    pattern = r"\d+[\.:]\d*|(?:[A-Z]\.)+|\w+(?:[-']\w+)*|'|^\w*"
    tokens = re.findall(pattern, words)
    tokens = [token for token in tokens if len(token) > 0]
    return [' '.join(tokens), tokens]


'''
checks for numbers

tokens is the tokenised input, a list of strings
using regex. used to use the upenn tagset, but it takes like two
seconds per string and its slower

upenn tags: maybe useful for another purpose
ex: nltk.help.upenn_tagset('NN.*')
DT determiner (some, the), PRP pronoun,  CD numeral
JJ adjective, NN noun, VB verb, IN prep/conjunction
'''
def tag_tokens_number(tokens):
    pattern = r"[0-9]+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand"

    return [token for token in tokens if re.search(pattern, token) is not None ]

'''
levenshtein edit distance between two strings a,b,
from wikipedia
'''
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

'''
helper function for tag_tokens_movies()
ALL STRING COMPARISONS should be done here to make sure the lower()
is applied evenly
input, two String words
returns True if the words are equal, or equal except for one
substitution OR one insertion OR one deletion typo
'''
# todo return to other functions exactly how off the guess is

def typo(w1, w2):
    w1 = w1.lower()
    w2 = w2.lower()
    if w1 == w2:
        return True
    # check for typos. other ideas: tying in the concept of
    # the letters around a letter on the Qwerty keyboard
    #
    # substitution of one letter/ hammond distance
    if len(w1) == len(w2):
        s = 0
        for i, j in zip(w1, w2):
            if i == j:
                s += 1
        if abs(s-len(w1)) <= 1:
            return True

    # insertion or deletion / levenshtein distance
    if abs(len(w1)-len(w2)) <= 1 and min(len(w1), len(w2)) >= 3:
        if levenshtein(w1, w2) <= 1:
            return True

    return False

'''
helper function for look() in tag_tokens_movies()
matches consecutive words in title with words in tokens
'''
def recurse(title, tokens):
    if len(title) == 0:  # win
        return True
    if len(tokens) == 0:
        return False
    if typo(tokens[0], title[0]):
        return recurse(title[1:], tokens[1:])
    else:
        return False

'''
helper function for tag_tokens_movies()
tokens is String[] of tokenised input
title is a String[] title to search for in the tokens

return Boolean if all consecutive words in title are found in the tokens
'''
def look(title, tokens):
    # helper function
    # ignore title tokens like '3d' or '2'
    # note that sometimes with long-titled movies, people
    # will shorten it to one or two words, should check for that todo
    def z(t):
        if typo(t, '3d') | typo(t, '2d') | typo(t, '2') | typo(t, '3'):
            return False
        return True

    title = [t for t in title if z(t)]

    for i, tok in enumerate(tokens[:len(tokens)-len(title)+1]):
        if typo(tok, title[0]):
            if recurse(title, tokens[i:i+len(title)]):
                return True
            # else, continue checking
    return False

'''
looking for movie titles, theatre names, addresses

uthese might be present in full, in part, or with typos
mst be lenient

coiterates through tokens, trying to match it to first movie title
word or movie company word
uld potentially match to more than one possible, in that case
return all possible
returns list of all movies found, list of all theatres found
as String[] movietitles, String[] theatre names
'''
def tag_tokens_movies(tokens, ntm, ntt):
    movies = ntm.keys()
    theatres = ntt.values()

    ts = clean([t.company for t in theatres])

    theatre_comps = [c.split() for c in ts]
    theatre_addrs = [t.address for t in theatres]

    # check if any movies are mentioned
    found_movies = [title for title in movies if look(title.split(), tokens)]

    # first, check if theatre companies are mentioned. then check
    # if their addresses are mentioned.
    # todo need a lot more logic, because often the full address isn't
    # mentioned or req'd
    tc = [i for i, title in enumerate(theatre_comps) if look(title, tokens)]
    ta = [i for i, title in enumerate(theatre_addrs) if look(title, tokens)]
    tb = set(tc) & (set(ta))
    if len(tc) == 0:
        tfinal = ta
    elif len(ta) == 0:
        tfinal = tc
    elif len(tb) == 0:
        tfinal = tc
    else:
        tfinal = tb
    # need to index into a separate list that contains the theatre name
    found_theatres = [theatres[t].bms_name for t in tfinal]

    return found_movies, found_theatres


# for debugging
#
'''
from knowledge import get_theatres
ntm, ntt, tl = get_theatres()

t = tokeniser("something something put in a movie name here ok")[1]

fm, ft = tag_tokens_movies(t, ntm, ntt)
'''