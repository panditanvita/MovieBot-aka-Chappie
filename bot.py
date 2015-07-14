__author__ = 'V'

import threading

from knowledge import get_theatres
from classes import Conversation, ChatLine, MovieRequest
from tokeniser import tokeniser, tag_tokens_number, tag_tokens_time, tag_tokens_movies
from collections import deque
from logic import narrow
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
        self.ntm, self.ntt, trash = get_theatres()

    '''
    run() function

    handles a movie request
    Take in all customer data
    run() function takes in incoming lines from user, uses tokenizer and
    spellcheck, just enough to preprocess and then send it to the relevant submodules.

    '''

    def run(self):
        req = MovieRequest('test')
        chatLines = []
        conversation = Conversation(chatLines)

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

            # return the numbers found in the input
            tag_number = tag_tokens_number(tokens)
            tag_times = tag_tokens_time(tokens)

            # return the movies and theatres mentioned in the input
            # can only return known movies and theatres
            tag_movs, tag_theats = tag_tokens_movies(tokens, self.ntm, self.ntt)

            # logic for what to do if there is more than one of the above,
            # must narrow it down todo next
            evald = narrow(req, tag_movs, tag_theats, tag_number, tag_times, self.ntm, self.ntt)

            # ask a question to find out later information
            if evald is not 'ok':
                print(evald)
                print("Got it, thanks.")
            else:
                print req.readout()
                return

'''
bot = Bot()
bot.run()

'''