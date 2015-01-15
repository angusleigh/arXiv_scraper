"""
arXiv.py

This is a modification of the arXiv parser here:
http://arxiv.org/help/api/examples/python_arXiv_parsing_example.txt

I changed it to query the server to retrieve all abstracts from articles
of a given category. This does not retrieve the pdf's of the articles 
(arXiv does not like that, see: http://arxiv.org/help/robots).

I used it to create the dataset for our machine learning class's Kaggle competition: 
http://inclass.kaggle.com/c/abstract-classification

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
import os

# Parse input args
if len(sys.argv) != 3:
    print "Usage: python arXiv.py category max_results"
    print "Example: python arXiv.py stat 5000"
    print "Exiting"
    exit()
category = sys.argv[1]
max_total_results = int(sys.argv[2])

# Open csv file to write abstracts to
ofile  = open(os.path.dirname(__file__) + category + '.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL) 
writer.writerow(['category', 'abstract'])

# Base api query url
base_url = 'http://export.arxiv.org/api/query?'

# Search parameters
search_query = 'cat:'+category+'.*' 

# Opensearch metadata such as totalResults, startIndex, 
# and itemsPerPage live in the opensearch namespase.
# Some entry metadata lives in the arXiv namespace.
# This is a hack to expose both of these namespaces in
# feedparser v4.1
feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

# Iterating so query is broken down into multiple smaller queries
# with time delays in between so their server doesn't hang up on us
results_per_iter = 500
for i in xrange(0,max_total_results,results_per_iter):    
    # Search parameters
    start = i                     
    max_results = results_per_iter
    query = 'search_query=%s&start=%i&max_results=%i' % (search_query,start,max_results)

    # Repeat GET requests if there's a <Connection timed out> or some other kind of excpetion
    excepetion_count = 0
    successful_response = False
    while successful_response == False:
        try:
            # Perform a GET request using the base_url and query
            response = urllib.urlopen(base_url+query).read()
            successful_response = True
        except IOError:
            print 'IOError exception. Likely a connection time out. Trying again in 20s.'
            time.sleep(20)
            excepetion_count += 1
            if excepetion_count > 10:
                print 'Too many IOError exceptions. They have likely hung up for good. Stopping' 
                exit()

    # Parse the response using feedparser
    feed = feedparser.parse(response)
    
    # Print opensearch metadata
    if i == 0:
    	    print 'Total results for this query: %s' % feed.feed.opensearch_totalresults
    print 'Recieved: %d results so far' % (i+results_per_iter)

    # Run through each entry, and save the abstract and category to a csv file
    for entry in feed.entries:
        raw_abstract = entry.summary
        abstract = ' '.join(raw_abstract.splitlines())
        writer.writerow([category, abstract])
    
	print type(feed.feed.opensearch_itemsperpage)
	print feed.feed.opensearch_itemsperpage

    # Need additional stopping condition in case the results available < max_total_results
    if feed.feed.opensearch_itemsperpage < max_results:
        break
    
    # Time delay so we don't overload their server, causing them to hang up on us
    time.sleep(5)    

print 'Finished!'
ofile.close()