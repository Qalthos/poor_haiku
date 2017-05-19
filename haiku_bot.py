#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    haiku_bot is a Twisted IRC bot to tell people when they've made cool
#    haikus.
#
#    Copyright ©2017 Nathaniel Case
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import random
import re

from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor


NOT_ALPHA = re.compile(r'[^a-zA-Z]')


def count_sylables(word):
    word = NOT_ALPHA.sub('', word).lower()
    if not word:
        return 0

    if word[-1] == 'e':
        word = word[:-1]

    # Create a list of either 'x' (vowel) or ' ' (non-vowel) for each letter
    # in `word`
    tmp = []
    for char in word:
        if char in 'aeiouy':
            tmp.append('x')
        else:
            tmp.append(' ')

    return len(''.join(tmp).split()) or 1


def is_haiku(string):
    words = string.replace('_', ' ').split()

    syllables = 0
    for word in words:
        sylables += count_syllables(word)

    return syllables == 17


def haiku_time(self):
    responses = [
        "That is a haiku! / But I am just a robot / Could be mistaken",
        "Haiku detected! / That just makes me so happy / (I hope I'm not wrong)",
        "I have learned English / Just to listen for haiku / This seems like a waste",
    ]

    return random.choice(responses)


class HaikuBot(IRCClient):
    bot_name = "might_be_haiku"
    channel = "#rit-foss"
    versionNum = 1
    sourceURL = "http://github.com/Qalthos/poor_haiku"
    lineRate = 1

    def __init__(self, *args, **kwargs):
        self.sauce = re.compile(r'{}([:,])? s(our|au)ce'.format(self.nickname))
        self.halp = re.compile(r'{}([:,])? h[ea]lp'.format(self.nickname))
        self.thanks = re.compile(r'({0}([:,])?  thanks)|(thanks.*{0})'.format(self.nickname))
        self.love = re.compile(r'{}: <3'.format(self.nickname))

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)
        self.factory.add_bot(self)
        print('{} joined {}'.format(self.bot_name, self.channel))

    def help_me(self, user, channel):
        self.msg(channel, "source: display my source / GitHub repository / go there to file bugs")
        self.msg(channel, "help: display this text / how you got to this message / in the first place, silly".format(user))

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]

        if self.sauce.match(msg):
            self.msg(channel, 'I am from this link / it is not a haiku so / please be nice to me')
            self.msg(channel, self.sourceURL)

        elif self.halp.match(msg):
            self.help_me(user, channel)

        #elif self.thanks.match(msg):
        #    self.msg(channel, "{}: You're welcome!".format(user))

        #elif self.love.match(msg):
        #    self.msg(channel, 'I <3 you too, {}'.format(user))

        elif is_haiku(msg):
            self.msg(channel, haiku_time())


class HaikuBotFactory(ReconnectingClientFactory):
    active_bot = None

    def __init__(self, protocol=HaikuBot):
        self.protocol = protocol
        self.channel = protocol.channel
        IRCClient.nickname = protocol.bot_name
        IRCClient.realname = protocol.bot_name

    def add_bot(self, bot):
        self.active_bot = bot


if __name__ == '__main__':
    # create factory protocol and application
    f = HaikuBotFactory()

    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    reactor.run()
