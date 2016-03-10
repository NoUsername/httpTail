#!/usr/bin/env python
from __future__ import print_function
import sys
import requests
import time
import argparse
import traceback

__author__ = "Paul Klingelhuber"
__copyright__ = "Copyright 2016, Paul Klingelhuber"
__license__ = "MIT"


DEBUG = True

class Config:
  def __init__(self):
    self.url = ''
    self.cookie = ''
    self.offset = 0
    self.session = None
    self.interval = 1
    self.startBytes = 1000

def dbg(info):
    if DEBUG:
        print(info)

def getSession(config):
    if config.session is None:
        config.session = requests.Session()
        cookies = dict()
        for part in config.cookie.split(';'):
            if not part:
                continue
            keyVal = part.split('=')
            cookies[keyVal[0]] = keyVal[1]
        requests.utils.add_dict_to_cookiejar(config.session.cookies, cookies)
    return config.session

def request(config):
    offset = config.offset
    if offset == 0:
        offset = -1 * config.startBytes
    else:
        offset = offset + 1
    s = getSession(config)
    offsetString = '%s'%offset
    if offset > 0:
        offsetString = offsetString + '-'
    dbg('offset: %s'%offsetString)
    return s.get(config.url, headers={'range': 'bytes=%s'%offsetString})

def parseRange(text):
    text = text.replace('bytes ', '')
    (responseRange, total) = text.split('/')
    if responseRange == '*':
        dbg('total: %s'%total)
        return (None, None, total)
    (start, end) = responseRange.split('-')
    dbg('start %s, end %s, total %s'%(start, end, total))
    return (start, end, total)

def checkNew(config):
    try:
        data = request(config)
    except:
        # some connection error
        if DEBUG:
            traceback.print_exc()
        return None
    if not 'Content-Range' in data.headers:
        print('unexpected error, headers: %s'%(data.headers))
        return None

    responseRange = data.headers['Content-Range']

    (start, end, total) = parseRange(responseRange)
    if end == None:
        # no new content
        return True

    config.offset = int(end)
    if data.text:
        print(data.text, end='')
        sys.stdout.flush()
    return True

def doStream(config):
    initialSuccess = checkNew(config)
    if not initialSuccess:
        print('initial request failed, please check settings')
        return
    fails = 0
    while True:
        success = checkNew(config)
        dbg('result %s, fails %s'%(success, fails))
        if success:
            fails = 0
        else:
            fails += 1
        if fails > 0 and fails % 5 == 0:
            print('\n[httpTail error] retrying...')
        time.sleep(config.interval)

def parseArgs():
    parser = argparse.ArgumentParser(description='Tail a streamable http text resource via continued get requests.')
    parser.add_argument('url', type=str)
    parser.add_argument('-c', '--cookie')
    parser.add_argument('-i', '--interval', type=int)
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()

if __name__=='__main__':
    args = parseArgs()
    conf = Config()
    conf.url = args.url
    conf.interval = args.interval or conf.interval
    conf.cookie = args.cookie or conf.cookie
    DEBUG = args.debug
    doStream(conf)
