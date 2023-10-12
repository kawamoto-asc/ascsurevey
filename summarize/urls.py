from django.urls import path, include

from summarize import views
#from summarize.views import top

urlpatterns = [
    path('<str:pshname>', views.SummarizeListView.as_view(), name='summary-list'),
]
