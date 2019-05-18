from django.urls import path, re_path

from . import views

app_name = 'LineDetection'
urlpatterns = [
    path(r'', views.IndexView.as_view(), name='index'),
    path('monitor_index/', views.monitor_index, name='monitor_index'),
    path('report/', views.report, name='report'),
    path('monitor/<int:facility_id>/', views.monitor, name='monitor'),
    path('statistics/<int:facility_id>/',views.statistics, name='statistics'),
    path('cluster/<int:facility_id>/',views.cluster, name='cluster'),
    path('cluster_superuser/<int:facility_id>/',views.cluster_superuser, name='cluster_superuser'),
    path('calender/<int:facility_id>/',views.calender, name='calender'),
#    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#    path('<int:question_id>/vote/', views.vote, name='vote'),
]