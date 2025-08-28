# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals, print_function
from datetime import datetime
from . import models
from six import text_type
from django.apps.registry import apps
from xyz_util.datautils import access
from django.contrib.contenttypes.models import ContentType
import logging

log = logging.getLogger('django')

SUBJECT_REGISTER = {}


def subject_add_item_receiver(sender, **kwargs):
    for sid in SUBJECT_REGISTER[sender]:
        try:
            subject = models.Subject.objects.get(id=sid)
            model = kwargs['instance']
            created = kwargs['created']
            function = subject.function
            if function.get('created') and not created:
                break
            subject_add_item(subject, model)
        except:
            import traceback
            log.error('points subject_add_item_receiver sid: %s error: %s', sid, traceback.format_exc())


def subject_add_item(subject, model):
    function = subject.function
    value = access(model, function['value'])

    project = subject.project
    now = datetime.now()
    session = project.sessions.filter(begin_time__lt=now, end_time__gt=now, is_active=True).order_by('-number').first()
    if not session:
        return
    filter = function.get('filter')
    if filter:
        for k, v in filter.items():
            if access(model, k) != v:
                return
    # print(project, session, subject, model, value)
    user = model.user
    category = None
    if 'category' in function:
        cn = access(model, function.get('category'))
        # print(cn)
        category, created = project.categories.get_or_create(name=cn)
    point, created = session.points.get_or_create(
        category=category,
        user=user,
        defaults=dict(value=value)
    )
    item, created = point.items.update_or_create(
        user=user,
        owner_type=ContentType.objects.get_for_model(model),
        owner_id=model.id,
        defaults=dict(
            owner_name=text_type(model),
            value=value
        )
    )


def create_points_receiver():
    from django.db.models.signals import post_save
    try:
        for s in models.Subject.objects.filter(is_active=True):
            fd = s.function
            model = apps.get_model('%s.%s' % (fd['app'], fd['model']))
            sid = s.id
            ms = SUBJECT_REGISTER.setdefault(model, [])
            if not ms:
                post_save.connect(subject_add_item_receiver, sender=model)
            ms.append(sid)
            # print ('connect', s, model)
    except:
        import traceback
        log.error('create_points_receiver error: %s', traceback.format_exc())


def rank_users(us, page_size=3):
    from django.contrib.auth.models import User
    scores = sorted([(score, uid) for uid, score in us.items()], reverse=True)[:page_size]
    ranks = []
    for score, uid in scores:
        user = User.objects.filter(id=uid).first()
        if not user:
            continue
        ranks.append(dict(name=user.get_full_name(), id=user.id, score=score, avatar= access(user, 'as_wechat_user.headimgurl')))
    return ranks

def render_daily_ranks(record, my_uid):
    return dict(name='日榜', mine=dict(score=record.get(str(my_uid))), ranks=rank_users(record, page_size=1000))

def render_category_ranks(ranks, my_uid, **kwargs):
    rs = []
    for k, v in ranks.items():
        ct_id, id = k.split(':')
        ct = ContentType.objects.get_for_id(ct_id)
        c = ct.get_object_for_this_type(pk=id)
        urs = v['user']
        rs.append(dict(name=text_type(c), mine=dict(score=urs.get(str(my_uid))), ranks=rank_users(urs, **kwargs)))
    return rs

def project_create_categories(project, categories):
    ns = project.categories.all().values_list('name', flat=True)
    for c in categories:
        n = c.get('name')
        if n not in ns:
            category, created = project.categories.get_or_create(name=n, defaults=dict(is_active=True))
            print('created', category, created)

def project_exclude_categories(project, categories):
    exclude_list =list(project.categories.filter(is_active=False).values_list('name', flat=True))
    return [c for c in categories if c.get('name') not in exclude_list]