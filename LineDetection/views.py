from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from itertools import chain
from .models import Facility, Energy, Anomaly, Cluster, season_goal, production_amount, Tag, Article
from .utils import *
import pandas as pd
import json
import numpy as np
import calendar
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
import datetime

# Create your views here.

def login_index(request):
    return render(request, 'LineDetection/login.html')

def login_action(request):
    character_num = -1
    if request.method=="GET":
        account=request.GET.get('account',None)
        password=request.GET.get('password',None)
        character=request.GET.get('character',None)
        if(character=='能耗分析人员'):
            character_num = 0
        elif(character=='普通用户'):
            character_num = 1
        else:
            character_num = 2
    return HttpResponseRedirect(reverse('LineDetection:index', args=(character_num,)))

def index(request,character):
    return render(request, 'LineDetection/index.html', {'character': character})

def monitor_index(request,character):
    sql = open('SQL/index.sql', 'r')
    sql_query = sql.read()
    sql_query = sql_query.replace('\n',' ')
    queryset = Anomaly.objects.raw(sql_query)
    return render(request, 'LineDetection/yxjc.html', {'facility_list': queryset,'character':character})

def report(request,character):
    return render(request, 'LineDetection/report.html',{'character':character})

def monitor(request, facility_id, character):
    sql = open('SQL/monitor.sql', 'r')
    sql_query = sql.read()
    sql_query = sql_query.replace('\n',' ').replace('###', str(facility_id))
    queryset = Anomaly.objects.raw(sql_query)[:10]

    five_day_energy = Energy.objects.filter(facility_id = facility_id)
    five_day_energy_df = five_day_energy.to_dataframe()
    #five_day_energy_df.to_csv('test.csv', index=False)
    five_day_energy_df['date'] = pd.to_datetime(five_day_energy_df.energy_date,format="%Y/%m/%d")
    five_day_energy_df['hour'] = five_day_energy_df['date'].dt.hour
    aggregation = {'hour':'first','energy':'sum'}
    five_day_energy_group = five_day_energy_df.groupby('hour').agg(aggregation)
    five_day_energy_group = five_day_energy_group.sort_values("hour",inplace=False)
    #five_day_energy_group.to_csv('test.csv')
    five_day_energy_group = five_day_energy_group.reset_index(drop=True)
    five_day_energy_list = [{
        'hour':five_day_energy_group['hour'].tolist()[-5:],
        'energy':five_day_energy_group['energy'].tolist()[-5:]
    }]
    five_day_energy_json = json.dumps(five_day_energy_list)

    energy_limit = Facility.objects.filter(id = facility_id)
    energy_limit = energy_limit.to_dataframe()['energy_total'].tolist()[0]
    return render(request, 'LineDetection/monitor.html', \
        {'energy_list': queryset, 'five_day_energy': five_day_energy_json, 'facility_id': facility_id, \
            'latest_energy': round(five_day_energy_group['energy'].tolist()[-1],0), 'energy_limit': energy_limit,'character':character})

