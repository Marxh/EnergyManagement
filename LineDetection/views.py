from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from itertools import chain
from .models import Facility, Energy, Anomaly, season_goal, production_amount
import pandas as pd
import json
import numpy as np
import calendar

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
    anomaly = Anomaly.objects.filter(facility_id = facility_id)
    anomaly_df = anomaly.to_dataframe()

    sql = open('SQL/statistic_production.sql', 'r')
    sql_query = sql.read()
    sql_query = sql_query.replace('\n',' ')

    prod = season_goal.objects.raw(sql_query)
    prod = prod.to_dataframe()
    prod = prod.sort_index(by='production_date').reset_index(drop=True)
    prod['date'] = pd.to_datetime(prod.production_date,format="%Y/%m/%d")
    prod['day'] = prod['date'].dt.day
    prod['month'] = prod['date'].dt.month
    prod['year'] = prod['date'].dt.year
    time_json = [{
        'total':calendar.monthrange(prod['year'].tolist()[-1], prod['month'].tolist()[-1])[1],
        'passed':prod['day'].tolist()[-1]
    }]

    aggregation = {'goal':'first','amount':'sum'}
    prod_amount = prod.groupby('season').agg(aggregation)
    return render(request, 'LineDetection/statistics.html', {'time': time_json})