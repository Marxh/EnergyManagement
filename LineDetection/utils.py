import pandas as pd
from .models import Facility, Energy, Anomaly

def to_dataframe(queryset):
    df = queryset.to_dataframe()
    return df

def get_compare_date(df):
    return str(df['date'].year)+'-'+str(df['date'].month)

def get_type_num(df, flag_num):
    if(str(df['anomaly_type']) == flag_num):
        return 1
    else:
        return 0