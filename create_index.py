#!/usr/bin/env python3

from bs4 import BeautifulSoup
from collections import defaultdict
import sys, codecs
import os
from trie import Trie

search_index = defaultdict(set)
with open(os.path.join(os.path.dirname(__file__), 'stopwords.txt'), 'r') as f:
    stop_words = set(f.read().split())

def filter_char(char):
    return ord('a') <= ord(char) <= ord('z') or char == '.' or char == '_'

def token_filter(token):
    token = token.lower()
    token = ''.join(i for i in token if filter_char(i))

    if token in stop_words:
        return None

    if not token:
        return None

    return token


def parse_file(filename):
    with open(filename, 'r') as f:
        data = f.read()

    soup = BeautifulSoup(data, 'lxml')
    main_content = soup.find('div', {'class': 'col-md-8'})
    anchors = main_content.find_all(lambda tag: tag.has_attr('id'))
    for anchor in anchors:
        anchor_id = anchor.attrs['id']
        all_text = ''.join(anchor.findAll(text=True))
        tokens = all_text.split()
        for token in tokens:
            filtered = token_filter(token)
            if filtered is None:
                continue
            filtered = filtered.replace('.', '}')
            filtered = filtered.replace('_', '|')
            search_index[filtered].add(anchor_id.strip())

if __name__=='__main__':
    for root, dirs, files in os.walk(sys.argv[1]):
        for file in files:
            if file.endswith(".html"):
                print("parsing", os.path.join(root, file)) 
                parse_file(os.path.join(root, file))

    trie = Trie()
    for key in sorted(search_index):
        trie.insert(key)

    print ("dumping")
    trie.to_file('dumped.trie')

    print ("Done, trie dumped in dumped.trie!")
