#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys, re, os, shutil, json

from hotdoc_search_extension.trie import Trie
from lxml import etree
from collections import defaultdict

SECTIONS_SELECTOR=(
'./div[@id]'
)

INITIAL_SELECTOR=(
'./body'
'/div[@id="page-wrapper"]'
'/div[@class="row"]'
'/div[@class="col-md-8"]'
'/div[@id="main"]'
)


tok_regex = re.compile(r'[a-zA-Z_][a-zA-Z_\.]*[a-zA-Z_]')

def get_sections(root, selector='./div[@id]'):
    return root.xpath(selector)

def parse_content(section, stop_words, selector='.//p'):
    for elem in section.xpath(selector):
        text = etree.tostring(elem, method="text",
                encoding='unicode')

        tokens = tok_regex.findall(text)

        for token in tokens:
            original_token = token + ' '
            token = token.lower()
            if token in stop_words:
                yield (None, original_token)
                continue

            token = token.replace('.', '}')
            token = token.replace('_', '|')

            yield (token, original_token)

        yield (None, '\n')

def write_fragment(fragments_dir, url, text):
    dest = os.path.join(fragments_dir, url + '.fragment')
    try:
        f = open(dest, 'w')
    except IOError:
        os.makedirs(os.path.dirname(dest))
        f = open(dest, 'w')
    finally:
        f.write(text)
        f.close()

def parse_file(root_dir, filename, stop_words, fragments_dir):
    root = etree.parse(filename).getroot()
    initial = root.xpath(INITIAL_SELECTOR)[0]

    url = os.path.relpath(filename, root_dir)

    sections = get_sections(initial, SECTIONS_SELECTOR)
    for section in sections:
        section_id = section.attrib.get('id', '').strip()
        section_url = '%s#%s' % (url, section_id)
        section_text = ''

        for tok, text in parse_content(section, stop_words):
            section_text += text
            if tok is None:
                continue
            yield tok, section_url

        fragment = etree.tostring(section, encoding='unicode')
        write_fragment(fragments_dir, section_url, fragment)

def prepare_folder(dest):
    try:
        shutil.rmtree (dest)
    except OSError as e:
        pass

    try:
        os.mkdir (dest)
    except OSError:
        pass

def dump(index, dest):
    trie = Trie()
    for key, value in index:
        trie.insert(key)

        key = key.replace('}', '.')
        key = key.replace('|', '_')
        metadata = {'urls': list(value)}

        with open (os.path.join(dest, 'search', key), 'w') as f:
            f.write(json.dumps(metadata))

    trie.to_file(os.path.join(dest, 'search', 'dumped.trie'))

def create_index(root_dir, exclude_dirs=None, dest='.'):
    search_dir = os.path.join(dest, 'search')
    fragments_dir = os.path.join(search_dir, 'fragments')
    prepare_folder(search_dir)
    prepare_folder(fragments_dir)

    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'stopwords.txt'), 'r') as f:
        stop_words = set(f.read().split())

    if exclude_dirs is None:
        exclude_dirs=[]

    search_index = {}

    search_index = defaultdict(set)

    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            if f.endswith(".html"):
                for token, section_url in parse_file(root_dir, os.path.join(root,
                    f), stop_words, fragments_dir):
                    search_index[token].add(section_url)

    dump(sorted(search_index.items()), dest)

if __name__=='__main__':
    root_dir = sys.argv[1]
    create_index (sys.argv[1], exclude_dirs=['assets'])
