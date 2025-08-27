# -*- coding:utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from xyz_common.signals import to_save_version, new_version_posted
from datetime import datetime
from . import models, helper

import logging

log = logging.getLogger('django')


@receiver(post_save, sender=models.Answer)
def cal_performance(sender, **kwargs):
    try:
        # created = kwargs['created']
        # if not created:
        #     return
        answer = kwargs['instance']
        paper = answer.paper
        performance, created = paper.performances.update_or_create(
            paper=paper,
            user=answer.user,
            defaults=dict(update_time=datetime.now())
        )

        stat, created = models.Stat.objects.get_or_create(paper=paper)
        stat.add_answer(answer)
        # print 'stat'
        stat.save()
    except Exception as e:
        import traceback
        log.error("exam cal_performance with answer %s error:%s", answer.id, traceback.format_exc())


@receiver(post_save, sender=models.Answer)
def save_fault(sender, **kwargs):
    try:
        created = kwargs['created']
        if not created:
            return
        answer = kwargs['instance']
        helper.record_fault(answer)
    except Exception as e:
        import traceback
        log.error("exam save_fault with answer %s error:%s", answer.id, traceback.format_exc())

@receiver(post_save, sender=models.Answer)
def cal_exam_actual_user_count(sender, **kwargs):
    try:
        created = kwargs['created']
        if not created:
            return
        answer = kwargs['instance']
        paper = answer.paper
        owner = paper.owner
        if isinstance(owner, models.Exam):
            from django.db.models import Count
            owner.actual_user_count = paper.answers.aggregate(c=Count('user_id', distinct=True))['c']
            owner.save()
    except Exception as e:
        import traceback
        log.error("exam cal_exam_actual_user_count with answer %s error:%s", answer.id, traceback.format_exc())

@receiver(pre_save, sender=models.Content)
def save_paper_version(sender, **kwargs):
    to_save_version.send_robust(sender, instance=kwargs['instance'])

@receiver(post_save, sender=models.Content)
def to_store_paper_questions(sender, **kwargs):
    from .stores import store_paper_questions
    content = kwargs['instance']
    if not content.source:
        return
    paper = content.paper
    if paper.is_active:
        store_paper_questions(paper)


@receiver(new_version_posted, sender=models.Content)
def restruct_fault_when_paper_changed(sender, **kwargs):
    try:
        # created = kwargs['created']
        # if created:
        #     return
        content = kwargs['instance']
        paper = content.paper
        changed_fields = kwargs['changed_fields']
        # from django.contrib.contenttypes.models import ContentType
        # ct = ContentType.objects.get_for_model(models.Paper)
        # from xyz_common.models import VersionHistory
        # from datetime import date
        # changed = VersionHistory.objects.filter(content_type=ct, object_id=paper.id,
        #                                         create_time__gte=date.today()).exists()
        # if not changed:
        #     return
        if not paper.is_active:
            paper.faults.filter(is_active=True).update(is_active=False)
        if 'data' in changed_fields:
            from .helper import restruct_fault
            log.info('restruct_fault_when_paper_changed: %s', restruct_fault(paper))
    except:
        import traceback
        log.error("restruct_fault_when_paper_changed error: %s", traceback.format_exc())
