__author__ = 'V'

import re
from knowledge import clean
from showtime import Time
'''
helper function for tokeniser()
to cut out the text slang
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
called in bot.get_response()
Tokeniser takes in a line of chat text as a string
It attempts to spell-check the string

Returns a cleaned-up string for the chat line content
Returns list of tokens of the cleaned-up string IN ORDER

'''
# possible time regexes, finicky
# do not touch!!
#time = r"\d\d?(?:[\.:\s]?\d{2})?(?:\s?[ap]m)?"
#time = r"(?:\d{3,4}|(?:\d{1,2}[\.:\s]\d{2})|\d)(?:\s?[a|p]m)?" #possible better alternative
time = r'(?:\d{3,4}|(?:\d{1,2}[\.:\s]\d{2})|\d{1,2})(?:\s?[a|p]m)?'

#fix time so that it gets it right, looks for maybe three different times,
#cuts up the string around it and applies the usual
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
    digits = r"(?:\d{4,}[\.: ]?)+"
    acronyms = r"(?:[A-Z]\.)+"
    hyphen = r"\w+(?:[-']\w+)*" #others are mysteriously busted, fix later
    #pattern = r"{}|{}|{}|{}|'|\w+".format(time, digits, acronyms, hyphen)
    tokens = re.findall(r"{}|{}|\w+".format(digits,time), words)
    tokens = [token for token in tokens if len(token) > 0]
    return ' '.join(tokens), tokens

'''
helper function for tags_tokens_number()
tags word-number tokens, like 'one', 'ten',
all the way up to 'twenty', and then 'thirty','forty','fifty'
turns all word-number tokens in numbers
returns full list of tokens in same order, except with word-numbers changed to numbers

note: only done here, and not in general tokeniser, because sometimes the word-number is
used as a movie title or address
possible more robust alternative, is to adjust the string equality typo() function to
accept that 'one'=='1'
'''
def clean_nums(tokens):
    words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
             'eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen',
              'sixteen','seventeen','eighteen','nineteen','twenty']
    other = ['thirty','forty','fifty']
    tws = []
    for tok in tokens:
        if tok in words: tws.append(str(words.index(tok)+1))
        elif tok in other: tws.append(str((other.index(tok)+3)*10))
        else: tws.append(tok)
    return tws
'''
checks for numbers
called in bot.get_response()

tags all tokens with numbers in it.

input: tokens is the tokenised input, a list of strings
if question is 1, it is looking specifically for the number of tickets
if question is 4, it is looking for time of day
returns all_nums, times_of_day, ticket_nums, times

String[] all_nums: anything that matches as a number

String[] times_of_day: returned from helper function to find times of day

Int ticket_num: if asked, returns first number found. if there is a number
in front of the words "tickets" in input, that number overwrites everything

time: looks for times matching time regex

using regex. used to use the upenn tagset, but it takes like two
seconds per string and its slower
upenn tags: maybe useful for another purpose
ex: nltk.help.upenn_tagset('NN.*')
DT determiner (some, the), PRP pronoun,  CD numeral
JJ adjective, NN noun, VB verb, IN prep/conjunction
'''
def tag_tokens_number(tokens, question):
    tokens = clean_nums(tokens)
    # this will not break if the movie title is a number
    # because we are parsing title names somewhere else!
    all_nums = filter(lambda x: re.match(r"\d", x) is not None, tokens)
    times_of_day = tag_tokens_time(tokens)

    # if we are looking specifically for number of tickets, then it just chooses the
    # first number found
    # it looks to see if there was a number mentioned before the word "tickets"
    # and that overrides
    ticket_num = -1
    if question == 1: ticket_num = int(all_nums[0]) # ticket num must be a reasonable number?
    try:
        i = tokens.index("tickets")
        if tokens[i-1] in all_nums: ticket_num = int(tokens[i-1])
    except ValueError: pass

    # looking specifically for a time
    timeList = []
    #if question == 4: todo create a more/less picky option
    def f(tok): #what if you want 2 tickets for 2 pm dummy todo
        return re.match(time,tok) is not None and tok != (str(ticket_num))

    times = [tok for tok in tokens if f(tok)]
    for t in times:
        try: timeList.append(Time(t))
        except AssertionError:
            # this means it matched the time regex but refuses to be parsed by the Time class
            print("your time is weird")

    return all_nums, times_of_day, ticket_num, timeList

