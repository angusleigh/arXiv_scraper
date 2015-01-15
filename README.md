arxiv_scraper
==============

This is a modification of the arXiv parser here:
http://arxiv.org/help/api/examples/python_arXiv_parsing_example.txt

I changed it to query the server to retrieve all abstracts from articles
of a given category. This does not retrieve the pdf's of the articles 
(arXiv does not like that, see: http://arxiv.org/help/robots).

I used it to create the dataset for our machine learning class's Kaggle competition: 
http://inclass.kaggle.com/c/abstract-classification

This is free software.  Feel free to do what you want
with it, but please play nice with the arXiv API!

# Usage:
- python arXiv.py category max_results

# Example:
- python arXiv.py stat 5000

