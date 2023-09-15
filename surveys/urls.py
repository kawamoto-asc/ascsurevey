from django.urls import path, include

from surveys.views import top

urlpatterns = [
    path('', top, name='top'),
]
