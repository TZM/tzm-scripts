#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from trello import TrelloClient
import os
import BeautifulSoup
import csv
import re
import mechanize
#import twill
#import twill.commands
#from urlparse import urlparse

from fish import ProgressFish

## get the default browser
br = mechanize.Browser()
ua = ('Mozilla/5.0 (X11; U; Linux i686)'
                'Gecko/20071127 Firefox/2.0.0.11')
br.addheaders = [('User-Agent', ua)]
#br.set_debug_http(True)
#br.set_debug_responses(True)
#t_com = twill.commands
#t_brw = t_com.get_browser()

#Trello authentication
auth = TrelloClient(os.environ['TRELLO_API_KEY'], os.environ['TRELLO_TOKEN'])
gca_board = auth.get_board('4f199b088ab038761f17b066')
gca_lists = gca_board.all_lists()

total_sites = None
chapters_to_check = []
chapters_with_web_sites = []
for gca_list in gca_lists:
    #print gca_list.id, gca_list.name
    # we get the 'Chapters to Check' list
    # with id '4f199b088ab038761f17b06b'
    if gca_list.id == '4f199b088ab038761f17b06b':
        # get the cards
        cards = gca_list.list_cards()
        total_sites = len(cards)
        for i, c in enumerate(cards):
            # do something with the description and try to extract the website address
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', c.description)
            
            if urls != []:
                chapter_data = {'name': c.name, 'urls': urls}
                chapters_with_web_sites.append(chapter_data)
            else:
                chapter_data = {'name': c.name, 'description': c.description}
                chapters_to_check.append(chapter_data)
            
    else:
        pass

sites_with_links_back = []
sites_with_no_links_back = []

fish = ProgressFish(total=len(chapters_with_web_sites))
for i, c in enumerate(chapters_with_web_sites):
    req = c['urls'][0]
    try:
        r = br.open(req)
        fish.animate(amount=i)
    except urllib2.HTTPError, e:
        print e.code
        continue
    c['urls'] = r.geturl()
    doc = r.read()
    soup = BeautifulSoup.BeautifulSoup(doc)
    try:
        href = soup.findAll('a', {'href': re.compile('thezeitgeistmovement.com')})
        if href:
            sites_with_links_back.append(c)
        else:
            sites_with_no_links_back.append(c)
    except:
        continue

    # see what the website is running
    
    # About section
    #try:
    #    about = soup.findAll('about')
# clrd detection requires a certain amount of string, sentances to determine language
print 'Currently we have to check %s ' % total_sites
print '=============='
print 'Number of sites with no link back is %s and are as follows:' % len(sites_with_no_links_back)
for site in sites_with_no_links_back:
    print site

print '=============='
print 'Number of sites with link back is %s and are as follows:' % len(sites_with_links_back)
for site in sites_with_links_back:
    print site
    
print 'Number of sites with no URL is %s and are as follows:' % len(chapters_to_check)
for site in chapters_to_check:
    print site
    
print 'Total sites checked %s' % (len(sites_with_no_links_back) + len(sites_with_links_back) + len(chapters_to_check))
