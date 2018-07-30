import asteriks
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()


def get_bibtex(ID, force_abstract=True):
    '''Builds the bibtex citation for a K2 Guest Observer Proposal using the
    GO ID.

    Queries K2/GO website.

    Parameters
    ----------
    ID : string or int
        GO proposal ID
    force_abstract : bool
        Only return a result if an abstract is present. If True, will return None
        if no abstract is given on the K2 GO website.

    Returns
    -------
    bib : string
        Bibtex formated citation
    '''
    url = 'https://keplerscience.arc.nasa.gov/data/k2-programs/{}.txt'.format(ID)
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data, 'html.parser')
    if '404 Not Found' in str(soup):
        return None
    results = {'ID':ID}
    for item in ['Title:', 'PI:', 'CoIs:']:
        results[item[:-1]] = (str(soup).split(item)[1].split('\n')[0]).split('(')[0].strip()
    abstract=''
    for s in str(soup).split('\n\n'):
        if np.asarray([s.startswith(item) for item in ['#', 'Title:', 'CoIs:', 'PI:']]).any():
            continue
        abstract = '{}{}'.format(abstract, s)
    if (abstract == '') and (force_abstract):
            return None
    results['Abstract'] = abstract
    c = int(ID[2:-3])
    if c in [0, 1]:
        date = ['February 2014']
    if c in [2, 3, 4]:
        date = ['June 2014']
    if c in [5, 6, 7]:
        date = ['October 2014']
    if c in [8, 9, 10]:
        date = ['June 2015']
    if c in [11, 12, 13]:
        date = ['Februrary 2016']
    if c in [14, 15, 16]:
        date = ['November 2016']
    if c in [17, 18, 19]:
        date = ['October 2017']
    results['Date'] = date[0]
    results['URL'] = url
    authors = np.append(results['PI'].split(';'), results['CoIs'].split(';'))
    authors = authors[authors != '']
    authors = ' and '.join(['{{{}}}, {}.'.format(auth.strip().split(' ')[0][:-1], auth.strip().split(' ')[0][0]) for auth in authors])
    bib = ("@MISC{{{0}ktwo.prop{1}{7},\n\tauthor = {{{2}}},"
           "\n\ttitle = {{{3}}},\n\tabstract = {{{6}}}"
           "\n\thowpublished = {{K2 Proposal}},"
           "\n\tyear = {{{0}}},\n\tmonth = {{{4}}},\n\turl = {{{5}}},\n\t"
           "notes = {{K2 Proposal {1}}}\n}}"
            "".format(results['Date'].split(' ')[1], results['ID'], authors, results['Title'], results['Date'].split(' ')[0], results['URL'], results['Abstract'], authors[1]))
    return bib


def run():
    '''Write a bitex file for all GO IDs
    '''
    go = pd.read_csv('GO_proposal_metadata.csv')
    ids = go['Investigation IDs'].unique()
    IDs = []
    for i in ids:
        for n in i.split('|'):
            if n.strip().startswith('GO'):
                IDs.append(n.strip().replace('_LC','').replace('_SC',''))
    IDs = np.unique(np.asarray(IDs))
    with open("K2bib.txt", "a") as myfile:
        for ID in IDs:
            bib = get_bibtex(ID)
            if bib is None:
                continue
            myfile.write(bib)
            myfile.write('\n\n\n\n')
