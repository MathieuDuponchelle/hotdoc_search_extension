#!/usr/bin/env python3

from bs4 import BeautifulSoup
from collections import defaultdict
import sys, codecs
import os, json
from trie import Trie
import shutil

here = os.path.dirname(__file__)

search_index = defaultdict(set)
with open(os.path.join(here, 'stopwords.txt'), 'r') as f:
    stop_words = set(f.read().split())

def filter_char(char):
    return ord('a') <= ord(char) <= ord('z') or char == '.' or char == '_'

def token_filter(token):
    token = token.lower()
    token = ''.join(i for i in token if filter_char(i))

    if token in stop_words:
        return None

    token = token.strip('._')

    if not token:
        return None

    return token


def parse_file(root_dir, filename):
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
            url = filename + '#' + anchor_id.strip()
            url = os.path.relpath(url, root_dir)
            search_index[filtered].add(url)

def prepare_output_folder(root_dir):
    searchdir = os.path.join(root_dir, 'search')

    try:
        shutil.rmtree (searchdir)
    except OSError as e:
        pass

    try:
        os.mkdir (searchdir)
    except OSError:
        pass

if __name__=='__main__':
    root_dir = sys.argv[1]
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                print("parsing", os.path.join(root, file)) 
                parse_file(root_dir, os.path.join(root, file))

    prepare_output_folder(root_dir)

    trie = Trie()
    for key, value in sorted(search_index.items()):
        trie.insert(key)

        key = key.replace('}', '.')
        key = key.replace('|', '_')
        metadata = {'urls': list(value)}
        with open (os.path.join(root_dir, 'search', key), 'w') as f:
            f.write(json.dumps(metadata))

    print ("dumping")
    trie.to_file(os.path.join(root_dir, 'search', 'dumped.trie'))

    shutil.copy(os.path.join(here, 'trie.js'),
            os.path.join(root_dir, 'search', 'trie.js'))

    shutil.copy(os.path.join(here, 'search.js'),
            os.path.join(root_dir, 'search', 'trie.js'))

    print ("Done, trie dumped in dumped.trie!")
