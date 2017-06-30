#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import urllib
import urllib2
import cookielib
import json
from lxml.cssselect import CSSSelector
from lxml import html
import re
import pdb
import sys
import settings

reload(sys)
sys.setdefaultencoding('utf8')

chapterWords = []
exceptions = [line.rstrip().lower() for line in open('excepciones')]


def logIn(_lms_server, _cms_server, _user, _password):
    cj = cookielib.CookieJar()

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    response = opener.open(_lms_server + '/login')
    set_cookie = {}
    for cookie in cj:
        set_cookie[cookie.name] = cookie.value
    # Prepare Headers
    headers = {'User-Agent': 'edX-downloader/0.01',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
               'Referer': _lms_server,
               'X-Requested-With': 'XMLHttpRequest',
               'X-CSRFToken': set_cookie.get('csrftoken', '')}

    # Login
    post_data = urllib.urlencode({
                'email': _user,
                'password': _password,
                'remember': False
                }).encode('utf-8')
    request = urllib2.Request(_lms_server + '/user_api/v1/account/login_session/', post_data,headers)
    urllib2.urlopen(request)

    for cookie in cj:
        set_cookie[cookie.name] = cookie.value
    return set_cookie


def getCourseStructure(_cms_server, _set_cookie, _locator):
    '''
    connects to the studio server and returns the edx course structure
    to navigate afterwards
    '''
    url = _cms_server + '/course/' + _locator
    cookies = ""
    for key, value in _set_cookie.iteritems():
        cookies = cookies + key + ' = ' + value + ';'
    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        'X-CSRFToken': _set_cookie.get('csrftoken', ''),
        'content-type': "application/json; charset=UTF-8",
        'accept-encoding': "gzip, deflate",
        'Referer': _cms_server,
        'accept-language': "es,en;q=0.8,en-US;q=0.6",
        'cookie': cookies,
        'cache-control': "no-cache",
        }
    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)


def getVerticalChildrens(_cms_server,_set_cookie,_locator):
    '''
    connects to the studio server and get an array of the nodeids that are children of a vertical node
    vertical nodes need to be treated different since its childrens does not show in the course structure
    '''
    url = _cms_server + '/xblock/' + _locator + '/container_preview'

    cookies = ""
    for key, value in _set_cookie.iteritems():
        cookies = cookies + key + ' = ' + value + ';'
    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        'X-CSRFToken': _set_cookie.get('csrftoken', ''),
        'content-type': "application/json; charset=UTF-8",
        'accept-encoding': "gzip, deflate",
        'Referer': _cms_server,
        'accept-language': "es,en;q=0.8,en-US;q=0.6",
        'cookie': cookies,
        'cache-control': "no-cache",
        }
    response = requests.request("GET", url, headers=headers)
    result = response.text.decode('utf-8')
    verticalHtml = html.fromstring(json.loads(result)['html'])
    blockCSS = CSSSelector('li.studio-xblock-wrapper')
    blocks = blockCSS(verticalHtml)
    blockIds = []
    for block in blocks:
        blockIds.append(block.attrib['data-locator'])
    return blockIds


def getNodeData(_cms_server, _set_cookie, _locator):
    '''
    takes the data of a xblock node
    '''
    url = _cms_server +'/xblock/' + _locator
    payload = ''
    cookies=""
    for key,value in _set_cookie.iteritems():
        cookies = cookies + key + ' = ' + value + ';'
    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        'X-CSRFToken': _set_cookie.get('csrftoken', ''),
        'content-type': "application/json; charset=UTF-8",
        'accept-encoding': "gzip, deflate",
        'Referer': _cms_server,
        'accept-language': "es,en;q=0.8,en-US;q=0.6",
        'cookie': cookies,
        'cache-control': "no-cache",
        }
    response = requests.request("GET", url, headers=headers)
    return json.loads(response._content)

def getVideoTranscription(_cms_server, _set_cookie, _locator,_videoId,_language):
    '''
    takes the data of a xblock node
    '''
    url = _cms_server + 'preview/xblock/' + _locator + '/handler/transcript/translation/' + _language + '?videoId=' + _videoId
    payload = ''
    cookies = ""
    for key,value in _set_cookie.iteritems():
        cookies = cookies + key + ' = ' + value + ';'
    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        'X-CSRFToken': _set_cookie.get('csrftoken', ''),
        'content-type': "application/json; charset=UTF-8",
        'accept-encoding': "gzip, deflate",
        'Referer': _cms_server,
        'accept-language': "es,en;q=0.8,en-US;q=0.6",
        'cookie': cookies,
        'cache-control': "no-cache",
        }
    response = requests.request("GET", url, headers=headers)
    return response._content


