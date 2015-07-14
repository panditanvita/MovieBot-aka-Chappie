__author__ = 'V'

'''
classes for knowledge - google showtimes scraping

'''

'''
Movie
Each instance of Movie keeps track of a set of theatres in which it is played
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
String bms_name: exact title name as downloaded from book my show
String[] address: list of address keywords. example: ["Jayanagar", "Garuda Swagath Mall"]
String company_name: the company/name as a string examples: "PVR", "Inox LIDO", "Innovative Multiplex"
and a dictionary of String movieName:timings for that day
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
    # String[] timings ex: "10:30am"
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
classes for parser

never directly change the conversation and chatline objects.

todo: fix parser to reflect change of direction of Conversation arguments
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


class MovieRequest:
    # takes in customer id
    def __init__(self, customer):
        self.title = "[]"  # lower
        self.num_tickets = 0  # integer
        self.theatre = "[]"  # lower
        self.date = "[]"
        self.time = "[]"
        self.payment_method = 0

        self.done = [0, 0, 0, 0, 0, 0]  # check for the six earlier attrs
        self.comments = ""
        self.customer = customer

    def remaining(self):
        return self.done

    def add_title(self, title):
        self.done[0] = 1
        self.title = title

    def add_tickets(self, numTickets):
        self.done[1] = 1
        self.num_tickets = numTickets

    def add_theatre(self, theatre):
        self.theatre = theatre
        self.done[2] = 1
        return True, ""

    def add_date(self, date): # either today, tomorrow, or a day of the week
        self.date = date
        self.done[3] = 1
        return True, ""

    def add_time(self, time):
        self.time = time
        self.done[4] = 1
        return True, ""

    # 0 is COD, 1 is online
    def add_payment(self, payment):
        self.payment_method = payment
        self.done[5] = 1

    def readout(self):
        readout = '{} tickets for {} at {},' \
                  ' for the {} showtime, {}'.format(self.num_tickets, self.title, self.theatre, self.time, self.date)
        return readout

