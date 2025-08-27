# -*- coding:utf-8 -*-
from __future__ import division, unicode_literals

__author__ = 'denishuang'

from xyz_util.datautils import access
from collections import OrderedDict

import re
from xyz_util.datautils import strQ2B
from . import models, choices
from django.contrib.contenttypes.models import ContentType
from functools import reduce
from django.utils.functional import cached_property


def distrib_count(d, a, reverse=False):
    a = str(a)
    counts = d.setdefault('counts', {})
    percents = d.setdefault('percents', {})
    counts[a] = counts.setdefault(a, 0) + 1
    tc = sum(counts.values())
    cas = [(int(float(k)), v) for k, v in counts.items()]
    cas.sort(reverse=reverse)
    s = 0
    for k, v in cas:
        s += v
        percents[str(k)] = round(s / float(tc), 3)
    d['count'] = tc
    return d


def answer_is_empty(a):
    if isinstance(a, (list, tuple)):
        return not any(a)
    return not a


def answer_equal(standard_answer, user_answer):
    if len(standard_answer) != len(user_answer):
        return False
    l = zip(standard_answer, user_answer)
    return all([b in a.split('|') for a, b in l])


RE_MULTI_ANSWER_SPLITER = re.compile(r"[|()、]")


def split_answers(s):
    if isinstance(s, (list, tuple)):
        return s
    return RE_MULTI_ANSWER_SPLITER.split(strQ2B(s))


"""
In [36]: answer_match(['A|C','B','C','D'],['C','B'],True)
Out[36]: 0.5

In [37]: answer_match(['A','B','C','D'],['C','B'])
Out[37]: 0.5

In [38]: answer_match(['A','B','C','D'],['B'])
Out[38]: 0.25

In [39]: answer_match(['A','B','C','D'],['B'],True)
Out[39]: 0.0

In [40]: answer_match(['A','B','C','D'],['B','E'])
Out[40]: 0.0

In [41]: answer_match(['A','B','C','D'],['B','A','D','C'])
Out[41]: 1.0
"""


def answer_match(standard_answer, user_answer, one_by_one=False):
    sa = standard_answer
    ua = user_answer
    lsa = len(sa)
    lua = len(ua)
    if lua > lsa:
        return -1
    l = zip(sa[:lua], ua)
    c = 0
    for s, u in l:
        if one_by_one:
            if u in split_answers(s):
                c += 1
        else:
            if u in sa:
                c += 1
            else:
                c = 0
                break
    return c / lsa


def extract_fault(answer):
    m = dict([(a['number'], a) for a in answer.detail if not (answer_is_empty(a['userAnswer']) or a['right'])])
    p = answer.paper.content.data
    rs = []
    for g in p['groups']:
        for q in g['questions']:
            qnum = q['number']
            q['group'] = dict(title=g.get('title'), memo=g.get('memo'), number=g.get('number'))
            if qnum in m:
                rs.append((q, m[qnum]))
    return rs


def record_fault(answer):
    user = answer.user
    paper = answer.paper

    fs = extract_fault(answer)
    nums = [a['number'] for a in answer.detail]
    models.Fault.objects.filter(user=answer.user, paper=answer.paper).exclude(question_id__in=nums).update(
        is_active=False)
    for question, qanswer in fs:
        question_id = question['number']
        lookup = dict(user=user, paper=paper, question_id=question_id)
        fault = models.Fault.objects.filter(**lookup).first()
        if not fault:
            models.Fault.objects.create(
                question=question,
                question_type=choices.MAP_QUESTION_TYPE.get(question['type']),
                detail=dict(lastAnswer=qanswer), **lookup
            )
        else:
            fault.times += 1
            fault.detail['last_answer'] = qanswer
            fault.corrected = False
            fault.question = question
            fault.is_active = True
            fault.question_type = choices.MAP_QUESTION_TYPE.get(question['type'])
            from datetime import datetime
            fault.create_time = datetime.now()
            rl = fault.detail.setdefault('result_list', [])
            rl.append(False)
            fault.save()


