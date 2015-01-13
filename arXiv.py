"""
arXiv_scraper.py

This is a modification of the arXiv here:
http://arxiv.org/help/api/user-manual#python_simple_example

I changed it to query the server to retrive all abstracts from articles
of a given category. 

Command line usage is: arXiv.py category max_results
Example: arXiv.py stat 5000

This is free software.  Feel free to do what you want
with it, but please play nice with the arXiv API!
"""

import sys
import time
import urllib
import feedparser
import csv

# Parse input args
if len(sys.argv) != 3:
    print "Usage: arXiv.py category max_results"
    print "Example: arXiv.py stat 5000"
    print "Exiting"
    exit()
category = sys.argv[1]
max_total_results = int(sys.argv[2])

# Open csv file to write abstracts to
ofile  = open('/home/angus/python_workspace/arXiv_scraper/csv/' + category + '.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL) 
writer.writerow(['category', 'abstract'])

# Base api query url
base_url = 'http://export.arxiv.org/api/query?';

# Search parameters
search_query = 'cat:' + category + '.*' # search for electron in all fields

# Iterating so query is broken down into multiple smaller queries
# with time delays in between so their server doesn't hang up on us
results_per_iter = 500
reached_end = False
for i in xrange(0, max_total_results, results_per_iter): 
    if reached_end:
        break

    # Search parameters
    start = i                     
    max_results = results_per_iter
    query = 'search_query=%s&start=%i&max_results=%i' % (search_query,start,max_results)

    # Opensearch metadata such as totalResults, startIndex, 
    # and itemsPerPage live in the opensearch namespase.
    # Some entry metadata lives in the arXiv namespace.
    # This is a hack to expose both of these namespaces in
    # feedparser v4.1
    feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

    # Repeat GET requests if there's a <Connection timed out> excpetion
    excepetion_count = 0
    while True:
        try:
            # Perform a GET request using the base_url and query
            response = urllib.urlopen(base_url+query).read()
            break
        except IOError:
            print 'IOError exception. Trying again.'
            time.sleep(20)
            excepetion_count += 1
            if excepetion_count > 10:
                break
    if excepetion_count > 10:
        print 'Too many IOError exceptions. They have likely hung up. Stopping' 
        break

    # Parse the response using feedparser
    feed = feedparser.parse(response)

    # Print out feed information
    print 'Feed title: %s' % feed.feed.title
    print 'Feed last updated: %s' % feed.feed.updated

    # Print opensearch metadata
    print 'totalResults for this query: %s' % feed.feed.opensearch_totalresults
    print 'itemsPerPage for this query: %s' % feed.feed.opensearch_itemsperpage
    print 'startIndex for this query: %s'   % feed.feed.opensearch_startindex

    # Run through each entry, and save the abstract and category to a csv file
    for entry in feed.entries:
        raw_abstract = entry.summary
        abstract = ' '.join(raw_abstract.splitlines())
        writer.writerow([category, abstract])
    
    # Time delay so we don't overload their server, causing them to hang up on us
    time.sleep(5)

    # Stopping condition
    if feed.feed.opensearch_itemsperpage < max_results:
        reached_end = true

print 'Finished successfully!'
ofile.close()