# MovieBot
natural language requests for Magic Tiger

<in progress>
MovieBot helps you look for movie tickets

***
###to play with:
run Bot file on python interpreter

'''
bot = Bot()
bot.run()
'''

interact with bot on the console
ask for a movie that's in theatres. ask for 4 tickets. suggest a time of day.
or suggest an exact time. or ask for a theatre and suggest a time of day.

will finish by either fulfilling a request, or if you input "bye"
***

***
####design: idea of an 'expert system' with a knowledge base and logical rule-set. keeps track of state and can respond to certain movie-related inputs
***

***

###knowledge : takes care of scraping and parsing information from the internet/stored files

####knowledge.py:
Knowledge base for movie bot

Created by web scraping google movie results.
Only *need* to run it once a day, to update. This file doesn't call anything, all methods are called in other
places

Note: American spelling is 'theater', so google html code uses that.
Indian/British spelling is 'theatre' and my code uses this!

Speed: takes about five seconds to finish
***

***
###tokeniser: tokenises and tags information from the customer

####tokeniser.py
tokenizing, categorizing and tagging words done in here

tokeniser splits up incoming string into valid words, attempts to correct for slang,
and tries to keep times and phone numbers as one token

tagging done in tag_tokens_num (which looks for ticket numbers and times)
and tag_tokens_movies (which looks for movie titles and theatres).

idea is to allow for some typos using the typo() function for all string comparisons

currently theatre name is the hardest to select for, because the full theatre name is
never used - people will mention several keywords out of order like 'pvr koramangala' or
'sri srinivasa', and those keywords may even match to multiple theatres. current
implementation attempts to look for a subset of matching keywords , and narrows
down the total space as far as possible
***

***
###logic: takes tokenised information and attempts to fill in the request object

####logic.py
Logic is thought of in terms of cases: given a limited set of total
attributes to fulfill, we want to fit in as many as possible while also
making sure it is all mutually compatible. case 1: we have one movie, case 1.1: we have a movie
and a theatre, is this movie playing at this theatre? case 2: we have two movies and so on..
order of attempting-to-fit is movies - theatres - time. So it might input a movie
and a theatre and then fail at selecting the chosen time.

narrow() takes in tokeniser output - the tagged movie/theatre/time/day entities
it subcontracts the work. there is a submodule for each attribute, each function
makes sure that what it inputs into the movie request is
correct given all the other information it knows.
each submodule updates the request object based on what it knows. each one creates a
potential return message for the customer.

output of narrow() is given to eval()
finally, decisions: do we have enough information?
which questions must we ask to get more information?
maybe the selected movie is not playing in the selected theatre?
give alternate showtimes
eval() chooses which output to return.

IMPORTANT: note that eval() re-evaluates based on every time narrow() is called on a set
of tags! so information from the past eval() is re-written, and everything which is not
saved to the request object is lost.

potential improvement - save all past information returned by the narrow() sub-functions
-long if/else cases are awkward but it seems to work
***




