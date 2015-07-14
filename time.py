__author__ = 'V'

'''
Time class
Keeps track of hours[0-24] and minutes[0-60]
All showtimes are instances of Time

all user-parsed times should be able to be turned into instances of Time
'''
import re

class Time:
    # takes in String time, can be in the format 9:35, 9.35, 0935, 935pm,
    # somewhere need to substitute words nine-thirty for 9:30
    # assumes 11 and 12 are am, 1-10 is pm unless mentioned otherwise

    def __init__(self, time):
        self.hours, self.minutes = self.parse_time(time)

    def parse_time(self, time):
        # todo
        # todo maybe numbers next to each other should be one token
        # re.match(r"^\d+[.: ]\d{2}", time) todo regex capturing groups
        hours = time[0]
        minutes = time[2:]
        return hours, minutes