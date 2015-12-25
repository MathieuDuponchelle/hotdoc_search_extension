#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys, os, json, re, shutil

from trie import Trie
from collections import defaultdict
from lxml import etree

here = os.path.dirname(__file__)

search_index = defaultdict(set)
with open(os.path.join(here, 'stopwords.txt'), 'r') as f:
    stop_words = set(f.read().split())

def lxml_parse_file(root_dir, filename):
    doc = etree.parse(filename)
    root = doc.getroot()
    url = os.path.relpath(filename, root_dir)

    main_content = root.find('.//div[@class="col-md-8"]')
    anchors = main_content.findall('.//div[@id]')
    for anchor in anchors:
        anchor_id = anchor.attrib['id']
        anchor_url = '%s#%s' % (url, anchor_id.strip())
        all_text = etree.tostring(anchor, method="text", encoding='unicode')
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z_\.]*[a-zA-Z_]', all_text)
        for token in tokens:
            token = token.lower()
            if token in stop_words:
                continue
            original = token
            token = token.replace('.', '}')
            token = token.replace('_', '|')
            search_index[token].add((anchor_url, original))

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

    prepare_output_folder(root_dir)

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                print("parsing", os.path.join(root, file)) 
                lxml_parse_file (root_dir, os.path.join(root, file))


    trie = Trie()
    for key, value in sorted(search_index.items()):
        trie.insert(key)

        key = key.replace('}', '.')
        key = key.replace('|', '_')
        metadata = {'urls': list(value)}

        with open (os.path.join(root_dir, 'search', key), 'w') as f:
            f.write(json.dumps(metadata))

    trie.to_file(os.path.join(root_dir, 'search', 'dumped.trie'))

    shutil.copy(os.path.join(here, 'trie.js'),
            os.path.join(root_dir, 'search', 'trie.js'))

    shutil.copy(os.path.join(here, 'search.js'),
            os.path.join(root_dir, 'search', 'trie.js'))

    print ("Done, trie dumped!")
