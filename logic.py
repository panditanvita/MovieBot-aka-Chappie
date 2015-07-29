__author__ = 'V'

from open_questions import get_movies_at_theatre, get_theatres_for_movie
from showtime import string_to_frame, time_diff


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
    r1 = -1, "Which movie would you like to see?"
    nice_movs = [ntm[t].title for t in tag_movs]
     
    if len(tag_movs) == 1:
        m_nice = nice_movs[0]
        req = req.add_field(0, m_nice)
        r1 = 1, ""

    elif len(tag_movs) > 1:
        statement = '\n'.join(['{}. {}'.format(i+1, t) for i, t in enumerate(nice_movs)])
        r1 = 2, "Possible options: " + statement
    return r1, req

'''
look in current tags and past history, find known frames
'''
def find_frames(req,s_tday, s_time):
    if req.done[4]:
        frames = req.fields[4].ask_frame()
    elif len(s_tday) == 1:
        frames = s_tday
    elif len(s_time) == 1:
        frames = s_time[0].ask_frame()
    else:
        frames = []
    return frames

'''
helper function for narrow()

update the movie theatre in the request object
update the options in state
returns tuple r2 of Int has_correct_theatre (0,1, or 2), message
'''
def narrow_theatres(req, tag_theats,ntm, ntt, s_options, s_tday, s_time):
    mk = req.fields[0].lower()
    m_nice = (req.fields[0] if req.done[0] else '')
    tag_theats_nice = [ntt[t].bms_name for t in tag_theats]
    r2 = -1, "At which theatre?"

    frames = find_frames(req, s_tday, s_time)
    # take care of theatres, either we find 0, 1 or more than 1
    if len(tag_theats) == 1:
        t = tag_theats_nice[0]
        ans, statement = get_movies_at_theatre(t_nice, ntm, ntt, frames, m_nice)
        if len(ans)>0:
            req = req.add_field(2, t_nice)
        r2 = req.done[0], statement
   
    if len(tag_theats) > 1:
        # check which all are playing if movie is mentioned
        # then return subset or full set of tag_theats
        if req.done[0]:
            ft = [t for t in tag_theats if len(ntt[t].movies.get(mk, [])) > 0]
            answers, statement = get_theatres_for_movie(m_nice, ntm, ntt, frames, ft)
            s_options = ft         
            
            r2 = 2, statement
        else:
            statement = "Possible theatre options:\n" \
                        + '\n'.join(['{}. {}'.format(i+1, t) for i, t in enumerate(tag_theats_nice)])
            s_options = tag_theats
            r2 = 2, statement

    return r2, s_options, req


'''
helper function for narrow_num
# check if the number given was in response to a list of options
if so, then choose the correct option and add it to the request
and clear the tagged list of numbers

'''
def check_if_option(state, ntt, all_nums,times):
    chosen = False
    if len(state.options)>0:
        if len(all_nums) == 1:
            chosen = True
            # index into option list
            # ASSUMING that option is a theatre, todo expand to movies
            chosen_option =ntt[state.options[int(all_nums[0])-1]].bms_name
            state.req = state.req.add_field(2, chosen_option)
        print('Choosing option:{}'.format(chosen_option))
        # remove all options
        state.options = []
        # make sure the number chosen here isn't also taken for a time
        if len(times) ==1:
            times = []
        #if len(s_time)==1: shouldn't be necessary because we clear it
        #    s_time = [] before it gets to the narrow_num function
    
    return state, times, chosen
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
def narrow_num(state, all_nums, tday, ticket_num, times, ntm, ntt):
    r3 = -1, "How many tickets?"
    r4 = -1, "What time?"
    req = state.req
    s_options = state.options
    s_tday = state.s_tday
    s_time = state.s_time
    # number of tickets
    if ticket_num != -1:
        assert(isinstance(ticket_num,int))
        req = req.add_field(1, ticket_num)
        t_form = "You've got {} ticket{}".format(str(ticket_num),("" if ticket_num==1 else "s"))
        r3 = 1, t_form

    # pick a showtime or a time of day
    # showtime overrides time of day

    # we have a singular time options
    day,time = len(tday) == 1, len(times) == 1
    # don't forget information that may have been mentioned at some other time
    day1, time1 = len(s_tday) == 1, len(s_time) == 1

    
    '''
    get_options()
    helper function
    #Boolean time
    # given a single movie and theatre, and time of day or specific time
    #(which we convert back
    # to time of day
    # if we have a movie and a theatre, see if the time is possible
    # else, if we have just a movie, see which theatres we can go to
    # else, if we have just a theatre, see which movies
    # return a list of times that the movie is playing there
    #returns []Time
    '''
    def get_options(req, time_a, times_a, tday_a):
        if time_a: frames = times_a[0].ask_frame()
        else: frames = tday_a
        # at least one of these must not be None!!
        m_nice = (req.fields[0] if req.done[0] else "")
        t_nice = (req.fields[2] if req.done[2] else "")
        #Way too may options usually- so it only prints out the first 400 chars
        # maybe it should just remember the time/ time of day and
        # wait until a specific theatre is given

        if t_nice == "":
            # options: list of theatres, showtimes
            options, statement = get_theatres_for_movie(m_nice, ntm, ntt, frames, [])
        else:
            # options: movie, showtimes
            options, statement = get_movies_at_theatre(t_nice, ntm, ntt, frames, m_nice)
        return options, statement
    '''
    helper function to sort through cases for different option lengths
    time could have been given in on the tags here, or could have
    been saved times from previous tags
    '''
    def sort_options(req, time_a, times_a, tday_a):
        options, statement = get_options(req, time_a, times_a, tday_a)
        #3 cases
        if len(options) == 0: 
            r4 = 0, statement

        elif len(options) == 1:
            showtimes = options[0][1]

            if len(showtimes) == 1: req = req.add_field(4, showtimes[0])
            r4 = min(len(showtimes), 2), statement

            #if a specific time has been chosen, then look for similar showtimes
            if time:
                for time1 in showtimes:
                    if time_diff(time1,times_a[0]) <= 30:
                        req = req.add_field(4, time1)
                        r4 = 1, ""
                    if time_diff(time1, times_a[0]) <= 10:
                        req = req.add_field(4,time1)
                        r4 = 1, ""
                        continue
        else:
            #list of movies and theatres, cut off because it can get long
            if not req.done[2]: #todo must generalise to movies
                s_options = [opt[0].lower() for opt in options]
            r4 = 2, statement[:400] + '...'
            
        return r4, req
    
    
    if day or time:
        if req.done[0] or req.done[2]:
            r4, req = sort_options(req, time, times, tday)
        else:
            # no movie, no theatre either
            # just add the time and add functionality in narrow_movies and narrow_theatres for
            # checking time
            if day: s_tday = tday[0]
            if time: s_time = times[0]
            r4 = 1, ""

    elif day1 or time1:
        if req.done[0] or req.done[2]:
            r4, req = sort_options(req, time1, s_time, s_tday)
        else: pass
    # we have multiple time options>>
    if len(times) > 1:
        r4 = 2, "Multiple times selected."
    state.req = req
    state.options = s_options
    state.s_tday = s_tday
    state.s_time = s_time
    return r3, r4, state

