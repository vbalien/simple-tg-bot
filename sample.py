#!/usr/bin/python
# -*- coding: utf-8 -*-
import shlex, datetime
from tgbot import TGBot

import json
import http.client
# day : 0 = sunday,1 = monday, ...
def getAniList(day):
    result = ''
    conn = http.client.HTTPConnection('www.anissia.net')
    conn.request('GET', '/anitime/list?w='+str(day))
    r = conn.getresponse()
    data = r.read()
    data = data.decode('utf-8')
    data = json.loads(data)
    for i in data:
        result += i['t'][:2] + ':' + i['t'][2:] + ' ' + i['s'] + '\n'
    return result
    
class myTGBot(TGBot):
    __autoread__ = False
    is_sleep = False
    is_listen = False
    def command(self, message = '', msgType = 0, fromUser = None, fromGroup = None):
        #: Get peer
        peer = fromGroup is None and fromUser or fromGroup
        #: Split message
        args = shlex.split(message)
        
        #: Listen mode
        if(args[0] == '짓쨩' and not self.is_listen):
            if(len(args) == 1):
                if(not self.is_sleep):
                    self.sendMsg(peer, '네?')
                self.is_listen = True
                return
            else:
                args.pop(0)
        elif(args[0] != '짓쨩' and not self.is_listen):
            return
        self.is_listen = False
        
        #: owner check
        if(fromUser != 'Jisu Kim'):
            self.sendMsg(peer, '짓쨩은 주인님명령만 따릅니다.')
            return
        
        #: sleep mode
        if(not self.is_sleep and args[0] in ['자라', '자', '잘자']):
            self.sendMsg(peer, '주인님, 안녕히주무세요.')
            self.is_sleep = True
        if(self.is_sleep and args[0] in ['일어나', '좋은아침', '오하요']):
            self.sendMsg(peer, '주인님, 안녕히주무셧어요?')
            self.is_sleep = False
        if(self.is_sleep):
            return
        
        # basic commend 1
        if(args[0] in ['뭐해', '뭐해?', '뭐함', 'ㅁㅎ', 'ㅁㅎ?']):
            self.sendMsg(peer, '일해요.')
        
        # basic commend 2
        if(args[0] in ['고마워', '귀여워', '커여워', '이쁘다']):
            self.sendMsg(peer, '데헷 //ㅅ//')
        
        # get Animation List
        if(args[-1] in ['애니목록', '애니'] or args[0][-2:] == '애니' or args[0][-4:] == '애니목록'):
            daynum = datetime.datetime.today().weekday() + 1
            if(args[0][-2:] == '애니' or args[0][-4:] == '애니목록'):
                args[0] = args[0].replace('애니', '')
                args[0] = args[0].replace('목록', '')
            days = {'일요일' : 0, '월요일' : 1, '화요일' : 2, '수요일' : 3, '목요일' : 4, '금요일' : 5, '토요일' : 6,
                '그제' : (daynum - 2)%7, '어제' : (daynum - 1)%7, '오늘' : daynum,
                '내일' : (daynum + 1)%7, '모레' : (daynum + 2)%7,'글피' : (daynum + 3)%7}
            if(args[0] in days):
                msg = args[0]+' 애니입니다.\n--------------------------------\n'
                msg += getAniList(days[args[0]])
                self.sendMsg(peer, msg)
        pass
    
if __name__ == "__main__":
    bot = myTGBot()
    bot.start()
