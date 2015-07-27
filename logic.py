__author__ = 'V'

from open_questions import get_movies_at_theatre, get_theatres_for_movie
from showtime import string_to_frame, frame_to_time, time_diff


'''
helper function for narrow()

update the movie title in the request object,
returns tuple r1 of Int has_correct_movies, message
has_correct_movies code:
0 for no movies
1 for selected 1
2 for more than one
'''
def narrow_movies(req,tag_movs,ntm):
    r1 = 0, "Which movie would you like to see?"
    if req.done[0] != 1: # doesn't re-write if a movie is already selected
        if len(tag_movs) == 1:
            m_nice = ntm[tag_movs[0]].title
            req.add_title(m_nice)
            r1 = 1, ""

         # use for indexing! never gets here because eval doesn't check for it
        if len(tag_movs) > 1:
            statement = '\n'.join(['{}. {}'.format(i, t) for i, t in enumerate(tag_movs)])
            r1 = 2, "Possible options: " + statement
    return r1

'''
helper function for narrow()

update the movie theatre in the request object
update the options in state
returns tuple r2 of Int has_correct_theatre (0,1, or 2), message
'''
def narrow_theatres(req,tag_theats,ntt, options):
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
                statement = "{} isn't playing at any of those locations today".format(req.title)
            else:
                ft_nice = [ntt[t].bms_name for t in ft]
                [options.append(t) for t in ft]
                statement = "{} is playing in: ".format(req.title) \
                            + '\n'.join(['{}. {}'.format(i, t) for i, t in enumerate(ft_nice)])
                            #'\n'.join(ft_nice)
                #
                # support user choosing numbers!

                # ['{}. {}'.format(i, t) for i, t in enumerate(tag_theats)]
            r2 = 2, statement
        else:
            tag_theats_nice = [ntt[t].bms_name for t in tag_theats]
            statement = "Possible theatre options: " + '\n'.join(tag_theats_nice)
            r2 = 2, statement

    return r2

'''
helper function for narrow()

Given at least a movie title, and the list of times/numbers mentioned, try to narrow down
how many tickets and which time to choose

Also checks if the list of options is present, which means that the bot has
just presented a number of options to the user. if there are any numbers present,
then this number must be the option

input: r1 and r2 are tuples 0|1|2, Message for movies and theatres
Integer ticket_num, String[] tday, String[] times
returns r3, r4, similar tuples with code, message for number of tickets and times
'''
def narrow_num(req, all_nums, tday, ticket_num, times, ntm, ntt, b_options):
    r3 = 0, "How many tickets?"
    r4 = 0, "What time?"

    # check if the number given was in response to a list of options
    if len(b_options)>0:
        if len(all_nums) == 1:
            #index into option list
            chosen_option =ntt[b_options[int(all_nums[0])-1]].bms_name
            req.add_theatre(chosen_option)

        # remove all options
        [b_options.pop() for i in range(len(b_options))]
        # make sure the number chosen here isn't also taken for a time
        if len(times) ==1:
            times.pop()

    # number of tickets
    if ticket_num != -1:
        assert(isinstance(ticket_num,int))
        req.add_tickets(ticket_num)
        t_form = "You've got {} ticket{}".format(str(ticket_num),("" if ticket_num==1 else "s"))
        r3 = 1, t_form

    # pick a showtime or a time of day
    # showtime overrides time of day

    #we have a singular time options
    day,time = len(tday) == 1, len(times) == 1

    '''
    get_options()
    helper function
    #Boolean time
    #lowercase movie title key mk
    #lowercase theatre name key t_nice (if we have it)
    # given a single movie and theatre, and time of day or specific time (which we convert back
    # to time of day
    # if we have a movie and a theatre, see if the time is possible
    # else, if we have just a movie, see which theatres we can go to
    # else, if we have just a theatre, see which movies
    # return a list of times that the movie is playing there
    #returns []Time
    '''
    def get_options(time):
        if time: frames = times[0].ask_frame()
        else: frames = [string_to_frame(tday[0])]

        # at least one of these must not be None!!
        m_nice = (req.title if req.done[0] else None)
        t_nice = (req.theatre if req.done[2] else None)
        #Way too may options usually- so it only prints out the first 400 chars
        # maybe it should just remember the time/ time of day and
        # wait until a specific theatre is given

        if t_nice == None:
            # options: list of theatres, showtimes
            options, statement = get_theatres_for_movie(m_nice, ntt, frames)
        elif m_nice == None:
            # options: list of movies, showtimes
            options, statement = get_movies_at_theatre(t_nice, ntt,frames)
        else:
            # options: movie, showtimes
            options, statement = get_movies_at_theatre(t_nice, ntt, frames, m_nice)
        return options, statement

    # with tday
    if day or time:
        if req.done[0] or req.done[2]:
            options, statement = get_options(time)
            # we have options for the customer
            # cases for changing the returned statement
            if len(options) == 0: #no showtimes for the given combination
                r4 = 0, statement
            elif len(options) == 1:
                showtimes = options[0][1]
                if len(showtimes) == 1: req.add_time(showtimes[0])
                r4 = min(len(showtimes), 2), statement

                #if a specific time has been chosen, then look for similar showtimes
                if time:
                    for time1 in showtimes:
                        if time_diff(time1,times[0]) <= 30:
                            req.add_time(time1)
                            r4 = 1, ""
            else:
                #list of movies and theatres, cut off because it can get long
                if not req.done[2]: #todo generalise to movies
                    [b_options.append(opt[0].lower()) for opt in options]
                r4 = 2, statement[:400] + '...'
        else:
            # no movie, no theatre either
            # just add the time and add functionality in narrow_movies and narrow_theatres for
            # checking time todo
            if day: req.add_time(frame_to_time(string_to_frame(tday[0])))
            if time: req.add_time(times[0])
            r4 = 1, ""
    # we have multiple time options>>
    if len(times) > 1:
        r4 = 2, "Multiple times selected."

    return r3, r4