'''
logic is weird.

given that we have a sequence of checking different attributes
(answer was an option - movie - theatre - time), we have to do
a lot of repetitive reasoning within each one because we do not consider
all the information as a whole - if the person says 'i want to see bajrangi this
evening at innovative', it will
-insert bajrangi into the req object, then
-look for all the theatres that show it this evening and create a message for
that, and then
-attempt to search for showtimes this evening at innovative for bajrangi

(we know a theatre and a movie, what
are the times? we know two times and a movie, what are the theatres?) or
we re-check everything at the end, taking into account the saved state
information that we didn't enter into the movie list

basically sweeping up loose edge cases
'''
def final_reasoning(state, chosen, ntm, ntt):
    req, s_tday, timeout = state.req, state.s_tday, state.timeout
    statement = ''
    help_s = 'You can tell me a movie title, a theatre name and/or a time of day for a list of options. '

    # case: if we haven't learned anything yet, give options
    if req.last == -1:
        statement = 'I can help you book a ticket. ' + help_s
    # todo if self.done[0] and self.done[2]

    # after a certain number of attempts at the same question, we change to a human
    if timeout >= 3:
        statement = 'Cant quite understand you. ' + help_s

    # if we're not done, choose another statement
    if sum(req.done)<5:
        next_q = req.done.index(False)
        if next_q ==1 and req.done[4] == 0:
            next_q =4
        #todo change self.done to match order wanted
        #right now it's placing ticket num before showtime
    else: next_q = -1
    
    #if we've finished getting a movie and a theatre 
    if chosen:
        #look for and specify frames
        frames = find_frames(req, s_tday, state.s_time)
        o, statement = get_movies_at_theatre(req.fields[2], ntm, ntt,frames,req.fields[0])
        next_q = 4


    return next_q, statement


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
def narrow(state, tags, ntm, ntt):
    tag_movs, tag_theats, all_nums, tday, t_num, times = tags
    # take care of movies, either we find 0, 1 or more than 1
    #print (tag_movs, tag_theats)
    r1, state.req = narrow_movies(state.req, tag_movs, ntm)
    
    #check old options first
    state, times, chosen = check_if_option(state, ntt, all_nums, times)

    r2, state.options, state.req = narrow_theatres(state.req,tag_theats,ntm, ntt, state.options, state.s_tday, state.s_time)
    r3, r4, state = narrow_num(state, all_nums, tday, t_num, times, ntm, ntt)

    f = final_reasoning(state, chosen, ntm, ntt)
    return evaluate(state.req, r1, r2, r3, r4,f)



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
def evaluate(req, r1, r2, r3, r4, f):
    f_has_message = len(f[1])>0
    theatre_has_message = r2[0]>=0 and len(r2[1])>0
    '''theatre_has_message_2 = req.done[2] >= 1 and len(r2[1])>0
    not working because when an option is chosen, req.done[2]=1
    but an item might not have been chosen this time around'''
    movie_has_message = r1[0]==2 and len(r1[1])>0
    time_has_message = r4[0] >= 0 and len(r4[1])>0
    no_movie = req.done[0] == 0
    no_theatre = req.done[2] == 0
    no_time = req.done[4] == 0
    no_ticket_num = req.done[1] == 0
    
    returns = [f_has_message, time_has_message, theatre_has_message,
               movie_has_message, no_movie,no_theatre,no_time,
               no_ticket_num,True]
    to_return = [f, (4, r4[1]),(4, r2[1]),
                 (0, r1[1]), (0, r1[1]),(2, r2[1]),(4, r4[1]),
                 (1, r3[1]),(-1,req.readout())]
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
