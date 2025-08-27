# -*- coding:utf-8 -*-
from __future__ import division

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from xyz_util.statutils import do_rest_stat_action, using_stats_db
from xyz_util.mongoutils import MongoViewSet, json_util
from xyz_restful.mixins import UserApiMixin, BatchActionMixin
from . import models, serializers, stats, helper
from rest_framework import viewsets, decorators, response, status, exceptions
from xyz_restful.decorators import register, register_raw
from xyz_dailylog.mixins import ViewsMixin
import time


@register()
class PaperViewSet(ViewsMixin, UserApiMixin, BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Paper.objects.all()
    serializer_class = serializers.PaperSerializer
    search_fields = ('title',)
    filterset_fields = {
        'id': ['in', 'exact'],
        'owner_id': ['exact', 'in'],
        'is_active': ['exact'],
        'is_editable': ['exact'],
        'title': ['exact'],
        # 'is_break_through': ['exact'],
        'owner_type': ['exact'],
        'tags': ['exact', 'in'],
        # 'content': ['contains'],
        'create_time': ['range']
    }
    ordering_fields = ('is_active', 'title', 'create_time', 'questions_count')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PaperListSerializer
        return super(PaperViewSet, self).get_serializer_class()

    @decorators.action(['POST'], detail=False)
    def batch_active(self, request):
        return self.do_batch_action('is_active', True)

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_paper)

    @decorators.action(['GET', 'POST'], detail=True)
    def image_signature(self, request, pk):
        from xyz_qcloud.cos import gen_signature
        return response.Response(gen_signature(allow_prefix='/exam/paper/%s/images/*' % self.get_object().id))

    @decorators.action(['GET'], detail=False)
    def ids(self, request):
        qset = self.filter_queryset(self.get_queryset()).values_list('id', flat=True)
        return response.Response({'ids': list(qset)})

    @decorators.action(['GET'], detail=False, filter_backends=[DjangoFilterBackend])
    @method_decorator(cache_page(60 * 60 * 2))
    def count(self, request):
        c = self.filter_queryset(self.get_queryset()).count()
        return response.Response({'count': c})

    @decorators.action(['GET'], detail=False)
    def collect_questions(self, request):
        from .stores import QuestionStore
        from xyz_util.mongoutils import get_paginated_response
        from django.contrib.contenttypes.models import ContentType
        st = QuestionStore()
        qd = request.GET.copy()
        owner_id = qd.pop('owner_id', None)
        owner_type_id = ContentType.objects.get_by_natural_key('course', 'course').id
        rand = qd.get('random', False)
        count = int(qd.get('count', 20))
        d = st.normalize_filter(qd, cast=True)  # normalize_filter_condition(qd, st.field_types, st.fields)
        if owner_id:
            pids = models.Paper.objects.filter(
                owner_id=owner_id[0], owner_type_id=owner_type_id
            ).values_list('id', flat=True)
            d['papers'] = {
                '$in':list(pids)
            }
        print('collect_questions',  d)
        if rand:
            from xyz_util.mongoutils import drop_id_field
            return response.Response(dict(results=drop_id_field(st.random_find(d, count=count))))
        rs = st.find(d, {'_id': 0}).sort('updateTime', -1)
        return get_paginated_response(self, rs)

    @decorators.action(['GET'], detail=False)
    def questions_group(self, request):
        from .stores import QuestionStore
        st = QuestionStore()
        qd = request.GET
        group = qd.get('group', 'papers')
        d = st.normalize_filter(qd)
        return response.Response(st.count_by(group, filter=d, output='dict', unwind=group == 'papers'))

    @decorators.action(['PATCH'], detail=True)
    def outline_question(self, request, pk):
        from .stores import QuestionStore
        st = QuestionStore()
        rd = request.data
        uid = rd.get('uid')
        qd = {'papers': int(pk), 'uid': uid}
        st.update(qd, {'outline': rd.get('outline'), 'updateTime': int(time.time() * 1000)})
        return response.Response(rd)

    @decorators.action(['GET', 'POST'], detail=False)
    def chapter_papers(self, request):
        qd = request.query_params if request.method == 'GET' else request.data
        app, model = qd.get('owner_type').split('.')
        owner_id = qd.get('owner_id')
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_by_natural_key(app, model)
        owner = ct.get_object_for_this_type(pk=owner_id)
        if request.method == 'GET':
            papers = models.Paper.objects.filter(owner_type=ct, owner_id=owner_id, tags__in=['章节习题', '章节习题（备份）'])
        else:
            helper.backup_old_chapter_papers(owner)
            papers = helper.ChapterPaperGenerator(owner).generate()
        serializer = serializers.PaperListSerializer(papers, many=True)
        return response.Response(dict(results=serializer.data))


