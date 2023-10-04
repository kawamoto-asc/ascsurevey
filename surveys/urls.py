from django.urls import path, include

from surveys import views
from surveys.views import top

urlpatterns = [
    path('', top, name='top'),
    path('input/<str:psheetid>', views.InputListView.as_view(), name='input-list'),
]
