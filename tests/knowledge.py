__author__ = 'V'

from MovieBot.classes import *
from MovieBot.showtime import *

# for testing, we want known ntm, ntt dictionaries
def get_info():
    req1 = MovieRequest("test")
    req2 = MovieRequest("test")

    ntt, ntm = {}, {}

    times1 = [Time('6pm'), Time('630pm'), Time('730pm')]
    times2 = [Time('9am'), Time('1030am'), Time('1730pm'), Time('10pm')]

    #title, description, theatres
    m1 = Movie("Zabod")
    m2 = Movie("Interesting Short Stories")

    #bms_name, address, company
    t1 = Theatre("t1",['outer','ring''road'], 'pvr')
    t1.put('zabod',times1)
    t2 = Theatre("t2",['outer','koramangala'], 'cinemax')
    t2.put('zabod',times2)
    t3 = Theatre("t3",['marathalli'], 'innovative multiplex')
    t3.put('interesting short stories', times2)
    ntt['t1'] = t1
    ntt['t2'] = t2
    ntt['t3'] = t3

    ntt['zabod'] = m1
    ntt['interesting short stories'] = m2

    req1.add_title('zabod')
    return req1, req2, ntm, ntt