import sys, re, os, shutil
from random import shuffle
from hotdoc_search_extension.trie import Trie

if __name__ == '__main__':

    here = os.path.dirname(__file__)
    shutil.copy(os.path.join(here, '../javascript/trie.js'),
            os.path.join(here, 'trie.js'))

    shutil.copy(os.path.join(here, '../javascript/search.js'),
            os.path.join(here, 'search.js'))

    if os.path.exists(os.path.join(here, 'dumped.trie')):
        print ("All done")
        sys.exit(0)

    trie = Trie()
    word_count = 0
    DICT = os.path.join(here, 'somewords.txt')

    with open(DICT, 'r') as f:
        words = [w.lower() for w in f.read().split()]

    # Make sure unsorted insertions work.
    shuffle(words)

    for word in words:
        if not re.match(r'^[a-z]+$', word):
            continue

        word_count += 1
        trie.insert(word)
        if (word_count % 100) == 0:
            sys.stderr.write("{0}\r".format(word_count))
            sys.stderr.flush()

    print ("Should be True:", trie.exists('abaff'))
    print ("Should be False:", trie.exists('completenonsense'))
    print ("Should be True:", trie.exists('abalienate'))
    print ("Should be True", trie.exists('abalienated'))
    print ("Should be True", trie.remove('abalienate'))
    print ("Should be False", trie.exists('abalienate'))
    print ("Should be True", trie.exists('abalienated'))

    trie.to_file(os.path.join(here, 'dumped.trie'),
            os.path.join(here, 'trie_index.js'))

    ftrie = Trie.from_file(os.path.join(here, 'dumped.trie'))

    from datetime import datetime
    import cProfile
    dest = os.path.join(here, 'dumped2.trie')
    print 'to file now'
    n = datetime.now()
    #cProfile.run('ftrie.to_file(dest)', 'runstats')
    ftrie.to_file(dest)
    print "to file takes", datetime.now() - n

    ftrie2 = Trie.from_file(dest)
    print ("Should be True", ftrie2.exists('abaff'))
    print ("Should be False", ftrie2.exists('completenonsense'))

    print ("Should be True", ftrie.exists('abaff'))
    print ("Should be False", ftrie.exists('completenonsense'))

    print ("Removal in binary trie nao")
    ftrie.remove('abaff')
    print ("Should be False", ftrie.exists('abaff'))    
    print ("Insertion in binary trie nao")
    ftrie.insert('abaff')
    print ("Should be True", ftrie.exists('abaff'))

    
