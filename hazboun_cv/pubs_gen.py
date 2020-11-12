#!/usr/bin/env python
# coding: utf-8

import numpy as np
import bibtexparser as btp
import argparse, os
from datetime import datetime

parser = argparse.ArgumentParser()

path = os.path.dirname(os.path.abspath(__file__))
bibpath = path +'/hazboun_cv.bib'
pubspath = path + '/pub_entries.tex'
maintex_path = './'
parser.add_argument('--bibpath', dest='bibpath', action='store',
                    type=str, default=bibpath,
                    help='Path to bibliography.')
parser.add_argument('--longjour', dest='longjour', action='store_true',
                    default=True,
                    help='Flag to use long journal titles. ')
parser.add_argument('--pubspath', dest='pubspath', action='store',
                    type=str, default=pubspath,
                    help='Path to publication entries file.')
parser.add_argument('--maintex_path', dest='maintex_path', action='store',
                    type=str, default=None,
                    help='Path to main tex file.')

args = parser.parse_args()

aastexbib = {r'\baas':r'{Bulletin of American Astronomical Society}',
             r'\prd':r'{Physical Review D}',
             r'\prl':r'{Physical Review Letters}',
             r'\apjl':r'{The Astrophysical Journal Letters}',
             r'\apj':r'{The Astrophysical Journal}',
             r'\cqg':r'{Classical and Quantum Gravity}',
             r'\npb':r'{Nuclear Physics B}',
             r'\aapr':r'{The Astronomy and Astrophysics Review}',
             r'\ajp':r'{American Journal of Physics}',
             r'\apjs':r'{The Astrophysical Journal Supplements}',
             r'\grg':r'{General Relativity and Gravitation}',
             r'\jpcs':r'{Journal of Physics: Conference Series}',
             r'\joss':r'{Journal of Open Software Science}',
             r'\mnras':r'{Monthly Notices of the Royal Astronomical Society}',
             r'\clrpaawp':r'{Canadian Long Range Plan for Astronony and Astrophysics White Papers}',
             r'arXiv':r'{Arxiv:}',}

Months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
doi = 'https://doi.org/'
arxiv = 'https://arxiv.org/abs/'

with open(args.bibpath) as bibtex_file:
    bib = btp.bparser.BibTexParser(common_strings=True).parse_file(bibtex_file)#btp.load(bibtex_file)

# Fill in empt month values.
[en.update({'month':'jan'}) for en in bib.entries if 'month' not in en.keys()]
[en.update({'keywords':en['keywords']+', submitted'})
 for en in bib.entries if (en['journal']=='arXiv' and 'technical' not in en['keywords'])]
def get_sorted_kw_list(kw):
    if isinstance(kw,(list,np.ndarray)):
        pass
    elif isinstance(kw,str):
        kw = [kw]

    pubs = [en for en in bib.entries for key in kw if key in en['keywords']]
    dates = ['{0}/{1}'.format(Months.index(pub['month'].lower()[:3])+1,
                              pub['year'])
             for pub in pubs]
    isort = np.argsort([datetime.strptime(day, "%m/%Y").timestamp()
                        for day in dates])[::-1]
    return list(np.array(pubs)[isort])

def pubitem(title,authors,url,journal):
    return rf'''\pubitem{{{title}}}
         {{{authors}}}
         {{{url}}}
         {{{journal}}}'''

def get_bibitems(bibs):
    '''Given a list of bibliography entries return a list of cv items.'''
    items = []
    for ent in bibs:
        try:
            url = doi + ent['doi']
        except:
            try:
                url = arxiv + ent['eprint']
            except:
                print(ent['title'])
        author_list = ent['author'].split(' and ')
        author_list = ['~'.join(au.split(', ')[::-1]) for au in author_list]
        L = len(author_list)
        if L > 5:
            if 'Hazboun' in author_list[0]:
                authors = r"""\textbf{{J.~S.~{{Hazboun}}}}, et al. [{0} Authors]""".format(L)
            elif 'Hazboun' in author_list[1]:
                authors = r"""{0}, \textbf{{J.~S.~{{Hazboun}}}}, et al. [{1} Authors]""".format(author_list[0],L)
            else:
                authors = r"""{0}, [...], \textbf{{J.~S.~{{Hazboun}}}}, et al. [{1} Authors]""".format(author_list[0],L)
        elif L<=5:
            authors = ', '.join(author_list)
            authors= authors.replace('J.~S.~{Hazboun}','\\textbf{J.~S.~Hazboun}')

        jname = aastexbib[ent['journal']] if args.longjour else ent['journal']
        if 'Arxiv' in jname:
            jname += ent['eprint']
        else:
            if 'number' in ent.keys():
                numpage = ent['number']
            else:
                numpage = 'pp. {0}'.format(ent['pages'])
            jname += ', \\textbf{{{0}}}, {1}, ({2})'.format(ent['volume'],
                                                        numpage,
                                                        ent['year'])
        # journal= journal, \textbf{volume},number, (year)
        items.append(pubitem(ent['title'],
                             authors,
                             url,
                             jname))

    return items

#Get various lists. Will double return if both in keywords
collab = get_sorted_kw_list(['nanograv','ipta'])
theory = get_sorted_kw_list('theory')
pta = get_sorted_kw_list('pta')
published = get_sorted_kw_list('published')
submitted = get_sorted_kw_list('submitted')
white = get_sorted_kw_list(['white paper', 'technical'])
keypubs = get_sorted_kw_list('key')

submitems = get_bibitems(submitted)
publitems = get_bibitems(published)
whiteitems = get_bibitems(white)
keypubitems = get_bibitems(keypubs)

for ii in publitems:
    print(ii)

with open(args.pubspath,'w') as fout:
    for it in publitems:
        fout.write(it + '\n')
        fout.write('\n')

with open(path+'/sub_entries.tex','w') as fout:
    for it in submitems:
        fout.write(it + '\n')
        fout.write('\n')

with open(path+'/wp_entries.tex','w') as fout:
    for it in whiteitems:
        fout.write(it + '\n')
        fout.write('\n')

with open(path+'/keypub_entries.tex','w') as fout:
    for it in keypubitems:
        fout.write(it + '\n')
        fout.write('\n')

#
# for en in collab:
#     print(en['title'])
#
# def pubitem(title,authors,url,journal):
#     return fr'\pubitem{title}{authors}{url}{journal}'
#
