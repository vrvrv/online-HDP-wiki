import pickle
import threading, urllib, re, sys
import urllib.request
import urllib.error
import os
import argparse

def vocab_list(path):
    data = []
    with open(path, 'r') as f:
        w = True
        while w :
            w = f.readline()[:-1]
            data.append(w)
    vocab = dict()
    for word in data:
        word = word.lower()
        vocab[word] = len(vocab)
    return vocab

    
def fetch_wiki(n):
    """
    Downloads n articles in parallel from Wikipedia and returns lists
    of their names and contents. Much faster than calling
    get_random_wikipedia_article() serially.
    """
    maxthreads = 8
    WikiThread.articles = list()
    WikiThread.articlenames = list()
    wtlist = list()
    for i in range(0, n, maxthreads):
        print('downloaded %d/%d articles...' % (i, n))
        for j in range(i, min(i+maxthreads, n)):
            wtlist.append(WikiThread())
            wtlist[len(wtlist)-1].start()
        for j in range(i, min(i+maxthreads, n)):
            wtlist[j].join()
    return (WikiThread.articles, WikiThread.articlenames)


def get_random_wikipedia_article():
    """
    Downloads a randomly selected Wikipedia article (via
    http://en.wikipedia.org/wiki/Special:Random) and strips out (most
    of) the formatting, links, etc. 

    This function is a bit simpler and less robust than the code that
    was used for the experiments in "Online VB for LDA."
    """
    failed = True
    while failed:
        articletitle = None
        failed = False
        try:
            req = urllib.request.Request('http://en.wikipedia.org/wiki/Special:Random',
                                  None, { 'User-Agent' : 'x'})
            f = urllib.request.urlopen(req)
            while not articletitle:
                line = f.readline().decode('UTF-8')
                result = re.search('^\<title\>', line)

                if result:
                    articletitle = line[7:-21].replace(" ", "_")
                    break
                elif (len(line) < 1):
                    sys.exit(1)

            req = urllib.request.Request('http://en.wikipedia.org/w/index.php?title=Special:Export/%s&action=submit' \
                                      % (articletitle),
                                  None, { 'User-Agent' : 'x'})
            f = urllib.request.urlopen(req)
            all = f.read().decode('UTF-8')

        except (urllib.error.HTTPError, urllib.error.URLError, UnicodeEncodeError):
            print('oops. there was a failure downloading %s. retrying...'% articletitle)
            failed = True
            continue
        print('downloaded %s. parsing...' % articletitle)

        try:
            all = re.search(r'<text.*?>(.*)</text', all, flags=re.DOTALL).group(1)
            all = re.sub(r'\n', ' ', all)
            all = re.sub(r'\{\{.*?\}\}', r'', all)
            all = re.sub(r'\'', r'', all)
            all = re.sub(r'\[\[.*?\]\]', r'', all)
            all = re.sub(r'\&lt;.*?&gt;', '', all)
            all = re.sub(r'==\s*[Ss]ource\s*==.*', '', all)
            all = re.sub(r'==\s*[Rr]eferences\s*==.*', '', all)
            all = re.sub(r'==\s*[Ee]xternal [Ll]inks\s*==.*', '', all)
            all = re.sub(r'==\s*[Ee]xternal [Ll]inks and [Rr]eferences==\s*', '', all)
            all = re.sub(r'==\s*[Ss]ee [Aa]lso\s*==.*', '', all)
            all = re.sub(r'==\s*[Pp]ersonal [Ww]ebsite\s*==.*', '', all)
            all = re.sub(r'\[\[Category:.*', '', all)
            all = re.sub(r'http://[^\s]*', '', all)
            all = re.sub(r'\[\[Image:.*?\]\]', '', all)
            all = re.sub(r'Image:.*?\|', '', all)
            all = re.sub(r'\[\[.*?\|*([^\|]*?)\]\]', r'\1', all)
        except:
            # Something went wrong, try again. (This is bad coding practice.)
            print('oops. there was a failure parsing %s. retrying...' % articletitle)
            failed = True
            continue

    return(all, articletitle)
class WikiThread(threading.Thread):
    articles = list()
    articlenames = list()
    lock = threading.Lock()

    def run(self):
        (article, articlename) = get_random_wikipedia_article()
        WikiThread.lock.acquire()
        WikiThread.articles.append(article)
        WikiThread.articlenames.append(articlename)
        WikiThread.lock.release()


def _parse_doc_list(docs, vocab):
    D = len(docs)
    
    wordids = list()
    wordcts = list()
    for d in range(D):
        docs[d] = docs[d].lower()
        docs[d] = re.sub(r'-', ' ', docs[d])
        docs[d] = re.sub(r'[^a-z ]', '', docs[d])
        docs[d] = re.sub(r' +', ' ', docs[d])
        words = str.split(docs[d])
        ddict = dict()
        for word in words:
            if (word in vocab):
                wordtoken = vocab[word]
                if (not wordtoken in ddict):
                    ddict[wordtoken] = 0
                ddict[wordtoken] += 1
        wordids.append(ddict.keys())
        wordcts.append(ddict.values())

    return wordids, wordcts

def parse_doc_list(docs, vocab):
    D = len(docs)
    
    docs_id = list()

    for d in range(D):
        docs[d] = docs[d].lower()
        docs[d] = re.sub(r'-', ' ', docs[d])
        docs[d] = re.sub(r'[^a-z ]', '', docs[d])
        docs[d] = re.sub(r' +', ' ', docs[d])
        words = str.split(docs[d])
        ddoc = list()
        for word in words:
            if (word in vocab):
                wordtoken = vocab[word]
                ddoc.append(wordtoken)
        docs_id.append(ddoc)

    return docs_id

vocab = vocab_list(os.getcwd()+'/data/dictnostops.txt')

parser = argparse.ArgumentParser(description='data prepare')
parser.add_argument('--doc', type=int, default = 5)
parser.add_argument('--spl', type=int, default = 20)

args = parser.parse_args()


if __name__ == '__main__':
    num_of_doc_each_split = args.doc
    num_of_split = args.spl

    num_of_test = 30

    num = 1
    seen_doc = []

    for it in range(1, 1+num_of_split):
        
        # Fetch data from wikipedia in random
        DocSet, Title = fetch_wiki(num_of_doc_each_split)
        DocSet = parse_doc_list(DocSet, vocab)
        for doc, title in zip(DocSet, Title):
            title = title.replace('/', "")
            if title in seen_doc :
                continue
            try : 
                with open(f'./data/dat{it}/'+title+'.pkl', 'wb') as f:
                    pickle.dump(doc, f, protocol = 2)
            except FileNotFoundError :
                os.makedirs('./data/dat'+str(it), exist_ok = True)
                with open(f'./data/dat{it}/'+title+'.pkl', 'wb') as f:
                    pickle.dump(doc, f, protocol = 2)
            num += 1
            seen_doc.append(title)


    # Fetch data from wikipedia in random
    DocSet, Title = fetch_wiki(num_of_test)
    DocSet = parse_doc_list(DocSet, vocab)
    for doc, title in zip(DocSet, Title):
        title = title.replace('/', "")
        if title in seen_doc :
            continue
        try : 
            with open(f'./data/test/'+title+'.pkl', 'wb') as f:
                pickle.dump(doc, f, protocol = 2)
        except FileNotFoundError :
            os.makedirs('./data/test/dat'+str(it), exist_ok = True)
            with open(f'./data/test/'+title+'.pkl', 'wb') as f:
                pickle.dump(doc, f, protocol = 2)
        num += 1
        seen_doc.append(title)

