__author__ = 'V'

'''
once a day: run classifier (when updating for online, download latest chat info with labels, and retrain on that)

every time the bot runs:
initialise a bot instance to call run_bot() to hold a conversation

with each customer chat, trigger sub-modules

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

'''


'''
ORDER:
run Classes to initialise all classes
run Knowledge to web scrape(note: doesn't do that within run),
create list of Theatres

run Bot


'''