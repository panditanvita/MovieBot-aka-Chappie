__author__ = 'V'

# sleek xmpp echobot boilerplate

import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

from bot import Bot

class SleekMovieBot(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        # If you wanted more functionality, here's how to register plugins:
        # self.register_plugin('xep_0030') # Service Discovery
        # self.register_plugin('xep_0199') # XMPP Ping

        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

        #hash map of unique resource key (customer number) to a selected bot instance
        self.bots = {}

    def session_start(self, event):
        self.send_presence()
        #self.get_roster()

        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        #
        # try:
        #     self.get_roster()
        # except IqError as err:
        #     logging.error('There was an error getting the roster')
        #     logging.error(err.iq['error']['condition'])
        #     self.disconnect()
        # except IqTimeout:
        #     logging.error('Server is taking too long to respond')
        #     self.disconnect()

    def message(self, msg):
        key = msg['from']
        if not self.bots.has_key(key):
            self.bots[key] = Bot()
        bot = self.bots[key]

        body = msg['body']
        if msg['type'] in ('chat', 'normal'):
            response = bot.get_response(body)
            msg.reply(response).send()

            if response == "Goodbye!":
                self.bots.pop(key)


if __name__ == '__main__':
    # Ideally use optparse or argparse to get JID,
    # password, and log level.

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = SleekMovieBot('somejid@example.com', 'use_getpass')
    xmpp.connect()
    xmpp.process(block=True)