__author__ = 'V'

'''

The sleekxmpp bot is the interface between the bot and the server. it takes in and sends user messages
to a bot instance
Each bot instance is tied to a single conversation with one user.

Model: MovieRequest object: attempt to insert information into req object.
MovieRequest ensures only valid (according to the two movie and theatre dictionaries it contains) information is saved.
MovieRequest does not print anything - propagates all information back to the bot as a tuple (1 or 0, Err or "")

View: MovieBot object: class has access to single classifier, run at the beginning. each instance keeps track of all
its conversations, error logs and movie requests made. Run() function takes in incoming lines from user, uses tokenizer,
spellcheck and parser, just enough to preprocess and then send it to the relevant submodules. Customer should always
be able to keep typing, and MovieBot will keep re-updating the submodules. Chat may be over multiple lines.


Controller: Submodule logic. Extracts information from token lists given by MovieBot, and propagate the answers back.
submodule will keep track of what information needs to be learned to complete the MovieRequest, and tells the bot to ask
those questions.


idea of an 'expert system' with a knowledge base and logical rule-set.

knowledge takes care of scraping and parsing information from the internet/stored files

tokeniser parses information from the customer, looking for cues like numbers, names of movies
and theaters, and times

logic takes tokenised information and attempts to fill in the request object, making
sure that the information is mutually compatible
'''


'''
ORDER:
run Bot file with interpreter
bot = Bot()
bot.run()
interact with bot on the console
will finish by either fulfilling a request, or if you input "bye"

handy:
reload(module)

'''