'''
helper function for tags_tokens_number()

checks for times
days of the week, times of the day
'''
def tag_tokens_time(tokens):
    p1 = "(2|to)(nite|night)"
    tokens = [re.sub(p1, "tonight", tok) for tok in tokens]
    p2 = "(2|to)(morrow|moro|morro)"
    tokens = [re.sub(p2, "tomorrow", tok) for tok in tokens]
    #pattern = r"morning|afternoon|evening|night|tonight|today|" \
    #          r"tomorrow|sun(day)?|mon(day)?|tues(day)?|weds|wednesday|" \
    #          r"thurs(day)?|sat(urday)?"

    time_tags = ['morning','afternoon','evening','night']
    return [t for token in tokens if sum([typo(t, token) for t in time_tags])>0] #allow for typos here
    #return [token for token in tokens if re.match(r'^{}$'.format(pattern), token) is not None]

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
helper function for tag_tokens_movies(), look(), recurse()

ALL STRING COMPARISONS should be done here to make sure the lower()
is applied evenly
input, two String words
returns True if the words are equal, or equal except for one
substitution OR one insertion OR one deletion typo
if both words have >= 7 letters, allow for two typos

unless the strict flag is on, in which case only allow exact matches
'''
# todo return to other functions exactly how off the guess is
# return it as the second argument
# possible ways: -1 is failure, 0 is perf(no typos), >= 1 is number of typos, up to 3

def typo(w1, w2, strict=False):
    w1, w2 = w1.lower(), w2.lower()
    if w1 == w2: return True

    if strict: return False

    # can't reliably check short words
    if min(len(w1),len(w2)) <= 3: return False

    # check for typos. other ideas: tying in the concept of
    # the letters around a letter on the Qwerty keyboard

    # substitution of one letter/ hammond distance
    if len(w1) == len(w2):
        s = 0
        for i, j in zip(w1, w2):
            if i == j: s += 1
        if abs(s-len(w1)) <= 1: return True

    # insertion or deletion / levenshtein distance
    # for middling words
    d, m = abs(len(w1)-len(w2)), min(len(w1), len(w2))
    if d <= 1:
        if levenshtein(w1, w2) <= 1: return True

    # for larger words, allow greater leeway (2 typos)
    if d <= 2 and m >= 7:
        if levenshtein(w1, w2) <= 2: return True
    # biggest words, allow 3 typos..
    if d <= 3 and m >= 11:  return levenshtein(w1, w2) <= 3
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
optional Boolean arg strict signals to typo whether or not to allow typos, otherwise it just checks
lowercase strings

return Boolean if all consecutive words in title are found in the tokens
'''
def look(title, tokens, strict=False):
    # helper function
    # ignore title tokens like '3d' or '2'
    def z(t):
        return not (typo(t, '3d') | typo(t, '2d') | typo(t, '2') | typo(t, '3'))

    title = [t for t in title if z(t)]

    if len(title)==0: return False
    if len(title) == 1: return sum([typo(title[0],t, strict) for t in tokens])>0
    if len(tokens) < len(title): return False

    for i, tok in enumerate(tokens[:len(tokens)-len(title)+1]):
        if typo(tok, title[0], strict):
            if recurse(title, tokens[i:i+len(title)]):
                return True
            # else, continue checking
    # if title is more than one word, allow for semi-checks of transient words
    # can easily recode it so that it skips some words in the title(like the, at)
    # if this is useful
    return False

'''
 helper function for tags_tokens_movies()
 need a lot more logic, because often the full address isn't
 mentioned or req'd - change it so that the most common addresses are more likely
 takes list of theatre addresses and breaks it down so that an address in the format
 ["koramangala", "forum mall"] turns into ["koramanagala", "forum", mall"]
 keeps order of theaters, same length as theatres
'''
def secondary_keywords(theatre_addrs):
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

