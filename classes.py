__author__ = 'V'

'''
classes for knowledge - used when google showtimes scraping + book my show theatre listing

'''
from showtime import Time

'''
Movie
Each instance of Movie keeps track of its title(Cased) and
a set of theatres in which it is played
(no support for description yet, but could easily add it to the scraper)
'''
class Movie:
    # theatres is a set() String theatre_names where the movie is playing currently
    # String title
    # String description
    def __init__(self, title="", desc="", theatres=set()):
        self.title = title
        self.desc = desc
        self.theatres = theatres

    # String theatre
    def put(self, theatre):
        self.theatres.add(theatre)


'''
Theatre
Known set of Bangalore theatres created by parsing BookMyShow Cinema
listings for Bangalore, which are copied off the list of cinemas on
their site.
All Theatre instances are initialised in knowledge.py when parsing
When a theatre instance is initialised, it adds itself to the list of
total theatres

Each instance of Theatre keeps track of:
String bms_name: exact Cased title name as downloaded from book my show
String[] address: list of address keywords. example: ["Jayanagar", "Garuda Swagath Mall"]
String company_name: the company/name as a string examples: "PVR", "Inox LIDO", "Innovative Multiplex"
and a dictionary of String movieName:timings for that day. movieName is lowercase, timings is []Time
'''

class Theatre:
    city = "Bangalore"
    theatres = []

    def __init__(self, bms_name, address, company):
        self.movies = {}
        self.bms_name = bms_name
        self.address = address
        self.company = company
        Theatre.theatres.append(self)

    # String movie
    # Time[] timings ex: "[Time('10:30am')]
    def put(self, movie, timings):
        self.check()
        self.movies[movie.lower()] = timings

    # String movie
    # returns list of timings for movie
    def get(self, movie):
        self.check()
        return self.movies.get(movie.lower())

    # before allowing accesses, assert that all information is present
    def check(self):
        assert(len(self.theatres) == 81)


"""
classes for storing conversation information
instantiated by the bot
"""
class ChatLine:
    # Boolean who, String timestamp, String content
    def __init__(self, who_said=0, timestamp="00:00:00", content="test"):
        self.who = who_said
        self.timestamp = timestamp  # looks like 19:55:25
        self.content = content


class Conversation:
    #  String agentname, String customerNum, String text, ChatLine [] chatLines
    def __init__(self, chatLines, agentName="test_agent",
                 customerNum="test_customer", text="test"):
        self.agentName = agentName
        self.customerNum = customerNum
        self.text = text
        self.chatLines = chatLines

    '''retrieve all chats sent by the CUSTOMER
    returns a list of ChatLines'''

    def getCustomerChat(self):
        return [line for line in self.chatLines if not line.who]

    '''retrieve all chats sent by the AGENT
    returns a list of ChatLines'''

    def getAgentChat(self):
        return [line for line in self.chatLines if line.who]


'''
classes for bot
'''

'''
MovieRequest: object keep track of information that we are completely
sure of, which fits in with all the other information that we have
stored in the object

Title is String movie title, cased
num_tickets is Integer number of tickets
Theatre is String Theatre.bms_name, cased
date
time is instance of Time, time of showing
payment_method is 0 for COD, 1 for online

(currently nothing to support payment_method or comments)
'''
class MovieRequest:
    # takes in customer id
    def __init__(self, customer):
        self.fields = ["[]",0,"[]",'today',Time('3 am'),0]
        '''
        self.title = "[]"  # Cased
        self.num_tickets = 0  # integer
        self.theatre = "[]"  # bms_name
        self.date = "today"
        self.time = Time('3 am')
        self.payment_method = 0
        '''
        self.done = [0, 0, 0, 1, 0, 0]  # check for the six earlier attrs
        self.last = -1 # check the last changed attribute
        
        self.comments = ""
        self.customer = customer

    def remaining(self):
        return self.done

    def add_field(self,ind,field):
        self.done[ind] = 1
        self.last = ind
        self.fields[ind] = field
        return self

    def readout(self):
        t = (' for the {} showtime, '.format(self.fields[4].printout()) if self.done[4] else ", ")
        readout = '{} ticket{} for {} at {}{}{}'.format(
            self.fields[1], ('' if self.fields[1]==1 else "s"),
                              self.fields[0], self.fields[2],t, self.fields[3])
        return readout


'''
Keeping track of what we are learning.

state object keeps track of
1. Conversation conversation of total input from user,

2. Int question of the question we have just asked. corresponds to index of attribute in request.done.
    Initialised as 0, which means the initial question is about the movie.

3. MovieRequest req of all satisfied information

4. Options keeps track of a list of options, whether of movies or theatres,
where the option number is i+1, for index i of the item in the list

list of keys

Option is used in logic.py - if we are given a tagged numbers, and (there are
multiple items in state.options, indicating that the last thing the bot said
was a list of options AND the question isn't looking for time or  - there can be
multiple showtimes that the bot returns as possible examples, but people will
use the time value itself to refer to them, not the number), then
we should use that number to correspond to the item numbered in the options,
pick out that item, treat it like an equivalent to the case if tag_theats or
tag_movs had a single item, and rewrite the option list, either to [] or to a new
list
hence it must be re-created every time logic module runs

it is a list of theatre name keys
'''
class State:
    def __init__(self, resource):
        self.question = 0  # 0 for movies, 1 for num tickets, 2 for theatre

        self.options = []
        self.option_type = 0 #for theatres, 1 for movies

        self.timeout = 0

        self.req = MovieRequest(resource)

        chatLines = []
        self.conversation = Conversation(chatLines)

        # must be mutable so that the alias will mess with it
        self.s_time = []
        self.s_tday = []

    def add_line(self, line_string):
        self.conversation.chatLines.append(ChatLine(content=line_string))
