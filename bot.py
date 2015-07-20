__author__ = 'V'

import threading

from knowledge import get_theatres
from classes import Conversation, ChatLine, MovieRequest
from tokeniser import tokeniser, tag_tokens_number, tag_tokens_movies
from collections import deque
from logic import narrow
'''
Bot class:

Bot has access to single classifier, run at the beginning. each instance keeps track of all
its conversations, error logs and movie requests made.

-user should always be able to keep typing, and Bot will keep re-updating the submodules.
-Chat may be over multiple lines.

Two options for running:
1. with a debug flag (in which case, call bot.run() to play with the features,
and the bot will interact using System.in and System.out
2. without the debug flag, in which case the bot will keep track of its state in the MovieRequest and conversation
objects created at instantiation, and you must call the sleek_get_reponse(message) function to get the bot's
response to a particular input

'''
class Bot:
    # classifier = run_classifier()   maybe
    requests = []
    '''
    Keeping track of all conversations in the record
    Keeping track of all requests in requests
    Keeping track of errors in error_log
    '''

    def __init__(self, debug=True, resource='test'):

        self.ntm, self.ntt, trash = get_theatres() # should not be changed after instantiation

        self.debug = debug

        if not self.debug:
            self.req = MovieRequest(resource)
            chatLines = []
            self.conversation = Conversation(chatLines)

        self.question = -1

    '''
    sleek_get_response(String message)
    for responding to the SleekXMPP bot
    # if debug is false, then bot is called through sleekxmpp
    #takes in a String message from the customer
    # returns a String response from the bot, updates stored states to reflect new information given in
    # the conversation
    # reponse should be exactly as per the debug==True response
    '''
    def sleek_get_response(self, message):
        assert(self.debug==False)

        tokens = tokeniser(message)[1]

        if len(tokens) < 1: return "..?"

        self.conversation.chatLines.append(ChatLine(content=tokens[0]))

        all_nums, tday, t_num,times = tag_tokens_number(tokens, self.question)

        tag_movs, tag_theats = tag_tokens_movies(tokens, self.ntm, self.ntt, self.question)

        self.question, e2 = narrow(self.req, tag_movs, tag_theats, tday, t_num, times, self.ntm, self.ntt)

        # ask a question to find out later information
        if e2 == "ok":
            return self.req.readout()
        else:
            return e2





    '''
    run() function

    handles a movie request from the user
    run() function takes in incoming lines from user then send it to the relevant submodules.

    two threads:
    1. for constantly updating raw input from the user and writing to a buffer
    2. for popping items from the buffer and processing in order
    thread 1 signals to thread 2 with a new_text Event every time a new text is sent

    Submodules:
    - function tokeniser returns spellchecked lists of tokens
    - multiple tagging functions tag tokens for times, numbers, movie titles, addresses
    - tagged tokens are sent to logic, to be checked for mutual compatibility and then inserted
    into the MovieRequest object
    - logic output is given to function narrow, to decide which questions to ask
    - Int question keeps track of which question we are on. -1 for no question, index of
    MovieRequest.done for relevant question
    '''

    def run(self):
        assert(self.debug==True)

        req = MovieRequest('test')
        chatLines = []
        conversation = Conversation(chatLines)

        question = -1  # 0 for movies, 1 for num tickets, 2 for theatre
        chat_buffer = deque()

        # accept input at all times
        # open separate thread which writes it to a buffer
        new_text = threading.Event()

        def add_to_buffer():
            while True:
                inp = raw_input()
                chat_buffer.appendleft(inp)
                new_text.set()
                if inp.__eq__('bye'):
                    break

        buffer_thread = threading.Thread(name='buffer_thread', target=add_to_buffer)
        buffer_thread.daemon = True
        buffer_thread.start()

        print("Hi")
        # main thread
        # while buffer_thread has items in it, pop off items and process
        while True:
            new_text.wait(timeout=20) # timeout wait doesn't seem to do anything todo
            try:
                inp = chat_buffer.pop()
                new_text.clear()
            except IndexError:
                continue

            if inp.__eq__('bye'):
                print("Goodbye!")
                print(req.readout())
                return

            # send input to tokenizer
            # todo how to support checking multiple lines at once?
            tokens = tokeniser(inp)[1]

            if len(tokens) < 1:
                print("..?")
                continue
            #  track of current conversation-create and update
            # Conversation object
            conversation.chatLines.append(ChatLine(content=tokens[0]))

            # understand the prepositions to find where the info is
            # todo submodule, for now check everything
            # at [theatre], watch|see [movie], at [time]

            # return the different numbers found in the input
            # tries to tell the difference between number of tickets, t_num
            # times of day, t_day
            # showtimes []Time times
            # for example, looks for a number before "tickets"
            all_nums, tday, t_num,times = tag_tokens_number(tokens, question)

            # return the movies and theatres mentioned in the input
            # can only return known movies and theatres
            # use question to tell which question we are on, for more useful tagging
            tag_movs, tag_theats = tag_tokens_movies(tokens, self.ntm, self.ntt, question)

            #print([t.printout() for t in times]) check times are alright

            # logic for what to do if there is more than one of the above,
            # must narrow it down
            # input items into the MovieRequest object based on the current
            # state of the tags
            # returns the new question that it needs to know to finish the request
            # returns e2, the question itself
            question, e2 = narrow(req, tag_movs, tag_theats, tday, t_num, times, self.ntm, self.ntt)

            # ask a question to find out later information
            if e2 is not "ok":
                print(e2)
            else:
                print("Got it, thanks.")
                print(req.readout())
                return

'''
bot = Bot()
bot.run()

bye
'''
