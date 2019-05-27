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
    anomaly_solve = models.IntegerField(default=0)
    solved_comments = models.CharField(max_length=200, default = '', null = True)
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
    anomaly_condition = models.IntegerField(default=0)
    anomaly_comments = models.CharField(max_length=200, default = '', null=True)
    #position = models.IntegerField(default=0)
    #energy = models.FloatField(default = 0)
    #season = models.IntegerField(default=0, null=True)
    objects = DataFrameManager()

class Tag(models.Model):
    tag_text = models.CharField(max_length=200, default = '', null=True)
    #article = models.ForeignKey(Article, on_delete=models.CASCADE)
    objects = DataFrameManager()

    def __str__(self):
        return self.tag_text

    class Meta: 
        verbose_name='标签'
        verbose_name_plural='标签'

class Article(models.Model):
    article_name = models.CharField(max_length=200, default = '', null=True)
    article = models.CharField(max_length=2000, default = '', null=True)
    tag_on = models.ManyToManyField(Tag, blank=True)
    pub_date = models.DateTimeField('article date')
    objects = DataFrameManager()

    def __str__(self):
        return self.article_name
    
    class Meta: 
        verbose_name='文章'
        verbose_name_plural='文章'

    def get_article_name(self):
        return self.article_name
    
    def get_pub_date(self):
        return self.pub_date
    
    get_article_name.short_description = r'文章名称'
    get_pub_date.short_description = r'发布时间'