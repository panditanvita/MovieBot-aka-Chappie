__author__ = 'V'

import threading

from knowledge import get_theatres
from classes import Conversation, ChatLine, MovieRequest
from tokeniser import tokeniser, tag_tokens_number, tag_tokens_movies
from collections import deque
'''
Bot class:

Bot has access to single classifier, run at the beginning. each instance keeps track of all
its conversations, error logs and movie requests made.

-user should always be able to keep typing, and Bot will keep re-updating the submodules.
-Chat may be over multiple lines.

'''


class Bot:
    # classifier = run_classifier()   maybe
    '''
    Keeping track of all conversations in the record
    Keeping track of all requests in requests
    Keeping track of errors in error_log
    '''

    def __init__(self):
        self.records = []
        self.requests = []
        self.error_log = []

    '''
    run() function

    handles a movie request
    Take in all customer data
    run() function takes in incoming lines from user, uses tokenizer and
    spellcheck, just enough to preprocess and then send it to the relevant submodules.

    '''

    def run(self):
        ntm, ntt, trash = get_theatres()
        req = MovieRequest('test', ntm, ntt)
        conversation = Conversation()

        chat_buffer = deque()
        # accept input at all times
        # open separate thread which writes it to a buffer

        def add_to_buffer():
            while True:
                inp = raw_input()
                chat_buffer.appendLeft(inp)
                if inp.__eq__('bye'):
                    break

        buffer_thread = threading.Thread(name='buffer_thread', target=add_to_buffer)
        buffer_thread.start()

        # while buffer_thread has items in it, pop off items and process
        print("also happening")
        inp = buffer_thread.pop()
        print(inp)

        if inp.__eq__('bye'):
            print("Goodbye!")
            return

        # send input to tokenizer
        # todo how to support checking multiple lines at once?
        tokens = tokeniser(inp, ntm, ntt)

        #  track of current conversation-create and update
        # Conversation object
        conversation.chatLines.append(ChatLine(content=tokens))

        # understand the prepositions to find where the info is
        # todo submodule, for now check everything

        # return the numbers found in the input
        tagged_number = tag_tokens_number(tokens)

        # return the movies and theatres mentioned in the input
        # can only return known movies and theatres
        tag_movs, tag_theat = tag_tokens_movies(tokens)

        # logic for what to do if there is more than one of the above,
        # must narrow it down todo next

        # submodule for each attribute, each function
        # makes sure that what it inputs into the movie request is
        # correct. takes in chatline information
        # todo

        # finally, decisions: do we have enough information?
        # which questions must we ask to get more information?
        # maybe the selected movie is not playing in the selected theatre?
        # give alternate showtimes

        pass


bot = Bot()

bot.run()