'''
narrow()

input: MovieRequest object and several lists of tags. Movie and Theatre names in tags must be
keys into their respective maps. KEYS ARE LOWERCASE
Int ticket_num, Time[] times, tday
dictionaries ntm, ntt
takes and fills in a MovieRequest object based on the most likely.
outputs.
if there is only one movie and/or theatre, input into request, return 1
if there is more than one, send in a question to narrow it down
need to make sure the ticket is valid!

assuming time is for today

returns updated_request, r1, r2, r3, r4
a tuple of results each for movies, theatres, number of tickets and showtimes
'''
def narrow(req, tags, ntm, ntt, options):
    tag_movs, tag_theats, all_nums, tday, t_num, times = tags
    # take care of movies, either we find 0, 1 or more than 1
    #print (tag_movs, tag_theats)
    r1 = narrow_movies(req, tag_movs, ntm)
    #check old options first before re-writing
    r3, r4 = narrow_num(req, all_nums, tday, t_num, times, ntm, ntt, options)

    r2 = narrow_theatres(req,tag_theats,ntt, options)


    #print(tag_theats)
    #print('r2',r2)
    #print('r4',r4)
    return evaluate(req, r1, r2, r3, r4)


'''
helper function for narrow()

uses all the returned outputs of the previous helper functions
decide what more information is required
passes on final information to the bot
returns a tuple of the new question number,
and a statement to be sent back to the customer

note that req.done checks if we have completed the field
so it may be 0 if we have not heard a response, or if we
have too many possible answers as well
for theatres and times: first checks whether we have narrowed
down to a [theatre], if we haven't then it asks for one. else
it checks whether we have a theatre, but our narrow() function
has returned multiple options given what we know

Checks if there are any important messages in movie, messages from time, then
 movie, then theatre, then time, then number of tickets
 if these are all good, then it returns the request readout
'''
def evaluate(req, r1, r2, r3, r4):
    theatre_has_message = (req.done[2] ==1 and r2[0] == 1 and len(r2[1])>0)
    time_has_message = ((r4[0] == 1 or r4[0] == 2) and len(r4[1])>0)
    no_movie = req.done[0] == 0
    no_theatre = req.done[2] == 0
    no_time = req.done[4] == 0
    no_ticket_num = req.done[1] == 0

    returns = [theatre_has_message,time_has_message,
               no_movie,no_theatre,no_time,no_ticket_num,True]
    to_return = [(4, r2[1]),(4, r4[1]),
                 (0, r1[1]),(2, r2[1]),(4, r4[1]),(1, r3[1]),(-1,req.readout())]
    i = returns.index(True)
    return to_return[i]

print("Logic module loaded")

'''
debugging:

from knowledge import get_theatres
ntm, ntt, tl = get_theatres()
from showtime import *
from open_questions import *
from classes import *

t_nice = ntt.keys()[4]
mk = ntt[t_nice].movies.keys()[0]
req = MovieRequest("test")
req.add_title(mk)
req.add_theatre(t_nice)


#for narrow_num
times = [Time('5pm')]
tday = ['evening']
ticket_num = 3
r1 = [True]
r2 = [True]
narrow_num(req,tday,ticket_num,times,ntt)
r1=[False]
narrow_num(req,tday,ticket_num,times,ntt)

'''''
