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
    return ' '.join(tokens), tokens


'''
checks for numbers

tags all tokens with numbers in it. tags tokens which are word numbers, like 'one', 'ten',
all the way up to 'twelve'

tokens is the tokenised input, a list of strings
using regex. used to use the upenn tagset, but it takes like two
seconds per string and its slower

upenn tags: maybe useful for another purpose
ex: nltk.help.upenn_tagset('NN.*')
DT determiner (some, the), PRP pronoun,  CD numeral
JJ adjective, NN noun, VB verb, IN prep/conjunction
'''
def tag_tokens_number(tokens):
    pattern = r"[0-9]+|thirteen|fourteen|fifteen|" \
              r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty"

    #|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|" \
    #          r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand"

    words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight','nine','ten','eleven','twelve']
    tn = [token for token in tokens if re.search(pattern, token) is not None]
    tw = [str(words.index(tok)+1) for tok in tokens if tok in words]
    return tn+tw

'''
checks for times
days of the week, times of the day
'''
def tag_tokens_time(tokens):
    p1 = "(2|to)(nite|night)"
    tokens = [re.sub(p1, "tonight", tok) for tok in tokens]
    p2 = "(2|to)(morrow|moro|morro)"
    tokens = [re.sub(p2, "tomorrow", tok) for tok in tokens]
    pattern = r"morning|evening|night|tonight|today|" \
              r"tomorrow|sun(day)?|mon(day)?|tues(day)?|weds|wednesday|" \
              r"thurs(day)?|sat(urday)?"

    return [token for token in tokens if re.search(pattern, token) is not None]


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
            insertions = previous_row[j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
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
if both words have >= 7 letters, allow for two typos
'''
# todo return to other functions exactly how off the guess is
# possible ways: -1 is failure, 0 is perf(no typos), >= 1 is number of typos, up to 3

def typo(w1, w2):
    w1 = w1.lower()
    w2 = w2.lower()
    if w1 == w2:
        return True

    # can't reliably check short words
    if min(len(w1),len(w2)) <= 2:
        return False

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
    # for middling words
    d = abs(len(w1)-len(w2))
    m = min(len(w1), len(w2))
    if d <= 1:
        if levenshtein(w1, w2) <= 1: return True

    # for larger words, allow greater leeway (2 typos)
    if d <= 2 and m >= 7:
        if levenshtein(w1, w2) <= 2: return True

    if d <= 3 and m >= 11:  # biggest words, allow 3 typos..
        return levenshtein(w1, w2) <= 3

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
    # note that sometimes with long-titled movies, people
    # will shorten it to one or two words, should check for that todo

    # helper function
    # ignore title tokens like '3d' or '2'
    def z(t):
        return not (typo(t, '3d') | typo(t, '2d') | typo(t, '2') | typo(t, '3'))

    title = [t for t in title if z(t)]

    if len(title) == 1:
        if title in tokens:
            return True # can't return false because we haven't checked typos

    for i, tok in enumerate(tokens[:len(tokens)-len(title)+1]):
        if typo(tok, title[0]):
            if recurse(title, tokens[i:i+len(title)]):
                return True
            # else, continue checking
    # if title is more than one word, allow for semi-checks of transient words
    # can easily recode it so that it skips some words in the title(like the, at)
    # if this is useful
    return False

# helper function todo
# need a lot more logic, because often the full address isn't
# mentioned or req'd - change it so that the most common addresses are more likely
# takes list of theatre addresses and breaks it down so that an address in the format
# ["koramangala", "forum mall"] turns into ["koramanagala", "forum", mall"]
# keeps order of theaters, same length as theatres
def secondary_addrs(theatre_addrs):
    t_addrs1 = [] #cut up list so that all words are split up
    for t in theatre_addrs:
        t_i = []
        for a in t:
            if len(a.split()) >1:
                [t_i.append(i) for i in a.split()]
            else:
                t_i.append(a)
        t_addrs1.append(t_i)
    return t_addrs1


# helper function
# primary selects for the most information possible, and in order
def primary(tokens, tc, theatre_addrs):
    ta = [i for i, title in enumerate(theatre_addrs) if look(title, tokens)]
    tb = set(tc) & (set(ta))
    if len(tc) == 0:  # no companies mentioned, so return addresses mentioned
        tfinal = ta
    elif len(ta) == 0:  # no addresses mentioned, so return companies mentioned
        tfinal = tc     # will return empty list if neither mentioned
    elif len(tb) == 0:  # nothing in intersection, but neither are zero, so return smaller
        tfinal = ta
    else:
        tfinal = tb  # items in both sets
    return tfinal

# helper function
# alternative to primary, searches for theatre addresses in the tokens
# more lenient, searches for titles for number of occurences
def secondary(tokens, theatre_addrs):
    t_addrs1 = secondary_addrs(theatre_addrs)
    s = [sum([look(t,tokens) for t in t_addr]) for t_addr in t_addrs1]
    m = max(s)
    if m == 0: return []
    sec = [i for i,s1 in enumerate(s) if s1 == m]
    return sec

'''
tag_tokens_movies()
looking for movie titles, theatre names, addresses

these might be present in full, in part, or with typos
must be lenient
cleans theatre names of certain words(theatre, cinemas)

coiterates through tokens, trying to match it to first movie title
word or movie company word
could potentially match to more than one item, in that case
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
    # todo not all words in movie name required

    tc = [i for i, title in enumerate(theatre_comps) if look(title, tokens)]

    pri = primary(tokens, tc, theatre_addrs)
    sec = secondary(tokens, theatre_addrs)

    if len(pri) ==0: ##AAHHHH SOO MUCH MISSING FKKFKFK
        fin = sec
    else:
        fin = pri
    # need to index into a separate list that contains the theatre name
    found_theatres = [theatres[t].bms_name.lower() for t in fin]

    return found_movies, found_theatres


# for debugging
'''
from knowledge import get_theatres
ntm, ntt, tl = get_theatres()

t = tokeniser("something something put in a movie name max here ok")[1]

fm, ft = tag_tokens_movies(t, ntm, ntt)
'''