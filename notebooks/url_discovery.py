from __future__ import annotations
import abc
from rank_pair_tree import RankPairTree
from py_utils import nullPipe
from os import path
import io
import os
from collections import defaultdict
from collections.abc import Sequence
from enum import Enum, IntEnum
from typing import Literal
import debugpy as debug
import warnings
from pprint import pprint
import re
from uint import Uint, Int
import requests
import numpy as np
import matplotlib.pyplot as plt
import atexit
from datetime import datetime
from file_appender import IFileAppender, DummyFileAppender, FileAppender

import logging

from bs4 import BeautifulSoup, SoupStrainer, Tag, NavigableString, ResultSet
from selenium.webdriver import Safari
from selenium.webdriver.common.by import By





# driver.find_element(By.XPATH, '//button[text()="Some text"]')
# ID = "id"
# XPATH = "xpath"
# LINK_TEXT = "link text"
# PARTIAL_LINK_TEXT = "partial link text"
# NAME = "name"
# TAG_NAME = "tag name"
# CLASS_NAME = "class name"
# CSS_SELECTOR = "css selector"

# https://pythex.org/?regex=%5E(%3F%3A(%3FP%3Cprotocol%3Ehttp%5Bs%5D%3F%7Cftp)%3A%5C%2F)%3F%5C%2F%3F(%3FP%3Cdomain%3E%5B%5E%3A%5C%2F%5Cs%5D%2B)(%3F%3A(%3FP%3Cpath%3E(%3F%3A(%3F%3A%5C%2F%5Cw%2B)*)(%3F%3A%5C%2F%5B%5Cw%5C-%5C.%5D%2B%5B%5E%23%3F%5Cs%5D%2B))(%3FP%3Cquery%3E.*)(%3FP%3Cid%3E%23%5B%5Cw%5C-%5D%2B)%3F)%3F%24&test_string=https%3A%2F%2Fassets.adobedtm.com&ignorecase=0&multiline=0&dotall=0&verbose=0
URL_RE_PATTERN = r'^(?:(?P<protocol>http[s]?|ftp):\/)?\/?(?P<domain>[^:\/\s]+)(?:(?P<path>(?:(?:\/\w+)*)(?:\/[\w\-\.]+[^#?\s]+))(?P<query>.*)(?P<id>#[\w\-]+)?)?$'

def _urlDiscoverySelenium(rootUrl:str, driver:Safari):
    driver.get(rootUrl)
    find_and_agree_cookies(driver)
    anchorTagUrls = [we.get_attribute('href') for we in driver.find_elements(By.TAG_NAME, 'a')]
    scriptTagUrlEmbeds = [nullPipe(re.match(URL_RE_PATTERN, str(we.text)),lambda x: x.string) for we in driver.find_elements(By.TAG_NAME, 'script')] 
    onClickAttributeUrlEmbeds = [nullPipe(re.match(URL_RE_PATTERN, we.get_attribute('onClick')), lambda x: x.string) for we in driver.find_elements(By.CSS_SELECTOR, '[onClick]') if we.get_attribute('onClick')] 
    # Button urls should be included in the onClick handler above.
    # buttonTagUrls = [we for we in driver.find_elements(By.TAG_NAME, 'button')]

    # urlPioneer = anchorTagUrls + scriptTagUrlEmbeds + onClickAttributeUrlEmbeds
    urlProps = UrlProps(anchorTagUrls, scriptTagUrlEmbeds + onClickAttributeUrlEmbeds)
    return urlProps
    return urlPioneer

