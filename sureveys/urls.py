from django.urls import path, include
from . import views

from sureveys.views import top, getCustomerPostList

urlpatterns = [
    path('', top, name='top'),
    path('customusers/', views.CUsersListView.as_view(), name='list-cusers'),
    path('get-customerpostlist', getCustomerPostList, name='get-customerpostlist'),
]
