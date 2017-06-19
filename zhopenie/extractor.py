# -*- coding: utf-8 -*-
import itertools
from zhopenie.triple import Triple
from zhopenie.triple import Relation
from zhopenie.triple import Entity
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import SentenceSplitter
from pyltp import SementicRoleLabeller
from pyltp import Parser

class Extractor():

    def __init__(self):
        self.__clause_list = []
        self.__subclause_dict = {}
        self.__triple_list = []
        self.__segmentor = Segmentor()
        self.__postagger = Postagger()
        self.__recognizer = NamedEntityRecognizer()
        self.__parser = Parser()
        self.__labeller = SementicRoleLabeller()
        self.__words_full_list = []
        self.__netags_full_list = []

    @property
    def clause_list(self):
        return self.__clause_list

    @property
    def triple_list(self):
        return self.__triple_list


    def split(self, words, postags):
        start = 0
        for j, w in enumerate(words):
            if w == ',' or w == '，' or w == '。':
                clause = Clause(start, j-1 )
                self.__clause_list.append(clause)
                start = j + 1

        for clause in self.__clause_list:
            clause.split(postags)
            for subclause in clause.sub_clause_list:
                self.add_inverted_idx(subclause)

    def add_inverted_idx(self, subclause):
        for i in range(subclause.start_idx, subclause.end_idx):
            self.__subclause_dict[i] = subclause

    def load(self):
        self.__segmentor.load('ltp_data/cws.model')
        self.__postagger.load('ltp_data/pos.model')
        self.__recognizer.load('ltp_data/ner.model')
        self.__parser.load('ltp_data/parser.model')
        self.__labeller.load('ltp_data/srl')

    def release(self):
        self.__segmentor.release()
        self.__postagger.release()
        self.__recognizer.release()
        self.__parser.release()
        self.__labeller.release()

    def clear(self):
        self.__triple_list = []
        self.__words_full_list = []
        self.__netags_full_list = []
    
    def resolve_conference(self, entity):
        try:
            e_str = entity.get_content_as_str()
        except Exception:
            return '?'
        ref = e_str
        if e_str == '他' or e_str == '她':
            for i in range(entity.loc, -1, -1):
                if self.__netags_full_list[i].lower().endswith('nh'):
                    ref = self.__words_full_list[i]
                    break
        return ref
    
    def resolve_all_conference(self):
        for t in self.triple_list:
            e_str = self.resolve_conference(t.entity_1)
            try:
                t.entity_1.content = e_str.split()
            except Exception:
                pass

    def chunk_str(self, data):
        sents = SentenceSplitter.split(data)
        offset = 0
        for sent in sents:
            try:
                words = self.__segmentor.segment(sent)
                postags = self.__postagger.postag(words)
                netags = self.__recognizer.recognize(words, postags)
                arcs = self.__parser.parse(words, postags)
                roles = self.__labeller.label(words, postags, netags, arcs)
                self.chunk_sent(list(words), list(postags), list(arcs), offset)
                offset += len(list(words))
                self.__words_full_list.extend(list(words))
                self.__netags_full_list.extend(list(netags))
            except Exception as e:
                print(str(e))
                pass

    def chunk_sent(self, words, postags, arcs, offset):
        root = [i for i,x in enumerate(arcs) if x.relation == 'HED']
        if len(root) > 1:
            raise Exception('More than 1 HEAD arc is detected!')
        root = root[0]
        relations = [i for i, x in enumerate(arcs) if x.head == root and x.relation == 'COO']
        relations.insert(0,root)

        prev_e1 = None
        e1      = None
        for rel in relations:

            left_arc = [i for i, x in enumerate(arcs) if x.head == rel and x.relation == 'SBV']

            if len(left_arc) > 1:
                pass
                #raise Exception('More than 1 left arc is detected!')
            elif len(left_arc) == 0:
                e1 = prev_e1
            elif len(left_arc) == 1:
                left_arc = left_arc[0]
                leftmost = find_farthest_att(arcs, left_arc)
                e1 = Entity(1, [words[i] for i in range(leftmost, left_arc + 1)], offset + leftmost)


            prev_e1 = e1

            right_arc = [i for i, x in enumerate(arcs) if x.head == rel and x.relation == 'VOB']

            e2_list = []
            if not right_arc:
                e2 = Entity(2, None)
                e2_list.append(e2)
            else:
                right_ext = find_farthest_vob(arcs, right_arc[0])

                items = [i for i, x in enumerate(arcs) if x.head == right_ext and x.relation == 'COO']
                items = right_arc + items

                count = 0
                for item in items:
                    leftmost = find_farthest_att(arcs, item)


                    e2 = None

                    if count == 0:
                        e2 = Entity(2, [words[i] for i in range(leftmost, right_ext + 1)], offset+leftmost)
                    else:
                        p1 = range(leftmost, right_arc[0])
                        p2 = range(item, find_farthest_vob(arcs, item) + 1)
                        e2 = Entity(2, [words[i] for i in itertools.chain(p1, p2)])

                    e2_list.append(e2)
                    r = Relation(words[rel])
                    t = Triple(e1, e2, r)
                    self.__triple_list.append(t)
                    count += 1




def find_farthest_att(arcs, loc):
    att = [i for i, x in enumerate(arcs) if x.head == loc and (x.relation == 'ATT' or x.relation == 'SBV')]
    if not att:
        return loc
    else:
        return find_farthest_att(arcs, min(att))


def find_farthest_vob(arcs, loc):
    vob = [i for i, x in enumerate(arcs) if x.head == loc and x.relation == 'VOB']
    if not vob:
        return loc
    else:
        return find_farthest_vob(arcs, max(vob))





class Clause(object):

    def __init__(self, start=0 , end=0):
        self.start_idx = start
        self.end_idx = end
        self.__sub_clause_list = []

    @property
    def sub_clause_list(self):
        return self.__sub_clause_list

    def __str__(self):
        return '{} {}'.format(self.start_idx, self.end_idx)

    def split(self, postags):
        start = self.start_idx
        for k, pos in enumerate(postags):
            if k in range(self.start_idx, self.end_idx+1):
                if pos == 'c':
                    subclause = SubClause(start, k - 1)
                    self.__sub_clause_list.append(subclause)
                    start = k + 1


class SubClause():

    def __init__(self, start=0 , end=0):
        self.start_idx = start
        self.end_idx = end
