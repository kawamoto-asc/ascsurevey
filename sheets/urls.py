from django.urls import path, include

from sheets import views
#from sheets.views import getBusyoList, getLocationList, getPostList

urlpatterns = [
    path('', views.SheetsListView.as_view(), name='sheets-list'),
    #path('get-busyolist', getBusyoList, name='get-busyolist'),
    #path('get-locationlist', getLocationList, name='get-locationlist'),
    #path('get-postlist', getPostList, name='get-postlist'),
    #path('new/<int:pnendo>', views.CUsersCreateView.as_view(), name='cusers-new'),
    #path('edit/<int:pnendo>/<int:id>', views.CUsersEditView.as_view(), name='cusers-edit'),
    #path('excelout', views.download_excel, name='cuser-download'),
    #path('excelin', views.FileUploadView.as_view(), name='cuser-upload'),
]
