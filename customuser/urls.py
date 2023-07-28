from django.urls import path, include

from customuser import views
from customuser.views import getBusyoList, getLocationList, getPostList

urlpatterns = [
    path('', views.CUsersListView.as_view(), name='cusers-list'),
    path('get-busyolist', getBusyoList, name='get-busyolist'),
    path('get-locationlist', getLocationList, name='get-locationlist'),
    path('get-postlist', getPostList, name='get-postlist'),
    path('new/<int:pnendo>', views.CUsersCreateView.as_view(), name='cusers-new'),
]
