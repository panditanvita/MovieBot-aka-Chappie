__author__ = 'V'

import threading

from knowledge import get_theatres
from classes import Conversation, ChatLine, MovieRequest
from tokeniser import tokeniser, tag_tokens_number, tag_tokens_movies
from collections import deque
from logic import narrow
'''
Bot class:

Bot has access to unchangeable dictionaries of movie names and theatres, which come from the knowledge base
each bot instance keeps track of all its conversations, #todo error logs and movie requests made.

MovieBot gives a valid response to every line of movie-related input

Two options for running:
1. with a debug flag (in which case, call bot.run() to play with the features,
and the bot will interact using System.in and System.out
2. without the debug flag, in which case the bot will keep track of its state in the MovieRequest and conversation
objects created at instantiation, and you must call the sleek_get_response(message) function to get the bot's
response to a particular input

bot corresponds to a single conversation, as the final product of a successful conversation should be a single
completed movie request

'''
class Bot:
    # classifier = run_classifier()   maybe
    requests = []
    ntm, ntt, trash = get_theatres() # should not be changed after instantiation

    '''
    Keeping track of all conversations in the record
    Keeping track of all requests in requests
    Keeping track of errors in error_log
    '''

    def __init__(self, debug=True, resource='test'):

        self.debug = debug

        if not self.debug:
            self.req = MovieRequest(resource)
            chatLines = []
            self.conversation = Conversation(chatLines)
            self.question = 0

    '''
    sleek_get_response(String message)
    for responding to the SleekXMPP bot

    # if debug is false, then bot is called through sleekxmpp
    # takes in a String message from the customer
    # returns a String response from the bot, updates stored states of current instance
    to reflect new information given in the conversation
    # response should be exactly as per the debug==True response

    '''
    def sleek_get_response(self, message):
        assert(self.debug==False)

        self.question, response = self.get_response(message, self.req, self.conversation, self.question)

        if len(self.conversation.chatLines)==1: return "Hello, this is MovieBot!\n"+response
        return response


    '''
    the bot thinks of what to say...

    handles movie-related input from the user
    function takes in incoming lines from user then sends it to the relevant submodules.

     Submodules:
    - function tokeniser returns spellchecked lists of tokens
    - multiple tagging functions tag tokens for times, numbers, movie titles, addresses
    - tagged tokens are sent to logic, to be checked for mutual compatibility and then inserted
    into the MovieRequest object
    - logic output is given to function narrow, to decide which questions to ask
    - Int question keeps track of which question we are on. -1 for no question, index of
    MovieRequest.done for relevant question
    '''
    def get_response(self, message, req, conversation, question):
        # send input to tokenizer
        tokens = tokeniser(message)[1]

        if len(tokens) < 1:
            return question, "..?"

        #  track of current conversation-create and update
        # Conversation object
        conversation.chatLines.append(ChatLine(content=tokens[0]))

        # understand the prepositions to better find where the info is
        # todo submodule, for now check everything, which works pretty well tbh
        # at [theatre], watch|see [movie], at [time]

        # return the different numbers found in the input
        # tries to tell the difference between number of tickets, t_num
        # times of day, t_day
        # showtimes []Time times
        # for example, looks for a number before "tickets"
        all_nums, tday, t_num, times = tag_tokens_number(tokens, question)

        # return the movies and theatres mentioned in the input
        # can only return known movies and theatres
        # use question to tell which question we are on, for more useful tagging
        tag_movs, tag_theats = tag_tokens_movies(tokens, Bot.ntm, Bot.ntt, question)

        #print([t.printout() for t in times]) check times are alright

        # logic for what to do if there is more than one of the above,
        # must narrow it down
        # input items into the MovieRequest object based on the current
        # state of the tags
        # returns the new question that it needs to know to finish the request
        # returns statement, the question itself
        question, statement = narrow(req, tag_movs, tag_theats, tday, t_num, times, Bot.ntm, Bot.ntt)

        return question, statement

    '''
    run() function

    used for debugging, can interact on console. user should always be able to keep typing,
    and Bot will keep re-updating the submodules.

    two threads:
    1. for constantly updating raw input from the user and writing to a buffer
    2. for popping items from the buffer and processing in order
    thread 1 signals to thread 2 with a new_text Event every time a new text is sent

    keeps track of and constantly updates state within
    1. Conversation conversation of total input from user,
    2. Int question of the question we have just asked
    3. MovieRequest req of all satisfied information
    '''

    def run(self):
        assert(self.debug==True)

        req = MovieRequest('test')
        chatLines = []
        conversation = Conversation(chatLines)

        question = 0  # 0 for movies, 1 for num tickets, 2 for theatre
        chat_buffer = deque()

        # accept input at all times
        # open separate thread which writes it to a buffer
        new_text = threading.Event()
        end_buffer = threading.Event()

        def add_to_buffer():
            while True:
                inp = raw_input()
                chat_buffer.appendleft(inp)
                new_text.set()
                if inp.__eq__('bye'):
                    return
                if end_buffer.is_set():
                    return

        buffer_thread = threading.Thread(name='buffer_thread', target=add_to_buffer)
        buffer_thread.start()

        def close():
            print(req.readout())
            Bot.requests.append(req)
            end_buffer.set()
            return

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
                close()
                return

            question, e2 = self.get_response(inp, req, conversation, question)

            # ask a question to find out later information
            # todo: make it so that the bot doesn't have to say something after every single text,
            # todo let it combine texts which come in within a few seconds of each other into one input set
            # todo to support checking multiple lines at once - check past conversation lines
            if question != -1:
                print(e2)
            else:
                print("Got it, thanks.")
                close()
                return

'''
for debugging

bot = Bot()
bot.run()

bye
'''