def restruct_fault(paper):
    import textdistance
    jws = textdistance.JaroWinkler()

    qtm = {}
    from copy import deepcopy
    gs = deepcopy(paper.content.data.get('groups'))
    nums = []
    for g in gs:
        for q in g.get('questions'):
            q['group'] = dict(title=g.get('title'), memo=g.get('memo'), number=g.get('number'))
            qtm[q.get('title')] = q
            nums.append(q.get('number'))
    models.Fault.objects.filter(paper=paper).exclude(question_id__in=nums).update(is_active=False)
    bm = {True: [], False: []}
    for f in paper.faults.all():
        q = f.question
        t1 = q.get('title')
        tp1 = t1.split('题】')[-1]
        qn = None
        mdl = 0.8
        for t2 in qtm.keys():
            tp2 = t2.split('题】')[-1]
            dl = jws.similarity(tp1, tp2)
            if dl > mdl:
                qn = qtm.get(t2)
                mdl = dl
        if not qn:
            bm[False].append(f.id)
            f.is_active = False
            f.save()
            continue
        t2 = qn.get('title')
        if t1 != t2 \
                or q.get('options') != qn.get('options') \
                or q.get('answer') != qn.get('answer') \
                or q.get('explanation') != qn.get('explanation'):
            bm[True].append(f.id)
            f.question = qn
            f.save()
    return bm


def cal_correct_straight_times(rl):
    c = 0
    for i in range(len(rl) - 1, -1, -1):
        if not rl[i]:
            break
        c += 1
    return c


def check_token(request, pk):
    from django.core.signing import TimestampSigner
    import json, base64
    from datetime import datetime
    signer = TimestampSigner(salt=str(pk))
    qs = request.query_params
    token = qs.get('token')
    if not token:
        return '验证码缺失'
    try:
        s = signer.unsign(token)
        s = base64.b64decode(s)
        d = json.loads(s)
        if d['exam'] != pk or d['expire'] <= datetime.now().isoformat():
            return '验证码无效'
    except:
        import traceback
        print(traceback.format_exc())
        return '验证码无效'



def int_to_roman(num):
    if num<=12:
        return ['', 'Ⅰ','Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ', 'Ⅺ', 'Ⅻ'][num]
    TS = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
          (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
          (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "Ⅰ")]
    # 用来保存整数转罗马数字的信息
    roman_num = ""
    for number, roman in TS:
        # 用来保存整数和余数部分
        # 整数表示重复的次数
        count, num = divmod(num, number)
        roman_num += roman * count
        # 当余数为0时结束循环
        if num == 0:
            break
    return roman_num


def group_name_sumary(n):
    r = re.compile(r'[(（,， .。:： <Ⅰ-Ⅹ]')
    return r.split(n)[0].strip()


def group_name_normalize(n):
    return choices.MAP_QUESTION_TYPE_NAME.get(n, n) + '题'


def backup_old_chapter_papers(owner):
    ct = ContentType.objects.get_for_model(owner)
    old = '章节习题'
    new = '章节习题（备份）'
    c = models.Paper.objects.filter(
        owner_id=owner.pk,
        owner_type=ct,
        tags=new,
        is_active=False
    ).count()
    if c > 0:
        return
    print('备份%s试卷:%s' % (old, owner))
    models.Paper.objects.filter(
        owner_id=owner.pk,
        owner_type=ct,
        tags=old
    ).update(
        tags=new,
        is_active=False
    )


def questions_group_by_memo(qs):
    gs = {}
    for q in qs:
        k = access(q, 'group.memo') or ''
        gs.setdefault(k, []).append(q)
    return gs


def group_split_by_memo(gs):
    rs = OrderedDict()
    for gn, qs in gs.items():
        ngs = questions_group_by_memo(qs)
        if len(ngs) <= 1:
            nqs = ngs.get('')
            if nqs:
                rs[gn] = dict(questions=nqs)
        else:
            i = 1
            for memo, nqs in ngs.items():
                rs['%s%s' % (gn, int_to_roman(i))] = dict(memo=memo, questions=nqs)
                i += 1
    return rs

