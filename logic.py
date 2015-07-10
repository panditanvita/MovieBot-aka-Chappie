__author__ = 'V'

'''
logic submodule


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
def narrow_down_movies(found_movies):
    #todo
    n = len(found_movies)
    if n == 0:
        return 0, "Found no movies"
    if n == 1:
        return True, found_movies[0]
    return 2, "Too many movies"