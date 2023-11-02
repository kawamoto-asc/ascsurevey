from django.urls import path, include

from summarize import views
#from summarize.views import top

urlpatterns = [
    #path('excelout1', views.dl_score_excel1, name='score-download1'),
    path('excelout2', views.dl_score_excel2, name='score-download2'),
    path('<str:pshname>', views.SummarizeListView.as_view(), name='summary-list'),
]