def _urlDiscoveryBs4(rootUrl:str):
    
    # http://www.xhaus.com/headers -> View your headers in browser
    headers = {"User-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43'}
    if rootUrl.startswith('file:///'):
        with open(re.sub(r'^file:\/\/\/', '/', rootUrl), 'r') as f:
            pageContents = f.read()
    else:
        pageContents = requests.get(rootUrl, headers=headers).content
    # print(page.content)
    soup = BeautifulSoup(pageContents, 'html.parser')
    
    anchorTagUrls = [we.get('href') for we in soup.find_all('a')]
    scriptTagUrlEmbeds = [nullPipe(re.match(URL_RE_PATTERN, str(nullPipe(we.string, lambda y: y, returnIfnull=None))),lambda x: x.string) for we in soup.find_all('script')] 
    onClickAttributeUrlEmbeds = [nullPipe(re.match(URL_RE_PATTERN, we.get('onClick')), lambda x: x.string) for we in soup.find_all(onClick=True) if we.get('onClick')] 
    # Button urls should be included in the onClick handler above.
    # buttonTagUrls = [we for we in driver.find_elements(By.TAG_NAME, 'button')]

    # urlPioneer = anchorTagUrls + scriptTagUrlEmbeds + onClickAttributeUrlEmbeds
    urlProps = UrlProps(anchorTagUrls, scriptTagUrlEmbeds + onClickAttributeUrlEmbeds)
    return urlProps

def urlDiscovery(rootUrl:str, driver:Safari=None, useSelenium:bool=False,requiredSubDomain:str=None):
    driverType = 'selenium' if useSelenium else 'bs4'
    logging.info(f'urlDiscovery[{driverType}]: {rootUrl}')
    if useSelenium and driver is not None:
        result = _urlDiscoverySelenium(rootUrl=rootUrl, driver=driver)
    else:
        result = _urlDiscoveryBs4(rootUrl)
    
    def _removeEmptyUrls(result:list[str]):
        return [url for url in result if url is not None and (requiredSubDomain in url or requiredSubDomain is None)]
    
    return UrlProps(
        anchorTagHrefs=_removeEmptyUrls(result.anchorTagHrefs),
        embeddedScriptAndAnchorTagHrefs=_removeEmptyUrls(result.embeddedScriptAndAnchorTagHrefs)
    )

def nth_of_type(elem:Tag):
    count, curr = 0, 0
    for i, e in enumerate(elem.find_parent().find_all(recursive=False), 1):
        if e.name == elem.name:
            count += 1
        if e == elem:
            curr = i
    return '' if count == 1 else ':nth-child({})'.format(curr)

def _getElemSelector(elem:Tag):
    selector = elem.name
    # otherAttrs = set(elem.attrs.keys()).difference('class')
    if elem['class']:
        selector += '.' + '.'.join(elem['class'])

    for otherAtr in elem.attrs.keys():
        if isinstance(elem[otherAtr], list) and otherAtr == 'class':
            pass
        else:
            selector += f'[{otherAtr}="{elem[otherAtr]}"]'
    
    if str(elem.string) and not elem.children:
        selector += f':contains("{elem.text}")'
    
    return selector# + nth_of_type(elem)

def getCssPath(elem, maxTreeSize = 100):
    if elem.attrs.get('id'):
        return '#' + elem.attrs['id']

    rv = [_getElemSelector(elem)]
    _i = 0
    while _i < maxTreeSize:
        _i += 1
        elem = elem.find_parent()
        if not elem or elem.name == '[document]':
            return '>'.join(rv[::-1])
        elif _i >= maxTreeSize:
            return ' ... ' + ' > '.join(rv[::-1])
        elif elem.attrs.get('id'):
            return '#' + elem.attrs['id'] + ' > '.join(rv[::-1])
            
        rv.append(_getElemSelector(elem))
def seleniumTryClickWebEl(wElem):
    clickSuccess = False
    try:
        wElem.click()
        clickSuccess = True
    except Exception as e:
        clickSuccess = False

    return clickSuccess

def selenium_click_css(cssSelector, driver):
    success = False
    webEl = driver.find_element_by_css_selector(cssSelector)
    if webEl:
        if webEl.is_displayed():
            if seleniumTryClickWebEl(webEl):
                driver.execute_script(f'document.querySelector(\'{cssSelector}\').click()')
                success = True
    return success

def selenium_click_webEl(webEl, driver):
    success = False
    if webEl.is_displayed():
        if seleniumTryClickWebEl(webEl):
            if webEl.has_attribute('id'):
                _id = webEl.get_attribute('id')
                driver.execute_script(f'document.getElementById(\'{_id}\').click()')
            else:
                cssSelector = getCssPath(webEl)
                selenium_click_css(cssSelector)
            success = True

    return success

def find_and_agree_cookies(driver:Safari):
    _f = lambda btnText: f"//*[text()='{btnText}']"
    agreebtns = driver.find_elements_by_xpath(_f('I agree'))
    btn_ids= None
    if agreebtns:
        btn_ids = [agreebtn.get_attribute('id') for agreebtn in agreebtns]
    if not btn_ids:
        agreebtns = driver.find_elements_by_xpath(_f('Allow All'))
        if agreebtns:
            btn_ids = [agreebtn.get_attribute('id') for agreebtn in agreebtns]
        else:
            btn_ids = []

    if btn_ids:
        for btn_id in btn_ids:
            btn = driver.find_element_by_id(btn_id)
            if btn.is_displayed():
                if seleniumTryClickWebEl(btn):
                    # driver.execute_script(f'$(\'#{btn_id}\').click()')
                    driver.execute_script(f'document.getElementById(\'{btn_id}\').click()')


class CanUseBs4(Enum):
    No = -1
    Unknown = 0
    Yes = 1


class UrlProps():
    def __init__(self, anchorTagHrefs:list[str]=[], embeddedScriptAndAnchorTagHrefs:list[str]=[]) -> None:
        self.canUseBs4:CanUseBs4 = CanUseBs4.Unknown
        self.anchorTagHrefs = anchorTagHrefs
        self.embeddedScriptAndAnchorTagHrefs = embeddedScriptAndAnchorTagHrefs

    def getNumAnchorTags(self):
        return len(self.anchorTagHrefs)
    def getNumHrefsInScriptsAndButtons(self):
        return len(self.embeddedScriptAndAnchorTagHrefs)
    numAnchorTags = property(getNumAnchorTags)
    numHrefsInScriptsAndButtons = property(getNumHrefsInScriptsAndButtons)



maxSpiderExplodeAllowed:Literal = 3
defaultSpiderExplodeDepth:Literal = 3

def run_url_discovery_ASDA():
    return _run_url_discovery('https://groceries.asda.com', 'asda.com', 3, 'ASDA')
    

def _run_url_discovery(domain, subDomainReq, explodeTimes:Uint=defaultSpiderExplodeDepth, saveOut:str=None):
    
    driver:Safari = None
    if useSelenium:
        driver = Safari()
        driver.implicitly_wait(10)
        
    if maxSpiderExplodeAllowed < explodeTimes:
        warnings.warn(f'Warning: Max allowed Spider Explode to depth of: {maxSpiderExplodeAllowed}')
    fileToClose = False    
    saveFileWrap:IFileAppender
    if saveOut is not None:
        fileToClose = True
        saveFileWrap = FileAppender(saveOut).openStream()
    else:
        saveFileWrap = DummyFileAppender('Dummy').openStream()
        
        

    try:   
        urlsToSearch = [domain]
        newurls = []
        urlPioneer = []
        _i = 0
        urlTree:RankPairTree = RankPairTree()
        urlDict = {}
        # TODO: Catch popup windows and then close them. By checking for windows wptjer than the active window.
        while _i < max(1,min(defaultSpiderExplodeDepth,explodeTimes)):
            _i += 1
            newurls:list[str] = []
            for url in urlsToSearch:
                _useSeleniumForThisUrl = useSelenium
                exampleUrl = urlTree.getExampleGeneralisationOf(url, removeRegexNodes=True)
                if exampleUrl is not None:
                    _useSeleniumForThisUrl = False
                    expectedHtmlProps = urlDict[exampleUrl]
                urlTree.embedUrl(url)
                urlProps = urlDiscovery(url, driver, useSelenium=_useSeleniumForThisUrl, requiredSubDomain=subDomainReq)
                urlDict[url] = urlProps
                newurls += urlProps.anchorTagHrefs + urlProps.embeddedScriptAndAnchorTagHrefs
                saveFileWrap.write(f'{url}\n-\t' + '\n-\t'.join(newurls))
            urlsToSearch = [url for url in set(newurls) if url not in urlPioneer]
            if maxSubUrls > -1:
                urlsToSearch = urlsToSearch[:maxSubUrls]
            urlPioneer += urlsToSearch
            
            # for url in urlPioneer:
            #     _i += 1
            #     urlProps = urlDiscovery(url, driver, useSelenium=False, requiredSubDomain=subDomainReq)
            #     urlPioneer = urlPioneer + urlProps.anchorTagHrefs + urlProps.embeddedScriptAndAnchorTagHrefs 
            #     if _i > maxSubUrls > -1:
            #         break


        return urlPioneer
    except:
        if fileToClose != False:
            saveFileWrap.closeStream()
        
        return None


# def save_url_discovery_output(name:str, urlDiscoveryOut:list[str]): 
#     with open(f'../data/url_pioneer_{name}.txt', 'a+') as f:
#         for l in urlDiscoveryOut:
#             f.write(l)



maxSubUrls = 10
useSelenium = True
if __name__ == '__main__':

    logging.basicConfig(filename ='app.log',
                        level = logging.INFO)

    # Example logging calls (insert into your program)
    # logging.critical('Host %s unknown', hostname)
    # logging.error("Couldn't find %r", item)
    # logging.warning('Feature is deprecated')
    # logging.info('Opening file %r, mode = %r', filename, mode)
    # logging.debug('Got here')
    
    urlDiscovery = _run_url_discovery('https://groceries.asda.com', 'asda.com', explodeTimes = 2, saveOut='ASDA')
    
    

