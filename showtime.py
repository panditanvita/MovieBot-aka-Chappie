__author__ = 'V'

'''
Time class
Keeps track of hours Int [0-23] and minutes Int[0-60]
All showtimes are instances of Time

input: takes in String time, can be in the format 9:35, 9.35, 0935, 935pm, 935 pm
all user-parsed times should be able to be turned into instances of Time
'''
import re

class Time:
    def __init__(self, time):
        self.hours, self.minutes = self.parse_time(time)

    '''
    parse_time()
    helper function called in __init__ only
    turns strings in the formats '1', '10','130','01:30','1030','1030pm','10 30 pm', 10pm','1am', '1.00am'
    and likewise into Time objects
    '''
    def parse_time(self,time):
        time = time.lower()
        assert(len(time) <= 8) #biggest possible "11 30 pm"

        #insert space after numbers, before am/pm
        i = re.search(r"\d[ap]m",time)
        if i is not None:
            i = i.start()+1
            time = time[:i] + ' ' + time[i:]
        # split
        t = re.split(r"[.: ]", time)

        # size of split must be <= 3. if three, assert last part is am/pm
        assert(0 < len(t) <= 3)

        #  PARSING HELPER FUNCTIONS

        # sort out hours into 0-23
        # flag is None, am or pm
        # assumes 11 and 12 are am, 1-10 is pm unless mentioned otherwise
        # input Int hours, output Int hours[0:23]
        def hflag(hours,flag=None):
            assert(0 <= hours < 24)
            h = 0
            if flag == None:
                if hours <=10:
                    h = 12+hours
                else: # 11 or 12, or 13-23
                    h = hours
            elif flag == 'am':
                h = hours
            elif flag == 'pm':
                if hours <=24:
                    h = 12+hours
            else:
                assert(False)
            return h

        # for single-chunk times of different lengths
        # flag is None, am or pm - just passes flag onwards to hflag function
        # format \d+ (9 or 10 or 930 or 0930 or 1130)
        # input String Time, output Int hours, Int minutes
        def p1(t0,flag=None):
            assert(len(t0) in range(1,5))
            h,m = 0,0
            if len(t0) == 1 or len(t0)==2:
                h = hflag(int(t0),flag)
                m = 0
            elif len(t0) == 3:
                h = hflag(int(t0[0]),flag)
                m = int(t0[1:])
            elif len(t0) == 4:
                h = hflag(int(t0[:2]),flag)
                m = int(t0[2:])
            return h, m

        hours,minutes = 0,0
        if len(t) == 3: # format \d+,\d+,am|pm
            assert(re.match(r'am|pm',t[2]) is not None)
            minutes = int(t[1])
            hours = hflag(int(t[0]),t[2])

        if len(t) ==2: # format \d+(9 or 930 or 0930),am|pm  OR \d+,\d+
            if t[1] == 'am' or t[1] == 'pm':
                hours, minutes = p1(t[0],t[1])
            else:
                hours = hflag(int(t[0]))
                minutes = int(t[1])

        if len(t) == 1:
            hours, minutes = p1(t[0])

        assert(0 <= hours < 24)
        assert(0 <= minutes < 60)
        return hours, minutes

    '''
    # get_frame()
    # returns Boolean if time is within the frame specified
    # frames: morning, afternoon or evening or night [0, 1, 2, 3]
    # note that the frames overlap
    # set up so that 6 to 12 is morning
    # 12-16 is afternoon
    # 15 to 22 is evening
    # 18 onwards is night
    '''
    def get_frame(self, frame):
        # generators pretty
        def r(a,b): return a < self.hours <= b
        frames = [r(6,12),r(12,16),r(15,22),r(18,24)]
        return frames[frame]

    '''
    return list of frames that the time belongs to, should be 1 or 2 frames
    '''
    def ask_frame(self):
        return [frame for frame in range(4) if self.get_frame(frame)]

    def printout(self):
        m = self.minutes
        if m < 10: sm = str(0) + str(m)
        else: sm = str(m)
        out = "{}:{}".format(self.hours,sm)
        return out

'''
time-related functions
'''
frame_strings = ['morning','afternoon','evening','night']

'''
input: number in 0,1,2,3
frames: morning, afternoon or evening or night [0, 1, 2, 3]
return string name of frame
'''

def frame_to_string(frame):
    return frame_strings[frame]

'''
input: frame_string in frame_strings
return number of frame
'''
def string_to_frame(frame_string):
    return frame_strings.index(frame_string)

def frame_to_time(frame):
    times = [Time('11 am'),Time('2 pm'), Time('5 pm'), Time('9 pm')]
    return times[frame]