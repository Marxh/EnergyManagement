from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from itertools import chain
from .models import Facility, Energy, Anomaly,  season_goal, production_amount
from .utils import *
import pandas as pd
import json
import numpy as np
import calendar
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'LineDetection/yxjc.html'
    context_object_name = 'facility_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        #acility_list = Facility.objects.all()
        #anomaly_list = Anomaly.objects.all()
        sql = open('SQL/index.sql', 'r')
        sql_query = sql.read()
        sql_query = sql_query.replace('\n',' ')
        queryset = Anomaly.objects.raw(sql_query)
        return queryset

def monitor(request, facility_id):
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
            'latest_energy': round(five_day_energy_group['energy'].tolist()[-1],0), 'energy_limit': energy_limit})

def statistics(request, facility_id):
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
                  'left_amount':left_amount}) 

def cluster(request, facility_id):
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
    return render(request, 'LineDetection/cluster.html', {'json_cluster':json.dumps(json_cluster),'facility_id':facility_id}) 