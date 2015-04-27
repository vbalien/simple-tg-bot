# -*- coding: utf-8 -*-
import subprocess
import re
from threading import Thread

class TGBot(object):
    __autoread__ = False

    botThread = None
    botProc = None
    TG_CLI_PATH = '/home/vbalien/tg'

    ansi_escape = re.compile(r'\x1b[^m]*m')

    COLOR_RED="\033[0;31m"
    COLOR_REDB="\033[1;31m"
    COLOR_NORMAL="\033[0m"
    COLOR_GREEN="\033[32;1m"
    COLOR_GREY="\033[37;1m"
    COLOR_YELLOW="\033[33;1m"
    COLOR_BLUE="\033[34;1m"
    COLOR_MAGENTA="\033[35;1m"
    COLOR_CYAN="\033[36;1m"
    COLOR_LCYAN="\033[0;36m"
    COLOR_INVERSE="\033[7m"

    #: Patterns
    PAT_FROM_USER = (COLOR_BLUE + '[')
    PAT_FROM_GROUP = (COLOR_MAGENTA + '[')
    PAT_START_CHAT = (COLOR_BLUE + ' >>> ')
    PAT_BEGIN_USER = (COLOR_NORMAL + ' ' + COLOR_RED)
    PAT_END_USER = PAT_START_CHAT
    PAT_BEGIN_GROUP = (' ' + COLOR_NORMAL + ' ' + COLOR_MAGENTA)
    PAT_END_GROUP = COLOR_NORMAL + PAT_BEGIN_USER

    #: Message Types
    TYPE_NONE = 0
    TYPE_USER = 1
    TYPE_GROUP = 2

    def botCore(self):
        self.botProc = subprocess.Popen(
            [self.TG_CLI_PATH+'/bin/telegram-cli', '-k', self.TG_CLI_PATH+'/tg-server.pub'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        endline = True
        message = None
        msgType = self.TYPE_NONE
        fromUser = None
        fromGroup = None

        for line in iter(self.botProc.stdout.readline, ''):
            line = line.decode('utf-8')
            print(line.rstrip())
            if(not endline):
                message += line
                if line.endswith('[0m\n'):
                    message = message.rstrip('[0m\n')
                    endline = True

            #: Is User Chat
            if((self.PAT_FROM_USER in line) and (self.PAT_START_CHAT in line)):
                msgType = self.TYPE_USER
                fromUser = line[line.find(self.PAT_BEGIN_USER) + len(self.PAT_BEGIN_USER):]
                fromUser = fromUser[:fromUser.find(self.PAT_END_USER)]
                message = line[line.find(self.PAT_START_CHAT) + len(self.PAT_START_CHAT):]
                
                if not line.endswith("[0m\n"):
                    endline = False

            #: Is Group Chat
            if((self.PAT_FROM_GROUP in line) and (self.PAT_START_CHAT in line)):
                msgType = self.TYPE_GROUP
                fromUser = line[line.find(self.PAT_BEGIN_USER) + len(self.PAT_BEGIN_USER):]
                fromUser = fromUser[:fromUser.find(self.PAT_END_USER)]
                fromGroup = line.split(self.COLOR_MAGENTA)[2].split(self.COLOR_NORMAL)[0]
                message = line[line.find(self.PAT_START_CHAT) + len(self.PAT_START_CHAT):]
                if not line.endswith("[0m\n"):
                    endline = False

            #: execute command
            if(endline and message is not None):
                # escape ANSI Code
                message = self.ansi_escape.sub('', message)
                fromUser = self.ansi_escape.sub('', fromUser)
                if(msgType == self.TYPE_GROUP):
                    fromGroup = self.ansi_escape.sub('', fromGroup)

                self.command(message = message.strip(),
                    msgType = msgType,
                    fromUser = fromUser,
                    fromGroup = fromGroup)
                if(self.__autoread__):
                    peer = fromGroup
                    if(peer is None):
                        peer = fromUser
                    self.readChat(peer)
                endline = True
                message = None
                msgType = self.TYPE_NONE
                fromUser = None
                fromGroup = None
        pass

    def readChat(self, peer):
        cmd = 'mark_read '+peer.replace(' ','_')+'\n'
        self.botProc.stdin.write(cmd.encode('utf-8'))
        self.botProc.stdin.flush()
        pass

    def sendMsg(self, peer, text):
        if(('\n' in text)or('\r' in text) or ('\r\n' in text)):
            fp=open('tmp','w')
            fp.write(text)
            fp.close()
            cmd = 'send_text '+peer.replace(' ','_')+' tmp\n'
        else:
            cmd = 'msg '+peer.replace(' ','_')+' '+ text +'\n'
        self.botProc.stdin.write(cmd.encode('utf-8'))
        self.botProc.stdin.flush()
        pass

    def sendImg(self, peer, path):
        cmd = 'send_photo '+peer.replace(' ','_')+' '+ path +'\n'
        self.botProc.stdin.write(cmd.encode('utf-8'))
        self.botProc.stdin.flush()
        pass
    def sendFile(self, peer, path):
        cmd = 'send_file '+peer.replace(' ','_')+' '+ path +'\n'
        self.botProc.stdin.write(cmd.encode('utf-8'))
        self.botProc.stdin.flush()
        pass
    def sendVideo(self, peer, path):
        cmd = 'send_video '+peer.replace(' ','_')+' '+ path +'\n'
        self.botProc.stdin.write(cmd.encode('utf-8'))
        self.botProc.stdin.flush()
        pass
    def send_audio(self, peer, path):
        cmd = 'send_audio '+peer.replace(' ','_')+' '+ path +'\n'
        self.botProc.stdin.write(cmd.encode('utf-8'))
        self.botProc.stdin.flush()
        pass

    def command(self, message = None, msgType = 0, fromUser = None, fromGroup = None):
        pass

    def start(self):
        self.botThread = Thread(target = self.botCore)
        self.botThread.start()
        self.botThread.join()
