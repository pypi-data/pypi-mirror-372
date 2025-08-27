# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from xyz_exam.helper import *
from xyz_util.modelutils import get_generic_related_objects
from xyz_util.datautils import access
import json

def store_dump_course_questions(course_number, path='/tmp/%s.json'):
    from xyz_course.models import Course
    if '%' in path:
        path = path % course_number
    course = Course.objects.filter(name__startswith='%s '%course_number).first()
    cond=dict(outline={'$exists':True}, ownerType='course.course', ownerId=course.id)
    from xyz_exam.stores import QuestionStore
    qs = QuestionStore()
    d = dict(
       course=course.name
    )
    d['questions'] = list(qs.find(cond, {'_id': 0}))
    pids = set()
    for q in d['questions']:
        pid = access(q, 'papers.0') or access(q, 'paperId')
        pids.add(pid)
    d['papers'] = dict(get_generic_related_objects(course, 'exam.paper').filter(id__in=pids).values_list('title', 'id'))
    with open(path, 'w') as f:
        f.write(json.dumps(d))
    return d

def store_load_course_questions(file_name):
    data = json.loads(open(file_name).read())
    from xyz_course.models import Course
    print(data['course'])
    course = Course.objects.get(name=data['course'])
    spm = data['papers']
    dpm = dict(get_generic_related_objects(course, 'exam.paper').values_list('title', 'id'))
    std = {}
    for k,v in spm.items():
        #print(k, v)
        std[v] = dpm[k]

    from xyz_exam.stores import QuestionStore
    qs = QuestionStore()
    for q in data['questions']:
        uid=q['uid']
        cond=dict(ownerType='course.course', ownerId=course.id, uid=uid)
        nq = qs.get(cond)
        if not nq:
            pid = q['paperId']
            print('not found', q['uid'], pid, std.get(pid))
            print(q)
            continue
        if 'outline' not in nq:
            print(uid, q.get('outline'))
            qs.update(cond, {'outline': q['outline']})
        # print(q.get('uid'), q.get('paperId'), nq.get('paperId'), [std[pid] for pid in nq.get('papers', [])])
    # return std

def restore_exam_user(e):
    from xyz_school.models import ClassCourse, Class
    if not e.target_user_tags:
        return
    nms = e.target_user_tags.split('班级:')[-1]
    if not nms:
        return
    nms = nms.split(',')
    cls = Class.objects.filter(name__in=nms)
    rs = ClassCourse.objects.filter(course=e.owner, clazz__in=cls).values('teacher__user_id').distinct()
    rs = set([a['teacher__user_id'] for a in rs])
    if len(rs) == 1:
        e.user_id=rs.pop()
        e.save()
