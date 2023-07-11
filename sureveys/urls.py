from django.urls import path, include
from . import views

from sureveys.views import *

urlpatterns = [
    path('', top, name='top'),
    path('customusers/', views.CUsersListView.as_view(), name='list-cusers'),
    path('get-busyolist', getBusyoList, name='get-busyolist'),
    path('get-locationlist', getLocationList, name='get-locationlist'),
    path('get-postlist', getPostList, name='get-postlist'),
]
