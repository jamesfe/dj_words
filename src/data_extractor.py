"""
A project to identify the patterns in words over an email conversation.

Some ideas:
1. Create a class that encapsulates the conversation
2. Create ability to bin words by time
3. Show line graph of word usage over time
4. Show histograms of word usage binned by year, month, week, etc.
"""


import arrow
import mailbox
import os
from operator import itemgetter


def find_all(a_str, sub):
    """
    Nice function to find all substrings

    :param a_str:
    :param sub:
    :return:
    """
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)


class ConversationData():
    """
    A class to wrap our mbox data file and provide analytics.
    """
    def __init__(self, mbox_file, configs):
        """
        Initialize a number of things.
        :return:
        """
        self.filename = mbox_file
        if os.path.isfile(mbox_file):
            self.mbox = mailbox.mbox(mbox_file)
        else:
            raise IOError("Can't find that file")

        self.config = dict()
        cfg_file = file(configs, 'r')
        for line in cfg_file:
            if line[0] != '#':
                parsed = line.strip().split("=")
                if len(parsed) != 2:
                    raise ValueError("Bad config file.")
                else:
                    self.config[parsed[0]] = parsed[1]
        self.messages = list()

    def get_message_list(self):
        """
        Provide a list of all the messages
        :return:
        """
        count = 0
        for msg in self.mbox:
            if msg['From'].find(self.config['tgt_email']) > -1:
                dtime = arrow.get(msg['Date'], 'ddd, D MMM YYYY HH:mm:ss ZZ')
                message = dict({'from': msg['From'],
                                'date': dtime,
                                'subject': msg['Subject']})
                # print msg['From'], msg['Subject'], msg['Date']
                count += 1
                # print len(msg.get_payload())

                self.messages.append(message)
        print count
        self.messages.sort(key=lambda item: item['date'])
        for k in self.messages:
            print k



if __name__ == '__main__':
    mb = ConversationData("../data/data.mbox", "./configs.cfg")
    mb.get_message_list()