'''
 helper function for tags_tokens_movies()
 primary selects for the most information possible, and in order
 returns set of INDICES!
'''
def primary(tokens, tc, theatre_addrs):
    ta = [i for i, title in enumerate(theatre_addrs) if look(title, tokens, True)]
    tb = set(tc) & (set(ta))
    if len(tb) > 0:
        tfinal = tb
    elif ta == 1:
        tfinal = ta
    elif tc == 1:
        tfinal = tc
    else:
        tfinal = tb  # items in both sets, either 0 or something
    return tfinal

'''
 helper function for tags_tokens_movies()
 alternative to primary, searches for theatre addresses in the tokens
 more lenient, searches for titles for number of occurences

 first checks with the Strict flag on, looking for perfect matches, if those don't exist it
 looks for typo-matches
 returns titles with addresses whose keywords have appeared in the input
 the maximum number of times. returns INDICES OF all such titles (max > 0)
'''
def secondary(tokens, titleset):
    s0 = [sum([look([word], tokens, True) for word in title]) for title in titleset if len(title)>0]
    m0 = max(s0)
    if m0==0:
        s = [sum([look([word], tokens) for word in title]) for title in titleset if len(title)>0]
        m = max(s)
        if m == 0: return []
        sec = [i for i,s1 in enumerate(s) if s1 == m]
    else:
        sec = [i for i,s1 in enumerate(s0) if s1 == m0]
    return sec

'''
tag_tokens_movies()
looking for movie titles, theatre names, addresses
called in bot.get_response()

these might be present in full, in part, or with typos
must be lenient
cleans theatre names of certain words(theatre, cinemas)

primary:
coiterates through tokens, trying to match it to first movie title
word or movie company word
could potentially match to more than one item, in that case
return all possible returns list of all movies found, list of all theatres found

secondary:
if the question flag has marked it so that we are specifically looking for a movie
or theatre, it becomes more lenient, using the secondary function instead
secondary function looks for most common occurences/ most overlapping keywords
note that sometimes with long-titled movies and theatres, people
will shorten it to one or two words, so secondary helps with that

as String[] movietitles, String[] theatre names
'''
def tag_tokens_movies(tokens, ntm, ntt, question):
    movies = [k.split() for k in ntm.keys()]
    theatres = ntt.values()

    ts = clean([t.company for t in theatres]) #String[]

    theatre_comps = [c.split() for c in ts]# String[] []
    theatre_keywords = [[t.company] + t.address for t in theatres] #String [] []
    t_addrs1 = secondary_keywords(theatre_keywords) # String [] []

    # check if any movies are mentioned
    mov_pri = [' '.join(title) for title in movies if look(title, tokens)]
    mov_sec = [' '.join(movies[i]) for i in secondary(tokens,movies)]

    if question == 0 and len(mov_pri) ==0: found_movies = mov_sec
    else: found_movies = mov_pri

    # first, check if theatre companies are mentioned. then check
    # if their addresses are mentioned.
    tc = [i for i, title in enumerate(theatre_comps) if look(title, tokens, True)]
    pri = primary(tokens, tc, theatre_keywords)
    sec = secondary(tokens, t_addrs1)
    #important decision here: maybe give it another argument? maybe also include the cinema name
    # todo
    if question == 2 or len(pri) == 0: fin = sec
    else: fin = pri

    # need to index into a separate list that contains the theatre name
    found_theatres = [theatres[t].bms_name.lower() for t in fin]

    return found_movies, found_theatres


# abstraction
# return all tags
def get_tags(tokens, ntm, ntt, question):
    # return the different numbers found in the input
    # tries to tell the difference between number of tickets, t_num
    # times of day, t_day
    # showtimes []Time times
    # for example, looks for a number before "tickets"
    all_nums, tday, t_num, times = tag_tokens_number(tokens, question)

    # return the movies and theatres mentioned in the input
    # can only return known movies and theatres
    # use question to tell which question we are on, for more useful tagging
    tag_movs, tag_theats = tag_tokens_movies(tokens, ntm, ntt, question)

    return tag_movs, tag_theats, all_nums, tday, t_num, times

# for debugging
'''
from knowledge import get_theatres
ntm, ntt, tl = get_theatres()

t = tokeniser("something something cinemax bellandur put in a movie name max here ok")[1]
q=-1
fm, ft = tag_tokens_movies(t, ntm, ntt, q)

'''