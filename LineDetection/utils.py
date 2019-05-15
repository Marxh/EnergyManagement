import pandas as pd
from .models import Facility, Energy, Anomaly

def to_dataframe(queryset):
    df = queryset.to_dataframe()
    return df

'''
def to_queryset(df):
    return_qs = Facility.objects.none()
    for col in df.columns:
        pass
'''