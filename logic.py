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
def narrow_down(found_movies):
    #todo
    n = len(found_movies)
    if n == 0:
        return 0, "Found no movies"
    if n == 1:
        return True, found_movies[0]
    return 2, "Too many movies"


'''
takes and fills in a MovieRequest object based on the most likely
outputs.
if there is only one movie and/or theatre, input into request
if there is more than one, send in a question to narrow it down
need to make sure the ticket is valid!

assuming time is for today
'''
def narrow(req, tag_movs, tag_theats):

    if narrow_down(tag_movs) == 1:
        req.add_title(tag_movs[0])

    if narrow_down(tag_theats) == 1:
        # first check if it's playing
        if req.done[0]:
            # check if movie is in theatre today
            pass
        req.add_theatre(tag_theats[0])

    if narrow_down(tag_theats) > 1:
        # check which all are playing if movie is mentioned
        # then return subset or full set of tag_theats
        pass
    return
