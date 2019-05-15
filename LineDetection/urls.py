from django.urls import path

from . import views

app_name = 'LineDetection'

urlpatterns = [
    path(r'', views.IndexView.as_view(), name='yxjc'),
    path('<int:facility_id>/', views.monitor, name='monitor'),
    path('<int:facility_id>/statistics',views.statistics, name='statistics'),
#    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#    path('<int:question_id>/vote/', views.vote, name='vote'),
]