#!/usr/bin/env python3
"""
Builds taxonomy lineages
"""
import io
import logging
import os
import urllib.request

ROOT = 'root'


class Node:
    def __init__(self, tax_id):
        self.tax_id = tax_id
        self.children = []
        self.name = ''

    def __rank_tree__(self, parent_rank, lineages={}):
        '''Creates a dictionary of sets with keys being ranks pointing
        to a set of parent ranks via tree traversal.
        '''
        if self.rank != 'no rank' and self.rank != parent_rank:
            if self.rank in lineages:
                lineages[self.rank].add(parent_rank)
            else:
                lineages[self.rank] = set()
            parent_rank = self.rank
        for c in self.children:
            c.__rank_tree__(parent_rank, lineages)
        return lineages

    def __repr__(self):
        return '{} "{}" [{}]'.format(self.tax_id, self.name, self.rank)

    def add_child(self, child):
        self.children.append(child)

    def expand_no_ranks(self, suffix, ranks, parent=ROOT):
        if self.rank == 'no rank':
            self.rank = parent + suffix
            if self.rank not in ranks:
                ranks.insert(ranks.index(parent) + 1, self.rank)
        for c in self.children:
            c.expand_no_ranks(suffix, ranks, self.rank)

    def prune(self, keep):
        cut = self.tax_id not in keep
        for c in list(self.children):
            if c.prune(keep):
                self.children.remove(c)
            else:
                cut = False
        return cut

    def ranks(self, ranks=set()):
        ranks.add(self.rank)
        for c in self.children:
            c.ranks(ranks)
        return ranks

    def get_lineages(self, ranks, lineages=None, lin=None):
        if lineages is None:
            lineages = []
        if lin is None:
            lin = {}
        if self.rank in ranks:
            lin.update({self.rank: self.tax_id})
            lineages.append(
                {'tax_id': self.tax_id,
                 'tax_name': self.name,
                 'rank': self.rank,
                 **lin})
        for c in self.children:
            c.get_lineages(ranks, lineages, lin.copy())
        return lineages


class Tree(dict):
    '''
    Builds and returns all the nodes as a dictionary object
    '''
    def __init__(self, nodes, names=None):
        for tax_id, parent_id, rank in nodes:
            if tax_id in self:
                node = self[tax_id]
            else:
                node = Node(tax_id)
                self[tax_id] = node

            node.rank = rank

            if tax_id == parent_id:  # top node, no parent
                self.root = node
                continue

            if parent_id in self:
                parent = self[parent_id]
            else:
                parent = Node(parent_id)
                self[parent_id] = parent

            parent.add_child(node)

        for tax_id, name in names:
            self[tax_id].name = name

        self.ranks = self.__ranks__()

    def __ranks__(self):
        '''
        Determines rank order
        '''
        lineages = self.root.__rank_tree__(self.root.rank)
        for l in lineages.values():
            l.discard(self.root.rank)
        ranks = []
        if self.root.rank != 'no rank':
            ranks.append(self.root.rank)
        while lineages:
            next_rank = sorted(lineages, key=lambda x: len(lineages[x]))[0]
            ranks.append(next_rank)
            del lineages[next_rank]
            for v in lineages.values():
                v.discard(next_rank)
        return ranks

    def include_root(self):
        if self.ranks[0] != ROOT:
            self.root.rank = ROOT
            self.ranks.insert(0, ROOT)

    def expand_ranks(self, suffix):
        self.include_root()
        self.root.expand_no_ranks(suffix, self.ranks)

    def get_lineages(self):
        return self.root.get_lineages(self.ranks)


def get_taxdmp(url):
    logging.info('downloading ' + url)
    tar, headers = urllib.request.urlretrieve(url, os.path.basename(url))
    logging.debug(str(headers).strip())
    return tar


def get_data(taxdmp, name_class='scientific name'):
    nodes = io.TextIOWrapper(taxdmp.extractfile('nodes.dmp'))
    nodes = (n.strip().replace('\t', '').split('|') for n in nodes)
    nodes = (n[:3] for n in nodes)  # tax_id,parent,rank
    names = io.TextIOWrapper(taxdmp.extractfile('names.dmp'))
    names = (n.strip().replace('\t', '').split('|') for n in names)
    names = (n for n in names if n[3] == name_class)
    names = (n[:2] for n in names)  # tax_id,name
    return nodes, names


def setup_logging(namespace):
    loglevel = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }.get(namespace.verbosity, logging.DEBUG)
    if namespace.verbosity > 1:
        logformat = '%(levelname)s taxtree %(message)s'
    else:
        logformat = 'taxtree %(message)s'
    logging.basicConfig(stream=namespace.log, format=logformat, level=loglevel)
