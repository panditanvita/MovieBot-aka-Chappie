__author__ = 'V'

'''
logic submodule

finally, decisions: do we have enough information?
which questions must we ask to get more information?
maybe the selected movie is not playing in the selected theatre?
give alternate showtimes


submodule for each attribute, each function
makes sure that what it inputs into the movie request is
correct. takes in chatline information
'''

'''
narrow_down_movies()
input: list of movies, found_movies. len(found_movies) should be 3 or less

if there are no movies, return 0, "err:"
if there is only one movie, then it updates the movie request, returns
1, ""
if there is more than one movie, return 2, [question]
else, it returns a question to diffrentiate between the movies
'''
def narrow_down(found_movies):
    #todo
    n = len(found_movies)
    if n == 0:
        return 0, "Found no movies"
    if n == 1:
        return True, found_movies[0]
    return 2, "Too many movies"


'''
narrow()
input: MovieRequest object and several lists of tags. Movie and Theatre names must be
keys into their respective maps
takes and fills in a MovieRequest object based on the most likely
outputs.
if there is only one movie and/or theatre, input into request, return 1
if there is more than one, send in a question to narrow it down
need to make sure the ticket is valid!

assuming time is for today

returns returned1,returned2, a tuple of results for movies, theatres
'''
def narrow(req, tag_movs, tag_theats, tag_number, tag_times, ntm, ntt):
    returned1 = 0, "Which movie?"
    returned2 = 0, "At which theatre?"

    if narrow_down(tag_movs)[0] == 1:
        m_nice = ntm[tag_movs[0]]
        req.add_title(m_nice)
        returned1 = 1, ""

    if narrow_down(tag_movs)[0] > 1:
        statement = '\n'.join(['{}. {}'.format(i, t) for i, t in enumerate(tag_movs)])
        returned1 = 2, "Possible options: " + statement

    if narrow_down(tag_theats)[0] == 1:
        t = tag_theats[0]
        t_nice = ntt[t].bms_name
        if req.done[0]:
            # check if movie is in theatre today
            d = ntt[t].movies
            if len(d.get(req.title, [])) == 0:
                returned2 = 0, "Sorry, but {} isn't showing at {} today.".format(req.title, t_nice)
            else:
                returned2 = 2, "Possible showings: " + d.get(req.title)
        else:
            req.add_theatre(t_nice)
            returned2 = 1, ""

    if narrow_down(tag_theats)[0] > 1:
        # check which all are playing if movie is mentioned
        # then return subset or full set of tag_theats
        ft = tag_theats
        if req.done[0]:
            ft = [t for t in tag_theats if len(ntt[t].movies.get(req.title, [])) < 0]
        statement = '\n'.join(['{}. {}'.format(i, t) for i, t in enumerate(ft)])
        returned2 = 2, "That movie is playing in: " + statement

    r3 = narrow_num(req, returned1, returned2, tag_number, tag_times)

    return evaluate(req, returned1, returned2, r3)

'''
Given at least a movie title, and the list of times/numbers mentioned, try to narrow down which
time to choose
input: returned1 and returned2 are tuples 0|1|2, Message for movies and theatres
tagged_number is a list of numbers
'''
def narrow_num(req, returned1, returned2, tag_number, tag_time):
    # huge todo
    if len(tag_number) == 1:
        try:
            i = int(tag_number[0])
            req.add_tickets(i)
        except ValueError:
            pass  # todo
    if len(tag_time) == 1:
        pass  # todo something to parse times into known format for known showtimes
    # returned1, returned2
    return req.done[1], ""

'''
decide what more information is required
passes on final information to the bot

Checks movie, then theatre, then number of tickets
'''
def evaluate(req, r1, r2, r3):
    if req.done[0] == 0:  # no movie
        return r1[1]
    if req.done[2] == 0:  # no theatre
        return r2[1]
    #if req.done[1] == 0:
    #   return r3[1]
    return "ok"


print("Logic module loaded")
