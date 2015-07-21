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
update the movie title in the request object,
returns tuple r1 of boolean has_correct_movies, message
'''
def narrow_movies(req,tag_movs,ntm):
    r1 = 1, "Which movie?"
    if req.done[0] != 1:
        if len(tag_movs) == 1:
            m_nice = ntm[tag_movs[0]].title
            req.add_title(m_nice)
            r1 = 1, ""

         # use for indexing!
        if len(tag_movs) > 1:
            statement = '\n'.join(['{}. {}'.format(i, t) for i, t in enumerate(tag_movs)])
            r1 = 2, "Possible options: " + statement
    return r1

'''
update the movie theatre in the request object
returns tuple r2 of boolean has_correct_theatre, message
'''
def narrow_theatres(req,tag_theats,ntt):
    mk = req.title.lower()
    r2 = 0, "At which theatre?"
    # take care of theatres, either we find 0, 1 or more than 1
    if len(tag_theats) == 1:
        t = tag_theats[0] # use for indexing!
        t_nice = ntt[t].bms_name

        if req.done[0]:
            # check if movie is in theatre today
            d = ntt[t].movies
            if len(d.get(mk, [])) == 0:
                r2 = 0, "Sorry, but {} isn't showing at {} today.".format(req.title, t_nice)
            else:
                r2 = 1, "Possible showings today: "+ ' '.join([t.printout() for t in d.get(mk)])
                req.add_theatre(t_nice)
        else:
            req.add_theatre(t_nice)
            r2 = 1, ""

    if len(tag_theats) > 1:
        # check which all are playing if movie is mentioned
        # then return subset or full set of tag_theats
        if req.done[0]:
            ft = [t for t in tag_theats if len(ntt[t].movies.get(mk, [])) > 0]
            if len(ft) == 0:
                ft = tag_theats
                statement = "{} isn't playing there today".format(req.title)
            else:
                statement = "{} is playing in: ".format(req.title) \
                            + '\n'.join(['{}. {}'.format(i, t) for i, t in enumerate(ft)])
            r2 = 2, statement
        else:
            statement = "Possible theatre options: " \
                        + '\n'.join(['{}. {}'.format(i, t) for i, t in enumerate(tag_theats)])
            r2 = 2, statement

    return r2

'''
narrow()
input: MovieRequest object and several lists of tags. Movie and Theatre names must be
keys into their respective maps. KEYS ARE LOWERCASE
takes and fills in a MovieRequest object based on the most likely.
outputs.
if there is only one movie and/or theatre, input into request, return 1
if there is more than one, send in a question to narrow it down
need to make sure the ticket is valid!

assuming time is for today

returns updated_request, returned1,returned2, r3
a tuple of results for movies, theatres and numbers
'''
def narrow(req, tag_movs, tag_theats, tday, ticket_num, times, ntm, ntt):
    # take care of movies, either we find 0, 1 or more than 1
    #print (tag_movs, tag_theats)
    r1 = narrow_movies(req, tag_movs, ntm)
    r2 = narrow_theatres(req,tag_theats,ntt)
    r3, r4 = narrow_num(req, r1, r2, tday, ticket_num, times)

    return evaluate(req, r1, r2, r3, r4)

'''
Given at least a movie title, and the list of times/numbers mentioned, try to narrow down
how many tickets and which time to choose

input: returned1 and returned2 are tuples 0|1|2, Message for movies and theatres
Integer ticket_num, String[] tday, String[] times
'''
def narrow_num(req, r1, r2, tday, ticket_num, times):
    # number of tickets
    if ticket_num != -1:
        assert(isinstance(ticket_num,int))
        req.add_tickets(ticket_num)

    # pick a showtime

    #check if time exists for given theatre todo before adding
    # with tday
    if len(times) == 1: req.add_time(times[0])

    # returned1, returned2
    r3 = req.done[1], "How many tickets?"
    r4 = req.done[4], "What time?"
    return r3, r4

'''
decide what more information is required
passes on final information to the bot

Checks movie, then theatre, then number of tickets
'''
def evaluate(req, r1, r2, r3, r4):
    if req.done[0] == 0:  # no movie
        return 0, r1[1]
    elif req.done[2] == 0:  # no theatre
        return 2, r2[1]
    elif req.done[1] == 0:  # no ticket number
        return 1, r3[1]
    elif req.done[4] == 0: # no time
        return 4, r4[1]
    else:
        # we are done!
        return -1, req.readout()


print("Logic module loaded")
