from django.urls import path, include

from sheets import views
#from sheets.views import getBusyoList, getLocationList, getPostList

urlpatterns = [
    path('', views.SheetsListView.as_view(), name='sheets-list'),
    path('new/<int:pnendo>', views.SheetsCreateView.as_view(), name='sheet-new'),
    #path('edit/<int:pnendo>/<int:id>', views.SheetsEditView.as_view(), name='sheet-edit'),
    #path('excelout', views.sheets_downloadexcel, name='sheet-download'),
    #path('excelin', views.SheetsExcelUploadView.as_view(), name='sheet-upload'),
]
