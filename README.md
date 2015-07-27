# MovieBot
natural language movie requests for Magic Tiger

--in progress--

***
###to play:

run Bot file on python interpreter

`
bot = Bot()

bot.run()
`

Interact with bot on the console
Ask for a movie that's in theatres. Ask for 4 tickets. Suggest a time of day.
Or suggest an exact time. Or ask for a theatre and suggest a time of day. Or
ask for everything at once.

Finish by either fulfilling a request, or if you input "bye"
***

***
###Purpose:

MovieBot gives a valid response to every line of movie-related input

Each bot corresponds to a single conversation, as the final product of a successful conversation should be a single
completed movie request

Bot has access to static dictionaries of movie names and theatres, which come from the knowledge base
each bot instance keeps track of all its conversations.

Two options for running:

1. With a debug flag (in which case, call bot.run() to play with the features,
and the bot will interact using System.in and System.out

2. Without the debug flag, in which case the bot will keep track of its state in the MovieRequest and conversation
objects created at instantiation, and you must call the sleek_get_response(message) function to get the bots
response to a particular input

***

***
###Design:

idea of an 'expert system' with a knowledge base and logical rule-set.

keeps track of state in a State object and can respond to certain movie-related inputs

State object has a question and option.
Question corresponds to the attribute the bot is expecting to here about, and is used in the
tagging functions, to favor entities which are indicated by the question. For example -
if question is 1, then the tagging functions try harder to find a valid movie title.
If the bot response involves multiple options, we want to make it easier for the customer
to choose a specific one. Option field keeps track of given options, if the bot gave
a list of valid theatres or movies, for example.

The final product of the bot is the request object printout which summarises all the compatible information
learned so far.

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
Tokenizing, categorizing and tagging words done in here

Tokeniser splits up incoming string into valid words, attempts to correct for slang,
and tries to keep times and phone numbers as one token

Tagging is done in tag_tokens_num (which looks for ticket numbers and times)
and tag_tokens_movies (which looks for movie titles and theatres).

The idea is to allow for some typos using the typo() function for all string comparisons

Currently the theatre name is the hardest to select for, because the full theatre name is
never used - people will mention several keywords out of order like 'pvr koramangala' or
'sri srinivasa', and those keywords may even match to multiple theatres.

The current implementation attempts to look for a subset of matching keywords , and narrows
down the total space as far as possible. It returns all best matching options.
***

***
###Logic: takes tokenised information and attempts to fill in the request object

####logic.py
Logic is thought of in terms of cases: given a limited set of total
attributes to fulfill, we want to fit in as many as possible while also
making sure it is all mutually compatible.

There are many cases and sub-cases. For example:
Case 1: we have one movie in the list of tags
Case 2: we have a movie and a theatre, is this movie playing at this theatre?
case 3: we have multiple movies and one theatre. Which movies are playing at the theatre?
Case 4: We have one movie and one time of day. Which theatres can we return?
And so on.
The order of attempting-to-fit multiple options is movies - theatres - time. So it might input a movie
and a theatre and then fail at selecting the chosen time.

narrow() takes in tokeniser output - the tagged movie/theatre/time/day entities.
It subcontracts the work to specific subfunctions for each kind of entity.
Each function makes sure that what it inputs into the movie request is
correct given all the other information it knows. Each function returned creates a
potential return message for the customer.

The output of narrow() is given to eval()
Finally, bot must make decisions: Do we have enough information?
Which questions must we ask to get more information?
Maybe the selected movie is not playing in the selected theatre? What
alternative options are there?
eval() chooses which output to return.

Note that eval() re-evaluates based on every time narrow() is called on a set
of tags! so information from the past eval() is re-written, and everything which is not
saved to the request object is lost.
***

***
####Thoughts and further improvements:

######evaluation of design:
The current implementation of keyword-matching works reasonably well.

I read about, flirted with then abandoned the idea of using more elaborate
NLP techniques and making use of existing tools, like the python nltk library,
to understand the input on a deeper level. For example, we could further parse input
into the parts of a sentence (nouns, adjectives, verbs..). It
seemed like overkill for the scale of the project, although it could potentially
improve the bot in certain cases (if the movie name sounds like numbers or parts of a regular
input sentence, then it might make sense to make parts-trees of a sentence)

I also abandoned the idea of using more structured and unstructured learning algorithms,
both because it would involve changing too many other variables, and because
the scale of the project did not allow for it. For example, you could keep track of the
most common movies chosen, the most popular movie theatres and use those to tailor
search results.

Super basic user data - just location - would really improve finding the theatre

The current design is to have a single response to every line of input from the customer
There are other possible options, which might be better, depending on the use case.
1. the bot only responds to new information
2. the bot combines texts which come in within a few seconds of each other into one input set
3. save conversation and request as part of the state, and then you only need to query a single bot
instance at any time, for any number of concurrent users, because each call to the bot will include all
past state information and current user input. But this state object will still have to be stored somewhere,
and tied into the onging user resource.

######Generalising
How to generalise to a bot for booking travel tickets, or for buying groceries:



General principles - creating the knowledge base, tokenising user input, forming logical rules -
as described in the readme are broadly applicable.  The Knowledge base itself would of course completely change.
Tokenising would have to be adapted to incorporate new slang and tag different entity groups, like Cities.
Logic currently selects:
1 or many (available) movies, 1 or many (available) theatres, a given or range of showtimes, all mutually compatible
For bus tickets: To and From are set, a given or range of departure times
For groceries: 1 or more items, with quantities.
For logically similar cases like booking bus tickets, one would be able to reuse some of the logic functions.

######improvements:

- (most important) API is biggest bottleneck to a better bot - with it, we can use the request printout generated as a confirmation
ticket for the customer, and go ahead booking the ticket for them with the bot as well. We would also need further
questions, such as suggesting seat type (far from the screen, close) based on what's available.
google scraping doesn't return a lot of the valid showtimes - need
the book my show api. also important because then we could keep a single static knowledge
base, which would allow us to keep adding information about each theatre. scraping is like
hunter-gathering, works on the fly, but farming is better.


- save all past information returned by the narrow() sub-functions in some sort of State
object, which should keep track of both the question and the narrowed down options

(little improvements)
- long if/else cases in logic are awkward (but it seems to work). what alternatives?
- options for choosing numbered answers still needs to be done
- timeout for repeating the same question
- options for choosing a different day (will need to scrape theatres for the
next day as well, and tie that into our knowledge base)
***

####Credits
All code written by me, Anvita Pandit.


