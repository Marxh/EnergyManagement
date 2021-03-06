from django.contrib import admin
from django import forms
from django.forms import Textarea, TextInput
from django.db import models
from .models import Anomaly

# Register your models here.

from .models import Tag, Article


class ArticleForm(forms.ModelForm):
    article=forms.CharField( widget=forms.Textarea )
    
    class Meta:
        model = Article
        fields=('article',)
        widget = {
            'content': forms.Textarea(attrs={'style': 'height: 200px;width:1000px'}),}    

class ArticleAdmin(admin.ModelAdmin):
    search_fields = ['article_name']
    list_filter=['pub_date','tag_on']
    list_per_page = 20
    actions_on_top=True
    actions_on_bottom=False
    list_display = ['article_name','pub_date']

    form = ArticleForm
    empty_value_display = '空'
    fieldsets = [
        (None, {'fields': (('article_name', 'pub_date'), 'article','tag_on')}),
    ]
    filter_horizontal = ('tag_on',)

class MyAdminSite(admin.AdminSite):
    site_header = '知识分享博客'
    site_title = '知识分享博客'

admin.site.register(Tag)
admin.site.register(Article,ArticleAdmin)
admin.site.site_header = '知识分享博客'
admin_site = MyAdminSite(name='management')