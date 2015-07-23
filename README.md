# MovieBot
natural language movie requests for Magic Tiger

<</in progress/>>

***
###to play:
run Bot file on python interpreter

'''
bot = Bot()
bot.run()
'''

interact with bot on the console
ask for a movie that's in theatres. ask for 4 tickets. suggest a time of day.
or suggest an exact time. or ask for a theatre and suggest a time of day.

Finish by either fulfilling a request, or if you input "bye"
***

***
###Purpose:
MovieBot gives a valid response to every line of movie-related input
Each bot corresponds to a single conversation, as the final product of a successful conversation should be a single
completed movie request
Bot has access to unchangeable dictionaries of movie names and theatres, which come from the knowledge base
each bot instance keeps track of all its conversations.

Two options for running:
1. with a debug flag (in which case, call bot.run() to play with the features,
and the bot will interact using System.in and System.out
2. without the debug flag, in which case the bot will keep track of its state in the MovieRequest and conversation
objects created at instantiation, and you must call the sleek_get_response(message) function to get the bot's
response to a particular input

***

***
###Design:

idea of an 'expert system' with a knowledge base and logical rule-set. keeps track of state and can respond to certain movie-related inputs

###Knowledge : scraping and parsing information from the internet/stored files

####knowledge.py:
Knowledge base for movie bot

Created by web scraping google movie results. Correlates with static list of
theatre information from book my show theatre listings. Ties in google showings
to known theaters in stored file.
Only *need* to run it once a day, to update.

Note: American spelling is 'theater', so google html code uses that.
Indian/British spelling is 'theatre' and my code uses this!

Speed: takes about five seconds to finish
***

***
###Tokeniser: tokenises and tags information from the customer

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
###Logic: takes tokenised information and attempts to fill in the request object

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

Note that eval() re-evaluates based on every time narrow() is called on a set
of tags! so information from the past eval() is re-written, and everything which is not
saved to the request object is lost.
***

***
####Further improvements:

- google scraping doesn't return a lot of valid showtimes - need the book my show api

- save all past information returned by the narrow() sub-functions
- long if/else cases in logic are awkward (but it seems to work)
- options for choosing numbered answers still needs to be done
- timeout for repeating the same question
- options for choosing a different day (will need to scrape theatres for the
next day as well, and tie that into our knowledge base)
- current design is to have a single response to every line of input from the customer
 other possible options, which might be better
-- the bot only responds to new information
-- bot combines texts which come in within a few seconds of each other into one input set

***




