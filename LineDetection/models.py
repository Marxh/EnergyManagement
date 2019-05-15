from django.db import models
from django_pandas.managers import DataFrameManager

# Create your models here.


class Facility(models.Model):
    facility_name = models.CharField(max_length=200)
    production_line = models.IntegerField(default=0)
    brand = models.CharField(max_length=20)
    install_date = models.DateTimeField('installed date')
    energy_total = models.FloatField(default = 0)
    objects = DataFrameManager()

class Energy(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    season = models.IntegerField(default=0)
    energy_date = models.DateTimeField('energy date')
    energy = models.FloatField(default = 0)
    objects = DataFrameManager()

class Anomaly(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    season = models.IntegerField(default=0)
    anomaly_date = models.DateTimeField('energy date')
    anomaly_type = models.IntegerField(default=0)
    anomaly_comments = models.CharField(max_length=200)
    objects = DataFrameManager()

class season_goal(models.Model):
    season = models.IntegerField(default=0)
    production_line = models.IntegerField(default=0)
    goal = models.IntegerField(default=0)
    objects = DataFrameManager()

class production_amount(models.Model):
    season = models.ForeignKey(season_goal, on_delete=models.CASCADE)
    production_date = models.DateTimeField('pruduction date')
    production_line = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    objects = DataFrameManager()

class Cluster(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    cluster_id = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    energy = models.FloatField(default = 0)
    season = models.IntegerField(default=0, null=True)
    objects = DataFrameManager()