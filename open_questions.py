__author__ = 'V'

'''
now that the bot can ask questions and fill in a movie request, we want to move on the
next step: examining the information and offering alternative options

given a theatre, return a data structure and formatted string statement explaining all the movies, showtimes
for that theatre today. optional argument of a specific movie name and time of day to narrow it down

given a movie, and optional time, return data structure and statement of all the theatres and showtimes

two parts:
-recognising that there is a question/understanding the question
-answering the question, which is a lot easier

'''

from showtime import frame_to_string

# helper function
def get_time_statement(time):
    if len(time)>0: time_statement = "today {}".format(' or '.join([frame_to_string(t) for t in time]))
    else: time_statement = "today."
    return time_statement
'''
get_movies_at_theatre(theatre,ntt,time=-1)

What movies are playing at [String theatre]. optional time of day modifier, else returns all times
Time of day modifier is a list of frames, which are integers in [0,3]. empty list means all times

optional [String movie_name] modifier to choose a particular movie at [theatre], else returns all movies
input t_nice and m_nice are Cased
theatre and movie_name must be a working key!
input: String theatre_name key, ntt dictionary, list of times of day(ifnot specified, return all)
returns two items: [list of tuples of
((String movie_name, Time[] showtimes) for each movie], formatted string output of same
'''
def get_movies_at_theatre(t_nice, ntm, ntt, time, m_nice = ""):
    answers, statement = [], ""
    theatre = t_nice.lower()
    movie_name = m_nice.lower()
    movies = ntt[theatre].movies # returns dictionary of String movie_name: list of Time showtimes
    if len(movie_name) > 0:
        if movies.has_key(movie_name):
            movies = {movie_name: movies[movie_name]}
            mov_statement = m_nice
        else: return [], "{} is not playing at {}".format(m_nice, t_nice)
    else: mov_statement = "any movies"

    def present(t):
        l = [t.get_frame(t1) for t1 in time]
        return sum(l)>0
    # iterate through (subsection of) movies in the theatre
    for movie in movies.keys():
        if len(time)>0:
            ans = [t for t in movies[movie] if present(t)]
        else: ans = movies[movie]
        if len(ans)>0:
            answers.append((movie,ans))
            m_title = ntm[movie].title
            statement += "{} is playing at {}\n".format(m_title," ".join([t.printout() for t in ans]))

    time_statement = get_time_statement(time)

    if len(answers) == 0: statement = "{} is not playing {} {}".format(t_nice, mov_statement, time_statement)

    return answers, statement


'''
and its partner question:
where is [movie] playing? (with time of day modifier)

get_theatres_for_movie(movie_name, ntt, optional time)

String movie_name must be a proper key, but even then it might not exist in the theatre.movies dictionary
input: String movie_name, ntt dictionary, optional time frame list
List of theatres is a list of theatre name keys that movie search should be
limited to

returns two items: data structure, a [list of tuples (String theatre.bms_name, Time[] showtimes) for all theatres],
formatted statement for user explaining where the movie is playing

'''
def get_theatres_for_movie(m_nice, ntm, ntt, time, theatres):
    answers, statement = [], ""
    if len(theatres)>0:
        vals = [ntt[t] for t in theatres]
    else: vals = ntt.values()
    for theatre in vals:
        # should return either mktuple of movie_name, Time[] showtimes or an empty list
        playing = get_movies_at_theatre(theatre.bms_name, ntm, ntt, time, m_nice)[0]
        i = len(answers) +1
        for p in playing:
            answers.append((theatre.bms_name,p[1]))
            statement += "{}. {}- Showtimes are {}\n".format(i,theatre.bms_name," ".join([t.printout() for t in p[1]]))

    time_statement = get_time_statement(time)

    if len(statement) == 0:
        if len(theatres) == 0:
            statement = "Sorry, {} isn't playing {}".format(m_nice, time_statement)
        else:
            statement = "Sorry, {} isn't playing at those locations {}".format(m_nice, time_statement)
    else: statement = "{} is playing at: \n{}".format(m_nice, statement)

    return answers, statement


'''
to debug:
from knowledge import get_theatres
ntm,ntt,tl = get_theatres()
t = ntt.keys()[2] # try other index. 'innovative multiplex: marathalli' is popular
m = ntm.keys()[3] # try other index

print(get_movies_at_theatre(t, ntt, time = 0, movie_name = m)[1])  #change time, choose other movie name
print(get_theatres_for_movie(m,ntt)[1])



'''
