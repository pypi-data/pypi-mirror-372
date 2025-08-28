# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from . import models

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ('object_name', )
    list_display = ("create_time", "user", "content_type", "object_name")
    readonly_fields = ("create_time", 'user')

@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    search_fields = ('object_name', )
    list_display = ("create_time", "user", "content_type", "object_name")
    readonly_fields = ("create_time", 'user')

@admin.register(models.Rating)
class RatingAdmin(admin.ModelAdmin):
    search_fields = ('object_name', )
    list_display = ("update_time", "user", "content_type", "object_name", 'stars', 'content')
    readonly_fields = ("create_time", "update_time", 'user')
    raw_id_fields = ('content_type',)

@admin.register(models.RatingSumary)
class RatingSumaryAdmin(admin.ModelAdmin):
    search_fields = ('object_name', )
    list_display = ("update_time", "content_type", "object_name", "user_count", 'score')
    readonly_fields = ("create_time", "update_time")
    raw_id_fields = ('content_type',)
