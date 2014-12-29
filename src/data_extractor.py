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
from nltk.corpus import stopwords
import nltk
import string
from pytz import timezone


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
                # boundary = msg.get_boundary()
                # if boundary is not None:
                #     bounds = [m.start() for m
                #               in re.finditer(boundary, str(msg))]
                # else:
                #     bounds = list()
                # if len(bounds) > 2:
                #     message['text'] = str(msg)[bounds[1]:bounds[2]]
                # else:
                #     message['text'] = None
                pl = None
                if msg['Subject'].find(":") == -1:
                    finished = False
                    pl = msg.get_payload()
                    while finished is False:
                        if isinstance(pl, str):
                            finished = True
                        elif isinstance(pl, list):
                            pl = pl[0].get_payload()
                        else:
                            raise ValueError("Non-list, non-str payload?")
                            break
                message['text'] = self.clean_text(str(pl))

                if message['text'] is not None:
                    self.messages.append(message)
                    count += 1
        # print count
        self.messages.sort(key=lambda item: item['date'])

    def clean_text(self, intext):
        """
        clean text
        :param intext:
        :return:
        """
        intext = intext.lower()
        exclude = set(string.punctuation)
        intext = ''.join(ch for ch in intext if ch not in exclude)

        return intext

    def show_messages(self):
        """
        show all the messages
        :return:
        """
        for msg in self.messages:
            print msg['text']

    def build_distribution(self, msgid):
        """
        Get a frequency distribution for a certain email
        :param msgid:
        :return:
        """
        if msgid > len(self.messages):
            raise IndexError("Too big.  Pick a smaller index.")

        word_tokens = nltk.word_tokenize(self.messages[msgid]['text'])
        clean_words = [w for w in word_tokens
                       if not w in stopwords.words('english')]
        full_dist = nltk.FreqDist(clean_words)
        return full_dist

    def gather_full_dist(self):
        """
        figure out the most used words in this conversation
        :return:
        """
        full_dist = dict()
        for ind, msg in enumerate(self.messages):
            dist = self.build_distribution(ind)
            for p in dist:
                if p in full_dist:
                    full_dist[p] += dist[p]
                else:
                    full_dist[p] = dist[p]
        return full_dist


if __name__ == '__main__':
    mb = ConversationData("../data/data2.mbox", "./configs.cfg")
    mb.get_message_list()

    # mb.show_messages()
    i = mb.gather_full_dist()
    p = i.items()

    # p.sort(key=lambda item: item[1], reverse=True)
    # for k in p:
    #     print k

    ofile = file("outfile.txt", 'w')
    for k in p:
        for i in range(k[1]):
            ofile.write(k[0] + " ")
    ofile.close()