def statistics(request, facility_id,character):
    production = production_amount.objects.all().to_dataframe()
    production['season_id'] = production['season'].str[-2]
    production['season_id'] = production['season_id'].astype(int)
    #production.to_csv('test.csv')
    season = season_goal.objects.all().to_dataframe()
    #season.to_csv('test2.csv')
    prod = pd.merge(production, season, how = 'left', left_on = 'season_id', right_on = 'id')
    prod = prod.sort_index(by='production_date').reset_index(drop=True)
    prod['date'] = pd.to_datetime(prod.production_date,format="%Y/%m/%d")
    prod['day'] = prod['date'].dt.day
    prod['month'] = prod['date'].dt.month
    prod['year'] = prod['date'].dt.year
    total_time = calendar.monthrange(prod['year'].tolist()[-1], prod['month'].tolist()[-1])[1]
    passed_time = prod['day'].tolist()[-1]
    time_json = [{
        'total':total_time,
        'passed':passed_time
    }]

    aggregation_amount = {'goal':'first','amount':'sum'}
    prod_amount = prod.groupby('season_id').agg(aggregation_amount)
    goal = prod_amount['goal'].tolist()[0]
    done_amount = prod_amount['amount'].tolist()[0]
    left_amount = goal - done_amount
    prod_json = [{
        'total':goal,
        'done':done_amount
    }]

    anomaly = Anomaly.objects.filter(facility_id = facility_id)
    anomaly_df = anomaly.to_dataframe()
    anomaly_df['date'] = pd.to_datetime(anomaly_df.anomaly_date,format="%YYYY/%MM/%DD")
    anomaly_df = anomaly_df.sort_values("date",inplace=False).reset_index(drop=True)
    anomaly_df['compare_date'] = anomaly_df.apply(lambda df: get_compare_date(df), axis = 1)


    anomaly_df['1_flag'] = anomaly_df.apply(lambda df: get_type_num(df, str(1)), axis = 1)
    anomaly_df['2_flag'] = anomaly_df.apply(lambda df: get_type_num(df, str(2)), axis = 1)
    anomaly_df['3_flag'] = anomaly_df.apply(lambda df: get_type_num(df, str(3)), axis = 1)
    anomaly_df['4_flag'] = anomaly_df.apply(lambda df: get_type_num(df, str(4)), axis = 1)

    anomaly_pivot = pd.pivot_table(anomaly_df,index=["compare_date"],values=["1_flag","2_flag","3_flag","4_flag"],\
                                    aggfunc=np.count_nonzero)
    anomaly_bar_json = [{
        'compare_date':list(anomaly_pivot.index),
        'data_1':anomaly_pivot['1_flag'].tolist(),
        'data_2':anomaly_pivot['2_flag'].tolist(),
        'data_3':anomaly_pivot['3_flag'].tolist(),
        'data_4':anomaly_pivot['4_flag'].tolist()
    }]

    anomaly_pie_json = [{
        'data_1':np.sum(anomaly_pivot['1_flag'].tolist()),
        'data_2':np.sum(anomaly_pivot['2_flag'].tolist()),
        'data_3':np.sum(anomaly_pivot['3_flag'].tolist()),
        'data_4':np.sum(anomaly_pivot['4_flag'].tolist())
    }]
    return render(request, 'LineDetection/statistics.html', {'prod':prod_json,'time': time_json,'facility_id': facility_id, 'anomaly_bar': anomaly_bar_json,\
                  'anomaly_pie': anomaly_pie_json,'goal':goal, 'done_amount':done_amount, 'total_time':total_time,'passed_time':passed_time,\
                  'left_amount':left_amount,'character':character}) 

def cluster(request, facility_id,character):
    #total_energy = Energy.objects.filter(facility_id = facility_id)
    #total_energy = Energy.objects.values('energy','energy_date').all()
    #total_energy = total_energy.to_dataframe()
    total_energy = pd.read_csv('total_energy.csv')
    total_energy_list = total_energy['energy'].tolist()
    total_date_list = total_energy['energy_date'].tolist()
    kmeans_energy = []
    kmeans_date = []
    for i in range(200):
        temp_list = total_energy_list[1000*i:1000*i+1000]
        kmeans_energy.append(temp_list)
    for i in range(200):
        temp_list = [0,0]
        temp_list[0] = total_date_list[1000*i]
        temp_list[1] = total_date_list[1000*i+1000-1]
        kmeans_date.append(temp_list)
    score = 0
    cluster = 2
    for i in range(2,20):
        k_means = KMeans(n_clusters=i, random_state=10)
        y_predict = k_means.fit_predict(kmeans_energy)
        s = silhouette_score(kmeans_energy, y_predict)
        if(score<s):
            score = s
            cluster = i
    k_means = KMeans(n_clusters=cluster, random_state=10)
    y_predict = k_means.fit_predict(kmeans_energy)
    center=k_means.cluster_centers_
    labels=k_means.labels_
    json_cluster = []
    for i in range(cluster):
        temp_cluster = {}
        cluster_name = 'cluster_' + str(i)
        temp_cluster['name'] = cluster_name
        temp_cluster['xdata'] = [i for i in range(len(list(center[i])))]
        temp_cluster['ydata'] = list(center[i])
        temp_cluster['type'] = 'line'
        json_cluster.append(temp_cluster)
    
    cluster_info = Cluster.objects.all()
    return render(request, 'LineDetection/cluster.html', {'json_cluster':json.dumps(json_cluster),'facility_id':facility_id,\
                                                           'cluster_info':cluster_info,'character':character})

