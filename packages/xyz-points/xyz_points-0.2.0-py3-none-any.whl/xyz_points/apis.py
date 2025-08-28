# -*- coding:utf-8 -*-
from __future__ import division, unicode_literals
from xyz_restful.mixins import UserApiMixin
from . import helper
from rest_framework.response import Response

__author__ = 'denishuang'

from . import models, serializers
from rest_framework import viewsets, decorators, status
from xyz_restful.decorators import register, register_raw


@register()
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filterset_fields = {
        'id': ['in', 'exact'],
    }
    search_fields = ('name',)

    @decorators.action(['GET'], detail=False)
    def current(self, request):
        project = self.filter_queryset(self.get_queryset()).first()
        if not project:
            return Response(dict())
        from datetime import datetime
        now = datetime.now()
        session = project.sessions.filter(begin_time__lt=now).last()
        qset = project.categories.filter(is_active=True)
        return Response(dict(
            project=serializers.ProjectSerializer(project).data,
            session=serializers.SessionSerializer(session).data,
            categories=serializers.CategorySerializer(qset, many=True).data,
            myCategories=list(
                models.Point.objects.filter(user=request.user, session=session).values_list('category_id', flat=True))
        ))

    @decorators.action(['GET'], detail=False)
    def ranks(self, request):
        project = self.filter_queryset(self.get_queryset()).first()
        if not project:
            return Response(dict())
        from datetime import datetime
        now = datetime.now()
        session = project.sessions.filter(begin_time__lt=now).last()
        if not session:
            return Response(dict())
        from .stores import PointsSession, PointsSessionDaily
        rtype = request.query_params.get('type')

        categories = []
        if rtype == 'daily':
            sd = PointsSessionDaily().collection.find_one({'id': session.id, 'date': now.isoformat()[:10]})
            if sd:
                categories = [helper.render_daily_ranks(sd.get('user', []), my_uid=request.user.id)]
        else:
            sd = PointsSession().collection.find_one({'id': session.id})
            if sd:
                categories = helper.render_category_ranks(sd['category'], my_uid=request.user.id, page_size=int(request.GET.get('page_size', 3)))
                helper.project_create_categories(project, categories)

        categories = helper.project_exclude_categories(project, categories)
        return Response(dict(
            project=serializers.ProjectSerializer(project).data,
            session=serializers.SessionSerializer(session).data,
            categories=categories
        ))


@register()
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    filterset_fields = {
        'id': ['in', 'exact'],
    }
    search_fields = ('name',)


@register()
class SessionViewSet(viewsets.ModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer
    filterset_fields = {
        'id': ['in', 'exact'],
        'project': ['exact'],
        'is_active': ['exact'],
        'begin_time': ['range'],
    }
    search_fields = ('name',)


@register()
class CategoryViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filterset_fields = {
        'id': ['in', 'exact'],
        'project': ['exact'],
        'name': ['exact']
    }
    search_fields = ('name',)

    @decorators.action(['GET'], detail=True)
    def rank(self, request, pk):
        category = self.get_object()
        session = category.project.sessions.last()
        qset = category.points.filter(session=session).order_by('-value')
        points = self.paginate_queryset(qset)
        mine = qset.filter(user=request.user).first()
        return Response(dict(
            category=serializers.CategorySerializer(category).data,
            session=serializers.SessionSerializer(session).data,
            points=serializers.PointSerializer(points, many=True).data,
            mine=serializers.PointSerializer(mine).data if mine else None,
        ))


@register()
class PointViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Point.objects.all()
    serializer_class = serializers.PointSerializer
    filterset_fields = {
        'id': ['in', 'exact'],
        'user': ['in'],
        'session': ['exact'],
        'project': ['exact'],
        'category': ['exact']
    }
    ordering_fields = ('category', 'session', 'project', 'value', 'update_time')


@register()
class ItemViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemSerializer
    filterset_fields = {
        'id': ['in', 'exact'],
        'user': ['in']
    }
