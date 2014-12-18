#! /usr/bin/env python

import os
import socket
import json
import random
from imgurpython import ImgurClient

class BMO:
    socket = None
    connected = False
    nickname = 'BMOBot'
    server = ''
    port = ''
    channels = []
    imgurClient = None

    def __init__(self):
        self.readConfig()
        self.socket = socket.socket()
        self.socket.connect((self.server, self.port))
        self.send("NICK %s" % self.nickname)
        self.send("USER %(nick)s %(nick)s %(nick)s :%(nick)s" % {'nick':self.nickname})

        while True:
            buf = self.socket.recv(4096)
            lines = buf.split("\n")
            for data in lines:
                data = str(data).strip()

                if data == '':
                    continue
                print "I<", data

                # server ping/pong?
                if data.find('PING') != -1:
                    n = data.split(':')[1]
                    self.send('PONG :' + n)
                    if self.connected == False:
                        self.perform()
                        self.connected = True

                args = data.split(None, 3)
                if len(args) != 4:
                    continue
                ctx = {}
                ctx['sender'] = args[0][1:]
                ctx['type']   = args[1]
                ctx['target'] = args[2]
                ctx['msg']    = args[3][1:]

                # whom to reply?
                target = ctx['target']
                if ctx['target'] == self.nickname:
                    target = ctx['sender'].split("!")[0]

                # directed to the bot?
                if ctx['type'] == 'PRIVMSG' and (ctx['msg'].lower()[0:len(self.nickname)] == self.nickname.lower() or ctx['target'] == self.nickname):
                    # something is speaking to the bot
                    query = ctx['msg']
                    if ctx['target'] != self.nickname:
                        query = query[len(self.nickname):]
                        query = query.lstrip(':,;. ')
                    # do something intelligent here, like query a chatterbot
                    print 'someone spoke to us: ', query
                    msg = ctx['msg'].split(' ')
                    options = {'randimgur':self.randimgur()}
                    for cmd in options:
                        if cmd in msg:
                           action = options[cmd]
                        else:
                            action = 'available commands: !help'
                    self.say(action, target)

    def randimgur(self):
        imgs = self.imgurClient.gallery(section='top', sort='time', page=random.randint(0,15), window='week', show_viral=True)
        return 'May the odds be ever in your favor. ' + imgs[random.randint(0,15)].link

    def send(self, msg):
        print "I>",msg
        self.socket.send(msg+"\r\n")

    def say(self, msg, to):
        self.send("PRIVMSG %s :%s" % (to, msg))

    def perform(self):
        #self.send("PRIVMSG R : Register <>")
        self.send("PRIVMSG R : Login <>")
        self.send("MODE %s +x" % self.nickname)
        for c in self.channels:
            self.send("JOIN %s" % c)
            # say hello to every channel
            self.say('hello world!', c)

    def readConfig(self):
        config = json.loads(open('config', 'r').read())
        self.server = config['server1_url']
        self.port = int(config['server1_port'])
        for channel in config['server1_channels'].split(","):
            self.channels.append(channel)
        self.imgurClient = ImgurClient(config['imgur_client_id'], config['imgur_client_secret'])

if __name__ == "__main__" :
    BMO()
