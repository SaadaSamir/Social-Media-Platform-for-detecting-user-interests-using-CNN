from django.contrib import admin
from .models import *
from django.shortcuts import render
from django.urls import path


admin.site.register(User)
#admin.site.register(Interest)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Follower)



