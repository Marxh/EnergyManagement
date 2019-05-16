from django.urls import path, re_path

from . import views

app_name = 'LineDetection'
urlpatterns = [
    path(r'', views.IndexView.as_view(), name='yxjc'),
    path('monitor/<int:facility_id>/', views.monitor, name='monitor'),
    path('statistics/<int:facility_id>/',views.statistics, name='statistics'),
    path('cluster/<int:facility_id>/',views.cluster, name='cluster'),
#    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#    path('<int:question_id>/vote/', views.vote, name='vote'),
]