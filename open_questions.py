__author__ = 'V'

'''
now that the bot can ask questions and fill in a movie request, we want to move on the
next step: answering general questions

given a theatre, return a data structure and formatted string statement explaining all the movies, showtimes
for that theatre today. optional argument of a specific movie name and time of day to narrow it down

given a movie, and optional time, return data structure and statement of all the theatres and showtimes

two parts:
-recognising that there is a question/understanding the question
-answering the question, which is a lot easier

other features:
-options for choosing numbered answers still needs to be done
-timeout for repeating the same question
aaannnnd options for choosing a different day (will need to scrape theatres for the
next day as well, and tie that into our knowledge base)
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
optional [String movie_name] modifier to choose a particular movie at [theatre], else returns all movies
theatre_name and movie_name must be a working key!
input: String theatre_name key, ntt dictionary, list of times of day(ifnot specified, return all)
returns two items: [list of tuples of
((String movie_name, Time[] showtimes) for each movie], formatted string output of same
'''
def get_movies_at_theatre(theatre, ntt, time=[], movie_name = ""):
    answers, statement = [], ""
    movies = ntt[theatre].movies # returns dictionary of String movie_name: list of Time showtimes
    if len(movie_name) > 0:
        if movies.has_key(movie_name):
            movies = {movie_name: movies[movie_name]}
            mov_statement = movie_name
        else: return [], "{} is not playing at {}".format(movie_name, theatre)
    else: mov_statement = "movies"

    # iterate through (subsection of) movies in the theatre
    for movie in movies.keys():
        if len(time)>0: ans = [t for t in movies[movie] if sum([t.get_frame(t1) for t1 in time])>0]
        else: ans = movies[movie]
        if len(ans)>0:
            answers.append((movie,ans))
            statement += "{} is playing at {}\n".format(movie," ".join([t.printout() for t in ans]))

    time_statement = get_time_statement(time)

    if len(answers) == 0: statement = "{} is not playing {} {}".format(theatre, mov_statement, time_statement)

    return answers, statement


'''
and its partner question:
where is [movie] playing? (with time of day modifier)

get_theatres_for_movie(movie_name, ntt, optional time)

String movie_name must be a proper key, but even then it might not exist in the theatre.movies dictionary
input: String movie_name, ntt dictionary, optional time frame list

returns two items: data structure, a [list of tuples (String theatre.bms_name, Time[] showtimes) for all theatres],
formatted statement for user explaining where the movie is playing

'''
def get_theatres_for_movie(movie_name, ntt, time=[]):
    answers, statement = [], ""
    for theatre in ntt.values():
        # should return either mktuple of movie_name, Time[] showtimes or an empty list
        playing = get_movies_at_theatre(theatre.bms_name.lower(), ntt, time=time, movie_name=movie_name)[0]
        #print(playing)
        for p in playing:
            answers.append((theatre.bms_name,p[1]))
            statement += "{}- Showtimes are {}\n".format(theatre.bms_name," ".join([t.printout() for t in p[1]]))

    time_statement = get_time_statement(time)

    if len(statement) == 0: statement = "Sorry, that movie isn't playing {}".format(time_statement)
    else: statement = "{} is playing at: \n{}".format(movie_name, statement)

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