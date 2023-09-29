from django.urls import path, include

from sheets import views
#from sheets.views import getBusyoList, getLocationList, getPostList

urlpatterns = [
    path('', views.SheetsListView.as_view(), name='sheets-list'),
    path('new/<int:pnendo>/<str:pflg>', views.SheetsCreateView.as_view(), name='sheet-new'),
    path('edit/<int:pnendo>/<int:id>/<str:pflg>', views.SheetsEditView.as_view(), name='sheet-edit'),
    path('excelout/<int:pnendo>/<int:id>', views.SheetsDownloadExcel, name='sheet-download'),
    path('excelin', views.SheetFileUploadView.as_view(), name='sheet-upload'),
]