def calender(request, facility_id,character):
    total_energy = pd.read_csv('total_energy.csv')
    total_energy['date'] = pd.to_datetime(total_energy.energy_date,format="%Y/%m/%d")
    total_energy['day'] = total_energy['date'].dt.day
    total_energy['month'] = total_energy['date'].dt.month
    total_energy['year'] = total_energy['date'].dt.year
    total_energy['day'] = total_energy['day'].astype(str)
    total_energy['month'] = total_energy['month'].astype(str)
    total_energy['year'] = total_energy['year'].astype(str)
    total_energy['count_day'] = total_energy['year']+"-"+total_energy['month']+"-"+total_energy['day']
    aggregation = {'count_day':'first','energy':'sum'}
    total_energy_group = total_energy.groupby('count_day').agg(aggregation)
    total_energy_group = total_energy_group.sort_values("energy",inplace=False)
    total_energy_group = total_energy_group.reset_index(drop=True)
    
    '''
    # five top energy
    five_top_energy_json = [{
        'row_1_date':total_energy_group.iloc[0].tolist()[0],
        'row_1_energy':total_energy_group.iloc[0][1],
        'row_2_date':total_energy_group.iloc[1][0],
        'row_2_energy':total_energy_group.iloc[1][1],
        'row_3_date':total_energy_group.iloc[2][0],
        'row_3_energy':total_energy_group.iloc[2][1],
        'row_4_date':total_energy_group.iloc[3][0],
        'row_4_energy':total_energy_group.iloc[3][1],
        'row_5_date':total_energy_group.iloc[4][0],
        'row_5_energy':total_energy_group.iloc[4][1]
    }]
    '''
    
    max_energy = total_energy_group.iloc[0].tolist()
    min_energy = total_energy_group.iloc[-1].tolist()
    
    '''
    # get day of a date
    begin_date = datetime.date(total_energy['year'].iloc[0], total_energy['month'].iloc[0], total_energy['day'].iloc[0])
    begin_day = begin_date - datetime.date(begin_date.year - 1, 12, 31)
    energy_list = [0] * 365
    temp_day = begin_day.days
    for i in range(len(total_energy_group)):
        energy_list[temp_day-1] = total_energy_group['energy'].iloc[i]
        temp_day = temp_day + 1
    '''
    
    return render(request, 'LineDetection/calender.html', {'facility_id':facility_id,'character':character, 'five_top_energy':five_top_energy_json,\
        'max_energy':round(max_energy[1],2),'max_energy_date':max_energy[0],'min_energy':round(min_energy[1],2),'min_energy_date':min_energy[0]})

def cluster_superuser(request, facility_id,character):
    total_energy = pd.read_csv('total_energy.csv')
    total_energy_list = total_energy['energy'].tolist()
    total_date_list = total_energy['energy_date'].tolist()
    kmeans_energy = []
    kmeans_date = []
    for i in range(200):
        temp_list = total_energy_list[1000*i:1000*i+1000]
        kmeans_energy.append(temp_list)
    for i in range(200):
        temp_list = [0,0]
        temp_list[0] = total_date_list[1000*i]
        temp_list[1] = total_date_list[1000*i+1000-1]
        kmeans_date.append(temp_list)
    score = 0
    cluster = 2
    score_list = {}
    score_list['xdata'] = [i for i in range(2,20)]
    score_list['ydata'] = []
    for i in range(2,20):
        k_means = KMeans(n_clusters=i, random_state=10)
        y_predict = k_means.fit_predict(kmeans_energy)
        s = silhouette_score(kmeans_energy, y_predict)
        score_list['ydata'].append(s)
        if(score<s):
            score = s
            cluster = i
    k_means = KMeans(n_clusters=cluster, random_state=10)
    y_predict = k_means.fit_predict(kmeans_energy)
    center=k_means.cluster_centers_
    labels=k_means.labels_
    json_cluster = []
    for i in range(cluster):
        temp_cluster = {}
        cluster_name = 'cluster_' + str(i)
        temp_cluster['name'] = cluster_name
        temp_cluster['xdata'] = [i for i in range(len(list(center[i])))]
        temp_cluster['ydata'] = list(center[i])
        temp_cluster['type'] = 'line'
        json_cluster.append(temp_cluster)
    
    cluster_info = Cluster.objects.all()

    sql = open('SQL/article.sql', 'r')
    sql_query = sql.read()
    sql_query = sql_query.replace('\n',' ')
    sql_query = sql_query.replace('{% facility_id %}',str(facility_id))
    article_with_tag = Article.objects.raw(sql_query)
    if(len(article_with_tag)>5):
        article_with_tag = article_with_tag[:5]
    return render(request, 'LineDetection/cluster_superuser.html', {'json_cluster':json.dumps(json_cluster),'facility_id':facility_id,\
                                                           'cluster_info':cluster_info,'score_list':score_list,'cluster_number':len(center),'character':character,\
                                                               'article_with_tag':article_with_tag})

