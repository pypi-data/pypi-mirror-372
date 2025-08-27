# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals, print_function
from xyz_util.mongoutils import Store, drop_id_field
from xyz_util.datautils import access
import hashlib


class QuestionStore(Store):
    name = 'exam_question'
    field_types = {int: ['year', 'month', 'ownerId', 'paperId', 'papers']}
    fields = ['year', 'month', 'ownerId', 'paperId', 'papers', 'ownerType', 'outline', 'type']

    def gen_paper(self, cond={}, limit=100):
        ordering = [('typeName', 1), ('year', -1), ('month', -1)]
        ts = {}
        for q in self.find(cond, {'_id': 0}, sort=ordering, limit=limit):
            qs = ts.setdefault(q['typeName'], [])
            qs.append(q)
            q['number'] = len(qs)
        return ts


def gen_question_uid(q, g):
    if 'uid' in q:
        return q['uid']
    gids = g.get('memo', '')
    qids = '%s%s%s' % (gids, q['type'], q['title'])
    return hashlib.md5(qids.encode('utf8')).hexdigest()[:7]


def gen_question_subid(q):
    options = q.get('options')
    if options:
        ss = sorted([a['text'] for a in options])
        return hashlib.md5('\n'.join(ss).encode('utf8')).hexdigest()[:7]


def extra_year_month(title):
    import re
    m = re.compile(r'真题(\d{2})(\d{2})$').search(title)
    if m:
        return '20' + m.group(1), m.group(2)
    m = re.compile(r'(\d{4})年').search(title)
    year = m.group(1) if m else None
    m = re.compile(r'(\d+)月').search(title)
    month = m.group(1) if m else None
    return year, month


def store_paper_questions(paper):
    from .helper import group_name_sumary
    qs = QuestionStore()
    p = paper.content.data  # content_object
    if paper.owner_type is None:
        return
    pws = '.'.join(paper.owner_type.natural_key())
    year, month = extra_year_month(p['title'])
    qs.update({'papers': paper.id}, {}, pull=dict(papers=paper.id))

    for g in p['groups']:
        for q in g['questions']:
            # if g.get('memo'):
            q['group'] = dict([(k, v) for k, v in g.items() if k in ['title', 'memo', 'inputs', 'number']])
            q['ownerType'] = pws
            q['typeName'] = group_name_sumary(g['title'])
            owner_id = q['ownerId'] = paper.owner_id
            if year:
                q['year'] = int(year)
            if month:
                q['month'] = int(month)
            uid = gen_question_uid(q, g)
            q.pop('papers', [])
            qs.upsert(dict(uid=uid, ownerId=owner_id), q, addToSet=dict(papers=paper.id))


def group_paper_questions(qset, group='outline'):
    ids = list(qset.values_list('id', flat=True))
    st = QuestionStore()
    return st.count_by(group, filter={'papers': {'$in': ids}}, output='dict')


class PaperStore(Store):
    name = 'exam_paper'
    fields = ['ownerId', 'id', 'ownerType']

    def gen_paper(self, outlines):
        qs = QuestionStore()
        # qs.find(cond)

    def save_paper(self, paper):
        self.upsert(
            {'id': paper.id},
            {
                'source': paper.content.source,
                'data': paper.content.data,
                'title': paper.title
            }
        )
