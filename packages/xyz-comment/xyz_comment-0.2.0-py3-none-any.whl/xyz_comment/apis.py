# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from six import text_type
from xyz_restful.mixins import UserApiMixin
from xyz_util.statutils import do_rest_stat_action

from . import serializers, models, stats
from rest_framework import viewsets, exceptions, response, decorators, permissions
from xyz_restful.decorators import register
from xyz_util.statutils import smart_rest_stat_action
from copy import deepcopy
__author__ = 'denishuang'


@register()
class CommentViewSet(UserApiMixin, viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = models.Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = {
        'content_type': ['exact'],
        'object_id': ['exact'],
        'user': ['exact'],
        'create_time': ['range'],
        'reply_count': ['gte', 'lte']
    }
    search_fields = ['object_name']

    def filter_queryset(self, queryset):
        qset = super(CommentViewSet, self).filter_queryset(queryset)
        ct = self.request.query_params.get('content_type')
        if not ct and self.action == 'list':
            return qset.exclude(content_type=ContentType.objects.get_for_model(models.Comment))
        return qset

    @decorators.action(['GET'], detail=True)
    def replies(self, request, pk):
        c = self.get_object()
        page = self.paginate_queryset(c.replies)
        serializer = serializers.CommentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

@register()
class FavoriteViewSet(UserApiMixin, viewsets.ModelViewSet):
    serializer_class = serializers.FavoriteSerializer
    queryset = models.Favorite.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = {
        'content_type': ['exact'],
        'object_id': ['exact', 'in'],
        'user': ['exact'],
        'create_time': ['range']
    }

    @decorators.action(['GET', 'POST'], detail=False)
    def record(self, request):
        qs = request.query_params
        if not qs.get('content_type'):
            raise exceptions.ValidationError('content_type should not be empty.')
        if not qs.get('object_id'):
            raise exceptions.ValidationError('object_id should not be empty.')
        qd = dict(user=request.user, content_type=qs.get('content_type'), object_id=qs.get('object_id'))
        f = self.get_queryset().filter(**qd).first()
        if request.method == 'GET':
            if not f:
                return response.Response(qs)
        elif request.method == 'POST':
            if not f:
                qd['content_type'] = ContentType.objects.get(id=qd['content_type'])
                f = models.Favorite(notes={}, **qd)
            d = request.data
            f.notes[text_type(d['anchor'])] = d
            f.save()
        return response.Response(self.get_serializer_class()(f).data)


    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_favorite)


@register()
class RatingViewSet(UserApiMixin, viewsets.ModelViewSet):
    serializer_class = serializers.RatingSerializer
    queryset = models.Rating.objects.all()
    filterset_fields = {
        'content_type__app_label': ['exact'],
        'content_type__model': ['exact'],
        'content_type': ['exact'],
        'object_id': ['exact'],
        'create_time': ['range'],
        'user': ['exact']
    }
    search_fields = ['object_name']
    ordering_fields = ['stars']

    @decorators.action(['GET', 'POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def record(self, request):
        qs = request.query_params
        qp = request.data
        if not qs.get('content_type'):
            raise exceptions.ValidationError('content_type should not be empty.')
        if not qs.get('object_id'):
            raise exceptions.ValidationError('object_id should not be empty.')
        qd = dict(user=request.user, content_type=qs.get('content_type'), object_id=qs.get('object_id'))
        r = self.get_queryset().filter(**qd).first()
        if not r:
            if request.method == 'POST':
                qd['content_type'] = ContentType.objects.get(id=qd['content_type'])
                qd['stars'] = qp['stars']
                qd['content'] = qp.get('content', '')
                r = models.Rating(**qd)
                r.save()
                data = self.get_serializer_class()(r).data
            else:
                data = deepcopy(qs)
        else:
            if request.method == 'POST':
                r.stars = qp['stars']
                r.content = qp.get('content', '')
                r.save()
            data = self.get_serializer_class()(r).data
        sumary = models.RatingSumary.objects.filter(content_type_id=qd['content_type'], object_id=qd['object_id']).first()
        if sumary:
            data['sumary'] = serializers.RatingSumarySerializer(sumary).data
        return response.Response(data)

@register()
class RatingSumaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.RatingSumarySerializer
    queryset = models.RatingSumary.objects.all()
    filterset_fields = {
        'content_type': ['exact'],
        'object_id': ['exact', 'in']
    }

    @decorators.action(['get'], detail=False)
    def smart_stat(self, request):
        return smart_rest_stat_action(self)
    #
    #
    # @decorators.action(['GET'], detail=False)
    # def record(self, request):
    #     qs = request.query_params
    #     if not qs.get('content_type'):
    #         raise exceptions.ValidationError('content_type should not be empty.')
    #     if not qs.get('object_id'):
    #         raise exceptions.ValidationError('object_id should not be empty.')
    #     qd = dict(content_type=qs.get('content_type'), object_id=qs.get('object_id'))
    #     r = self.get_queryset().filter(**qd).first()
    #     if not r:
    #         return response.Response(qs)
    #     data = self.get_serializer_class()(r).data
    #     qd['user'] = request.user
    #     mr = models.Rating.objects.filter(qd).first()
    #     if mr:
    #         data['mine'] =serializers.RatingSerializer(mr).data
    #     return response.Response(data)