def setcluster(request, facility_id, cluster_number,character):
    comments_list = []
    if request.method=="POST":
        for i in range(1, cluster_number+1):
            input_name = 'anomaly_' + str(i)
            anomaly_comment=request.POST.get(input_name,None)
            if(anomaly_comment):
                cluster_obj = Cluster.objects.filter(cluster_id = i).update(anomaly_condition = 1, anomaly_comments = anomaly_comment)
            else:
                cluster_obj = Cluster.objects.filter(cluster_id = i).update(anomaly_condition = 0, anomaly_comments = '')
    return HttpResponseRedirect(reverse('LineDetection:cluster', args=(facility_id,character,)))

def cluster_superuser_view_article(request,article_id):
    url_view_article = 'http://127.0.0.1:8000/admin/LineDetection/article/{% article_id %}/change/'
    url_view_article = url_view_article.replace('{% article_id %}', str(article_id))
    return HttpResponseRedirect(url_view_article)

def exclude_anomaly(request, facility_id,character):
    #total_energy = Energy.objects.filter(facility_id = facility_id)
    #total_energy = Energy.objects.values('energy','energy_date').all()
    #total_energy = total_energy.to_dataframe()
    total_energy = pd.read_csv('total_energy.csv')
    total_energy_list = total_energy['energy'].tolist()
    total_date_list = total_energy['energy_date'].tolist()
    kmeans_energy = []
    kmeans_date = []
    for i in range(200):
        temp_list = total_energy_list[1000*i:1000*i+1000]
        kmeans_energy.append(temp_list)
    for i in range(200):
        temp_list = [0,0]
        temp_list[0] = total_date_list[1000*i]
        temp_list[1] = total_date_list[1000*i+1000-1]
        kmeans_date.append(temp_list)
    score = 0
    cluster = 2
    for i in range(2,20):
        k_means = KMeans(n_clusters=i, random_state=10)
        y_predict = k_means.fit_predict(kmeans_energy)
        s = silhouette_score(kmeans_energy, y_predict)
        if(score<s):
            score = s
            cluster = i
    k_means = KMeans(n_clusters=cluster, random_state=10)
    y_predict = k_means.fit_predict(kmeans_energy)
    center=k_means.cluster_centers_
    labels=k_means.labels_
    json_cluster = []
    for i in range(cluster):
        temp_cluster = {}
        cluster_name = 'cluster_' + str(i)
        temp_cluster['name'] = cluster_name
        temp_cluster['xdata'] = [i for i in range(len(list(center[i])))]
        temp_cluster['ydata'] = list(center[i])
        temp_cluster['type'] = 'line'
        json_cluster.append(temp_cluster)
    
    cluster_info = Cluster.objects.all()
    
    anomaly = Anomaly.objects.filter(facility_id = facility_id, anomaly_solve = 0)

    return render(request, 'LineDetection/exclude_anomaly.html', {'json_cluster':json.dumps(json_cluster),'facility_id':facility_id,\
                                                           'cluster_info':cluster_info, 'anomaly_list':anomaly,'character':character})

def fix_anomaly_action(request, facility_id,anomaly_id,character):
    if request.method=="POST":
        cluster_obj = Anomaly.objects.filter(id = anomaly_id).update(anomaly_solve = 1)
    return HttpResponseRedirect('http://127.0.0.1:8000/admin/LineDetection/article/add/')