@register()
class AnswerViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Answer.objects.all()
    serializer_class = serializers.AnswerSerializer
    filterset_fields = {
        'paper': ['exact', 'in'],
        'user': ['exact', 'in'],
        'create_time': ['range']
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AnswerListSerializer
        return super(AnswerViewSet, self).get_serializer_class()

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_answer)

    @decorators.action(['PATCH'], detail=True, permission_classes=[], filter_backends=[])
    def grade(self, request, pk):
        qs = request.query_params
        exam_id = qs.get('exam')
        error = helper.check_token(request, exam_id)
        if error:
            return response.Response(error, status=status.HTTP_403_FORBIDDEN)
        return self.partial_update(request)


@register()
class StatViewSet(UserApiMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Stat.objects.all()
    serializer_class = serializers.StatSerializer
    filterset_fields = ('paper',)


@register()
class PerformanceViewSet(UserApiMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Performance.objects.all()
    serializer_class = serializers.PerformanceSerializer
    filterset_fields = {
        'paper': ['exact', 'in'],
        'paper_id': ['exact', 'in'],
        'user': ['exact']
    }
    search_fields = ('paper__title', 'user__first_name')
    ordering_fields = ('score', 'update_time')

    def get_queryset(self):
        qset = super(PerformanceViewSet, self).get_queryset()
        if self.action == 'erase':
            return qset
        return using_stats_db(qset)

    @decorators.action(['DELETE'], detail=True)
    def erase(self, request, pk):
        pf = self.get_object()
        pf.paper.answers.filter(user=pf.user).delete()
        pf.delete()
        return response.Response(dict(detail='done'))


@register()
class FaultViewSet(UserApiMixin, BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Fault.objects.all()
    serializer_class = serializers.FaultSerializer
    filterset_fields = {
        'paper': ['exact', 'in'],
        'question_id': ['exact'],
        'question_type': ['exact'],
        'corrected': ['exact'],
        'is_active': ['exact'],
        'user': ['exact'],
        'paper__owner_type': ['exact'],
        'paper__owner_id': ['exact'],
        'create_time': ['range']
    }
    ordering_fields = ['times', 'update_time']

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_fault)

    @decorators.action(['patch'], detail=True)
    def redo(self, request, pk):
        fault = self.get_object()
        rl = fault.detail.setdefault('result_list', [])
        right = request.data['right']
        rl.append(right)
        if not right:
            fault.times += 1
        fault.save()
        return response.Response(self.get_serializer(instance=fault).data)

    @decorators.action(['patch'], detail=False)
    def batch_correct(self, request):
        from datetime import datetime
        return self.do_batch_action('corrected', True, extra_params=dict(update_time=datetime.now()))


@register()
class ExamViewSet(BatchActionMixin, UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Exam.objects.all()
    serializer_class = serializers.ExamSerializer
    search_fields = ('name',)
    filterset_fields = {
        'name': ['exact', 'in'],
        'is_active': ['exact', 'in'],
        'owner_type': ['exact'],
        'user': ['exact', 'in'],
        'owner_id': ['exact', 'in'],
        'begin_time': ['gte', 'lte', 'range'],
        'end_time': ['gte', 'lte', 'range'],
        'manual_grade': ['exact']
    }
    ordering_fields = ('minutes', 'question_count', 'begin_time', 'end_time', 'actual_user_count', 'target_user_count')

    @decorators.action(['POST'], detail=False)
    def batch_active(self, request):
        return self.do_batch_action('is_active', True)

    @decorators.action(['GET', 'POST'], detail=True)
    def user_answer_signature(self, request, pk):
        from xyz_qcloud.cos import gen_signature
        sign = gen_signature(allow_prefix='/exam/exam/%s/answer/%s/*' % (pk, request.user.id))
        return response.Response(sign)

    @decorators.action(['GET'], detail=True, permission_classes=[], filter_backends=[])
    def all_answers(self, request, pk):
        error = helper.check_token(request, pk)
        if error:
            return response.Response(error, status=status.HTTP_403_FORBIDDEN)
        exam = self.get_object()
        paper = exam.paper
        answers = paper.answers
        uids = list(answers.values_list('user_id', flat=True))
        from xyz_school.models import Student
        students = Student.objects.filter(user_id__in=uids).values('number', 'name', 'id', 'user')
        return response.Response(dict(
            students=students,
            answers=serializers.AnswerSerializer(answers, many=True).data,
            paper=serializers.PaperSerializer(paper).data,
            exam=serializers.ExamSerializer(exam).data
        ))

    @decorators.action(['GET'], detail=True)
    def get_grade_token(self, request, pk):
        from django.core.signing import TimestampSigner
        signer = TimestampSigner(salt=str(pk))
        from datetime import datetime, timedelta
        import json, base64
        expire_time = datetime.now() + timedelta(days=7)
        d = dict(exam=pk, expire=expire_time.isoformat())
        token = signer.sign(base64.b64encode(json.dumps(d).encode('utf8')).decode())
        return response.Response(dict(token=token))

    @decorators.action(['GET'], detail=True)
    def performance(self, request, pk):
        exam = self.get_object()
        return response.Response(dict(performance=exam.performance()))

    def permission_denied(self, request, message=None, code=None):
        if self.action not in ['result', 'all_answers']:
            return super(ExamViewSet, self).permission_denied(request, message=message, code=code)
        pk = self.kwargs['pk']
        error = helper.check_token(request, pk)
        if not error:
            return
        if error == '验证码缺失':
            return super(ExamViewSet, self).permission_denied(request, message=message, code=code)
        raise exceptions.PermissionDenied(detail=error, code='403')

    @decorators.action(['GET'], detail=True, filter_backends=[])
    def result(self, request, pk):
        # error = helper.check_token(request, pk)
        # if error:
        #     return response.Response(error, status=status.HTTP_403_FORBIDDEN)
        exam = self.get_object()
        return response.Response(serializers.ExamResultSerializer(exam).data)

    @decorators.action(['GET'], detail=True, permission_classes=[], filter_backends=[])
    def attendance(self, request, pk):
        error = helper.check_token(request, pk)
        if error:
            return response.Response(error, status=status.HTTP_403_FORBIDDEN)
        exam = self.get_object()
        return response.Response(serializers.ExamResultSerializer(exam).data)

    @decorators.action(['POST'], detail=False)
    def auto_gen(self, request):
        return super(ExamViewSet, self).create(request)

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_exam)

    @decorators.action(['GET'], detail=False, filter_backends=[DjangoFilterBackend])
    @method_decorator(cache_page(60 * 60 * 2))
    def count(self, request):
        c = self.filter_queryset(self.get_queryset()).count()
        return response.Response({'count': c})

    def perform_create(self, serializer):
        super(ExamViewSet, self).perform_create(serializer)
        data = self.request.data
        paper = data.get('paper')
        if paper:
            exam = serializer.instance
            exam.generate_paper(paper, user=self.request.user)
            if not exam.is_active:
                exam.is_active = True
                exam.save()


@register_raw()
class QuestionViewSet(MongoViewSet):
    store_name = 'questions'
    permission_classes = []

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        from .stores import QuestionStore
        rd = request.GET
        cond = dict(
            ownerId=int(rd.get('ownerId'))
        )
        st = QuestionStore()
        rs = st.count_by('type', filter=cond)
        return response.Response(rs)
