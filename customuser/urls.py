from django.urls import path, include

from customuser import views
from customuser.views import getBusyoList, getLocationList, getPostList

urlpatterns = [
    path('', views.CUsersListView.as_view(), name='list-cusers'),
    path('get-busyolist', getBusyoList, name='get-busyolist'),
    path('get-locationlist', getLocationList, name='get-locationlist'),
    path('get-postlist', getPostList, name='get-postlist'),
]