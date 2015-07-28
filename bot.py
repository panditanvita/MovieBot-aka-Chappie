__author__ = 'V'

import threading

from knowledge import get_theatres
from classes import State
from tokeniser import tokeniser, get_tags
from collections import deque
from logic import narrow


class Bot:
    requests = [] #Keeping track of all requests in requests
    ntm, ntt, trash = get_theatres() # should not be changed after instantiation
    '''
    bot is tied to a unique user conversation
    resource is unique conversation identifier. for a customer, it should be their number
    we kill the bot when the conversation closes

    '''
    def __init__(self, resource='test'):
        self.state = State(resource)

    '''
    handle potential crashing
    '''
    def sleek_get_response(self, message):
        try:
            response = self.get_response(message)
        except:
            response = "Chappie can't quite understand you!"
        return response
            
    '''
    the bot thinks of what to say...

    handles movie-related String input from the user
    function takes in incoming lines from user then sends it to the relevant submodules.
    current state of the Bot is kept track of in State object
    returns new state of bot and the bot response

     Submodules:
    - function tokeniser returns spellchecked lists of tokens
    - multiple tagging functions tag tokens for times, numbers, movie titles, addresses
    - tagged tokens are sent to logic, to be checked for mutual compatibility and then inserted
    into the MovieRequest object
    - logic output is given to function narrow, to decide which questions to ask

    Int question keeps track of which question we are on. -1 for no question, index of
    MovieRequest.done for relevant question
    '''
    def get_response(self, message):
        req, question, options = self.state.req, self.state.question, self.state.options

        #closing
        if message.lower() == "bye":
            return "Goodbye!"

        # send input to tokenizer
        tokens = tokeniser(message)[1]

        if len(tokens) < 1: return "..?"

        #  track of current conversation-create and update
        # Conversation object
        self.state.add_line(tokens[0])

        # understand the prepositions to better find where the info is
        # todo submodule, for now check everything, which works pretty well tbh
        # at [theatre], watch|see [movie], at [time]

        tags = get_tags(tokens, Bot.ntm, Bot.ntt, question)

        # logic for what to do if there is more than one of the above,
        # must narrow it down
        # input items into the MovieRequest object based on the current
        # state of the tags
        # returns the new question that it needs to know to finish the request
        # returns statement, the question itself
        question, statement = narrow(self.state, tags, Bot.ntm, Bot.ntt)

        # if we are still on the same question, add to the counter
        # works because question is an immutable Int
        if self.state.question == question:
            self.state.timeout += 1
        else: self.state.timeout = 0
        self.state.question = question

        if len(self.state.conversation.chatLines)==1: statement = "Hello, this is MovieBot!\n"+ statement

        return statement

    '''
    run() function

    used for debugging, can interact on console. user should always be able to keep typing,
    and Bot will keep re-updating the submodules.

    two threads:
    1. for constantly updating raw input from the user and writing to a buffer
    2. for popping items from the buffer and processing in order
    thread 1 signals to thread 2 with a new_text Event every time a new text is sent

    keeps track of and constantly updates State.
    '''

    def run(self):
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
            print(self.state.req.readout())
            Bot.requests.append(self.state.req)
            end_buffer.set()
            return

        # main thread
        # while buffer_thread has items in it, pop off items and process
        while True:
            new_text.wait(timeout=20) # timeout wait doesn't seem to do anything todo
            try:
                inp = chat_buffer.pop()
                new_text.clear()
            except IndexError:
                continue

            if inp.lower() == ('bye'):
                print("Goodbye!")
                close()
                return

            response = self.get_response(inp)

            if self.state.question == -1:
                print("Got it, thanks. Bye!")
                close()
                return
            else:
                # ask a question to find out later information
                print(response)
'''
for debugging
'''
bot = Bot()
bot.run()
'''
bye
'''
