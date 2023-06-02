from django.urls import path, include

from sureveys.views import top

urlpatterns = [
    path('', top, name='top'),
]
