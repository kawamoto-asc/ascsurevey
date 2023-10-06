from django.urls import path, include

from surveys import views
from surveys.views import top

urlpatterns = [
    path('', top, name='top'),
    path('input/<str:pshname>', views.InputListView.as_view(), name='input-list'),
    #path('edit1/<int:pnendo>/<int:psheetid>', views.InputEdit1View.as_view(), name='input-edit1'),
    path('edit2/<int:pnendo>/<int:psheetid>', views.InputEdit2View.as_view(), name='input-edit2'),
]