def disociate_words(parsedtext):
    global chapterWords
    if parsedtext:
        # let split and remove some stuff
        mapping = {',': '', ';': '', '.': '', ':': '', '(': '', ')': '', '!': '', '¡': '', '?': '', '¿': '', '-': '', '"': ''}
        parsedword = re.split(' |\/', parsedtext)
        for word in parsedword:
            # let clean the words
            if word != u'':
                for k, v in mapping.iteritems():
                    word = word.replace(k, v).lower().encode('utf-8')
                if word not in chapterWords:
                    chapterWords.append(word)
                    if len(word)>1:
                        with open(settings.FILENAME, 'a') as file:
                            file.write(u'<li>' + word.encode('utf-8') + u'</li>\n')


def generate_glosary(cmsServerSource, cookiesSource, nodeSource, courseLocator):
    '''
    Copys a node from one server as a child of another node in another server
    :param cmsServerSource:
    :param cookiesSource:
    :param cmsServerTarget:
    :param cookiesTarget:
    :param nodeTarget:
    :param nodeSource:
    :return:
    '''
    global chapterWords
    if 'category' not in nodeSource:
        return -1
    if 'category' in nodeSource and nodeSource['category'] == 'chapter':
        chapterWords = exceptions
        href = 'https://courses.edx.org/courses/' + courseLocator + '/course/#' + nodeSource['id']
        with open(settings.FILENAME, 'a') as file:
            file.write('<h1><a href="' + href + '">' + nodeSource['display_name'] + '</a>\n')
            file.write('<ul>\n')
    if 'display_name' in nodeSource:
        disociate_words(nodeSource['display_name'])
    if 'child_info' in nodeSource:
        for children in nodeSource['child_info']['children']:
            generate_glosary(cmsServerSource, cookiesSource, children, courseLocator)
    elif nodeSource['category'] == 'vertical':
        blocks = getVerticalChildrens(cmsServerSource, cookiesSource, nodeSource['id'])
        for block in blocks:
            nodeData = getNodeData(cmsServerSource, cookiesSource, block)
            generate_glosary(cmsServerSource, cookiesSource, nodeData, courseLocator)
    if 'data' in nodeSource:
        if nodeSource['category'] == 'video':
            transcription = getVideoTranscription(cmsServerSource, cookiesSource, nodeSource['id'],nodeSource['metadata']['youtube_id_1_0'],'es')
            if transcription != u'':
                transcriptionText = json.loads(transcription)['text']
                for line in transcriptionText:
                    disociate_words(line)
        if nodeSource['category'] == 'problem':
            #enunciado de problema $("h4>b") $("problem>b") $("problem b")
            #opciones en dropdown $("optioninput>option")
            #$("multiplechoiceresponse") el texto dentro del tag parece ser todo en español
            #$("td p")
            #$("optionresponse")
            #blockCSS = CSSSelector('li.studio-xblock-wrapper')
            #blocks = blockCSS(verticalHtml)
            #pdb.set_trace()
            htmlData = html.fromstring(nodeSource['data'])
            parseCSSs = ['problem b', 'optioninput>option', 'multiplechoiceresponse', 'td p', 'optionresponse']
            for selector in parseCSSs:
                blockSelector = CSSSelector(selector)
                blockhtml = blockSelector(htmlData)
                for block in blockhtml:
                    disociate_words(block.text)
            '''
            enunciadoSelector = CSSSelector('problem b')
            enunciado = enunciadoSelector(htmlData)
            for block in enunciado:
                disociate_words(block.text)
            optionSelector = CSSSelector("optioninput>option")
            options = optionSelector(htmlData)
            for block in options:
                disociate_words(block.text)
            multiplechoiceSelector = CSSSelector("multiplechoiceresponse")
            multiplechoice = multiplechoiceSelector(htmlData)
            for block in multiplechoice:
                disociate_words(block.text)
            tdpSelector = CSSSelector("td p")
            tdp = tdpSelector(htmlData)
            for block in tdp:
                disociate_words(block.text)
            optionresponseSelector = CSSSelector("optionresponse")
            optionresponse = optionresponseSelector(htmlData)
            for block in optionresponse:
                disociate_words(block.text)
            '''
        if nodeSource['category'] == 'html':
            # right now we dont parse html objects
            pass
    if nodeSource['category'] == 'chapter':
        # once we get out of the recursion we close the unordered list
        with open(settings.FILENAME, 'a') as file:
            file.write('</ul>\n')

with open(settings.FILENAME, 'wb') as file:
    file.write('')

cookies = logIn(settings.LMSURL, settings.CMSURL, settings.USERNAME, settings.PASSWORD)

courseStructure = getCourseStructure(settings.CMSURL, cookies, settings.COURSELOCATOR)
generate_glosary(settings.CMSURL, cookies, courseStructure, settings.COURSELOCATOR)
