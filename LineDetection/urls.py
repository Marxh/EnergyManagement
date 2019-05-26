from django.urls import path, re_path

from . import views

app_name = 'LineDetection'
urlpatterns = [
    path(r'', views.login_index, name='login_index'),
    path('index/<int:character>/', views.index, name='index'),
    path('monitor_index/<int:character>/', views.monitor_index, name='monitor_index'),
    path('report/<int:character>/', views.report, name='report'),
    path('monitor/<int:facility_id>/<int:character>/', views.monitor, name='monitor'),
    path('exclude_anomaly/<int:facility_id>/<int:character>/', views.exclude_anomaly, name='exclude_anomaly'),
    path('statistics/<int:facility_id>/<int:character>/',views.statistics, name='statistics'),
    path('cluster/<int:facility_id>/<int:character>/',views.cluster, name='cluster'),
    path('cluster_superuser/<int:facility_id>/<int:character>/',views.cluster_superuser, name='cluster_superuser'),
    path('calender/<int:facility_id>/<int:character>/',views.calender, name='calender'),
    path('setcluster/<int:facility_id>/<int:cluster_number>/<int:character>/',views.setcluster, name='setcluster'),
    path('login_action',views.login_action, name='login_action'),
#    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#    path('<int:question_id>/vote/', views.vote, name='vote'),
]