class PaperGenerator(object):

    def __init__(self, owner, target_owner=None):
        from .stores import QuestionStore
        self.owner = owner
        self.target_owner = target_owner or owner
        self.owner_type = ContentType.objects.get_for_model(owner)
        self.papers = self.get_source_papers()
        self.user = self.papers.first().user
        self.store = QuestionStore()

    @cached_property
    def group_number_orders(self):
        ids = list(self.papers.values_list('id', flat=True))
        cond = {
            'group.number': {'$exists': 1},
            'papers': {'$in': ids}
        }
        al = list(
            self.store.group_by(
                'typeName',
                filter=cond,
                aggregate={
                    'avg':
                        {'$avg': '$group.number'},
                    'count': {'$sum': 1}
                }
            )
        )
        return [a['_id'] for a in sorted(al, key=lambda a: a['avg'])]


    def get_source_papers(self):
        return models.Paper.objects.filter(
            owner_id=self.owner.pk,
            owner_type=self.owner_type,
            is_active=True
        )

    def normalize(self, gs):
        ogs = OrderedDict([(a, []) for a in self.group_number_orders])
        ogs.update(gs)
        return group_split_by_memo(ogs)

    def gen_paper(self, title, cond, order_number=0, tags='章节习题', parent_id=0, **kwargs):
        from .models import Paper, Content
        filter = {
            'ownerType': self.owner._meta.label_lower,
            'ownerId': self.owner.pk,
            'typeName': {'$exists': True}
        }
        filter.update(cond)
        qts = self.store.gen_paper(filter, **kwargs)
        if not qts:
            return None
        qts = self.normalize(qts)
        gs = []
        gc = 0
        qc = 0
        score = 0
        for qt, g in qts.items():
            gc += 1
            qs = g['questions']
            for qi, q in enumerate(qs):
                qc += 1
                q['position'] = qi + 1
                q['number'] = qc
                q['id'] = 'g%dq%d' % (gc, qi + 1)
            g.update(dict(title=qt, id='g%d' % gc, number=gc, questionCount=len(qs)))
            score += reduce(lambda a, b: a + b['score'], qs, 0)
            gs.append(g)
        cdata = dict(title=title, groups=gs, totalScore=score)
        paper, created = Paper.objects.update_or_create(
            owner_id=self.target_owner.pk,
            owner_type=ContentType.objects.get_for_model(self.target_owner),
            title=title,
            tags=tags,
            defaults=dict(
                user=self.user,
                is_active=qc>0,
                is_editable=False,
                order_number=order_number,
                questions_count=qc,
                parent_id=parent_id
            ))
        content, created = Content.objects.update_or_create(
            paper=paper,
            defaults=dict(
                data=cdata
            )
        )
        return paper


def chapter_name_normalize(n):
    r = re.compile(r'(\d+)')
    ps = r.split(n)
    if len(ps) != 3:
        return n
    i = int(ps[1])
    if i == 0:
        return '绪论'
    from xyz_util.datautils import digits2cn
    return ps[0] + digits2cn(i) + ps[2]


class ChapterPaperGenerator(PaperGenerator):

    def generate(self):
        categories = self.get_categories()
        ps = []
        no = 0
        pids = list(self.papers.values_list('id', flat=True))
        for n in self.owner:
            ols = [sn.name for sn in n.items]
            for cn, cts in categories:
                pname = '%s %s（%s）' % (chapter_name_normalize(n.prefix), n.name, cn)
                cond = {
                    'type': {'$in': cts},
                    'papers': {'$in': pids},
                    'outline': {'$in': ols}
                }
                paper = self.gen_paper(pname, cond, order_number=no)
                if not paper:
                    continue
                ps.append(paper)
                no += 1
                for i, sn in enumerate(n.items):
                    pname = '%s.%s（%s）' % (i+1, sn, cn)
                    cond = {
                        'ownerType': self.owner._meta.label_lower,
                        'ownerId': self.owner.pk,
                        'type': {'$in': cts},
                        'papers': {'$in': pids},
                        'outline': sn.name
                    }
                    p = self.gen_paper(pname, cond, order_number=no, tags='小节练习', parent_id=paper.id)
                    if not p:
                        continue
                    ps.append(p)
                    no += 1
        return ps

    def get_source_papers(self):
        return super(ChapterPaperGenerator, self).get_source_papers().filter(
            tags__in=['历年真题', '模拟真题']
        )

    def get_categories(self):
        SUB_LIST = [v for k, v in choices.MAP_QUESTION_TYPE_NO.items() if k in choices.SUBJECTIVE_TYPES]
        OBJ_LIST = [v for k, v in choices.MAP_QUESTION_TYPE_NO.items() if k not in choices.SUBJECTIVE_TYPES]
        return [('客观题', OBJ_LIST), ('主观题', SUB_LIST)]

    # def group_by_memo(qs):
    #     gs = {}
    #     for q in qs:
    #         k = access(q, 'group.memo') or ''
    #         gs.setdefault(k, []).append(q)
    #     return gs

class ExamGenerator(object):

    def gen_exam(self, title, cond, order_number=0, tags='章节习题', parent_id=0, **kwargs):
        pass

