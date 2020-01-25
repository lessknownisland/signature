#!/usr/bin/env python
#-_- coding:utf-8 -_-
#Author: Arno
#Introduction:
#    调用telegram API，发送信息

import requests, sys, os
import datetime, json, logging, re
from detect.models      import TelegramUserIdTb, TelegramChatGroupTb
from signature             import settings
from control.middleware import config

logger = logging.getLogger('django')

# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#获取当前脚本路径
basedir = os.path.abspath(os.path.dirname(__file__))

#获取当前时间，以特定的格式，如Wed, 09 May 2018 12:51:25 GMT
def getDate():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

#telegram 通知

class SendTelegram(object):
    def __init__(self, message):
        '''
            参数初始化:message
        {
            bot：       机器人的username
            group：     聊天组名称[默认arno_test]
            doc：       是否是以文件形式发送[True|False，默认False]
            doc_name：  文件名称[默认warning.txt]
            timeout：   发送超时时间[默认15s]
            parse_mode：信息文本模式[HTML|Markdown，默认无格式]
            caption：   对文件的注释
            text：      信息文本内容
            disable_web_page_preview：是否关闭预览[True|False，默认True]
        }
        '''
        tg         = config.TELEGRAM_API
        bot        = message['bot']     if 'bot' in message else ''
        doc        = message['doc']     if 'doc' in message else False
        group      = message['group']   if 'group'   in message else ''
        timeout    = message['timeout'] if 'timeout' in message and isinstance(message['timeout'], int) else 15

        self.__message = {}
        self.__doc     = doc
        self.__timeout = timeout
        self.__verify  = False
        self.__url     = tg['url'][bot] if bot in tg['url'] else tg['url']['sa_monitor_bot']
        self.__message['parse_mode'] = message['parse_mode'] if 'parse_mode' in message else ''
        self.__message['doc_name']   = f"{settings.BASE_DIR}/tmp/{getDate()}_{message['doc_name']}" if 'doc_name' in message else getDate()+'_message.txt'
        self.__message['caption']    = self.get_at_users(message['caption']) if 'caption'  in message  else ''
        self.__message['text']       = self.get_at_users(message['text'])    if 'text'     in message else ''
        self.__message['disable_web_page_preview'] = False if 'disable_web_page_preview' in message and str(message['disable_web_page_preview']).lower() == 'false' else True

        try: 
            self.__message['chat_id'] = TelegramChatGroupTb.objects.get(group=group).group_id 
        except: 
            self.__message['chat_id'] = TelegramChatGroupTb.objects.get(group="arno_test").group_id 

    def get_at_users(self, text):
        regCp  = re.compile('[A-Za-z0-9]+(?![A-Za-z0-9])', re.I)
        user_l = [ {'user': '@'+regCp.match(user).group(),
                    'name': regCp.match(user.lower()).group()} for user in text.split('@')[1:] if regCp.match(user.lower())]

        #if self.__message['parse_mode'] == 'HTML':
        #    text = text.replace("<", "&lt;").replace(">", "&gt;")

        if user_l:
            user_id_l = {}
            s = TelegramUserIdTb.objects.all()
            for i in s:
                user_id_l[i.user] = {}
                user_id_l[i.user]['name']    = i.name
                user_id_l[i.user]['user_id'] = i.user_id

            for user in user_l:
                if user['name'] in user_id_l:
                    if self.__message['parse_mode'] == 'HTML':
                        atUser = "<a href='tg://user?id=%s'>%s</a>" %(user_id_l[user['name']]['user_id'], user_id_l[user['name']]['name'])
                        text = text.replace(user['user'], atUser)
                    elif self.__message['parse_mode'] == 'Markdown':
                        atUser = "[%s](tg://user?id=%s)" %(user_id_l[user['name']]['name'], user_id_l[user['name']]['user_id'])
                        text = text.replace(user['user'], atUser)

        #logger.info(text)
        return text

    def send(self):
        self.__message['text'] = self.__message['text']
        #logger.info(self.__message['text'])
        #logger.info(type(self.__message['text']))
        try:
            if (not self.__doc) or str(self.__doc).lower() == 'false':
                ret = requests.post(self.__url+'sendMessage', data=self.__message, timeout=self.__timeout, verify=self.__verify)
            else:
                with open(self.__message['doc_name'], 'w') as f:
                    for line in self.__message['text'].split('\n'):
                        f.writelines(line+'\r\n')
                self.__files = {'document': open(self.__message['doc_name'], 'rb')}
                ret = requests.post(self.__url+'sendDocument', data=self.__message, files=self.__files, timeout=self.__timeout, verify=self.__verify)
                
        except Exception as e:
            logger.error('Attention: send message failed!')
            logger.error(e)
            return False
        else:
            if ret.status_code == 200:
                logger.info('send message successfull!')
                return True
            else:
                logger.error('Attention: send message failed!')
                logger.error('%s: %s' %(ret.status_code, ret.content))
                logger.error(self.__message)
                return False

    def send_photo(self, photo):
        '''
            发送图片
        '''
        if not photo: return False
        self.__message['text']    = self.__message['text']
        self.__message['caption'] = self.__message['text']
        files = {'photo': photo}
        try:
            ret = requests.post(self.__url+'sendPhoto', data=self.__message, files=files, timeout=self.__timeout, verify=self.__verify)
                
        except Exception as e:
            logger.error('Attention: send photo failed!')
            logger.error(e)
            return False
        else:
            if ret.status_code == 200:
                logger.info('send photo successfull!')
                return True
            else:
                logger.error('Attention: send photo failed!')
                logger.error('%s: %s' %(ret.status_code, ret.content))
                logger.error(self.__message)
                return False

    def send_document(self, file):
        '''
            发送文件
        '''
        if not file: return False
        self.__message['text'] = self.__message['text']
        self.__message['caption'] = self.__message['text']
        files = {'document': file}
        try:
            ret = requests.post(self.__url+'sendDocument', data=self.__message, files=files, timeout=self.__timeout, verify=self.__verify)
                
        except Exception as e:
            logger.error('Attention: send file failed!')
            logger.error(e)
            return False
        else:
            if ret.status_code == 200:
                logger.info('send file successfull!')
                return True
            else:
                logger.error('Attention: send file failed!')
                logger.error('%s: %s' %(ret.status_code, ret.content))
                logger.error(self.__message)
                return False