from django.contrib import admin
from django import forms

# Register your models here.

from .models import Tag, Article


class ArticleForm(forms.ModelForm):
    article=forms.CharField( widget=forms.Textarea )
    class Meta:
        model = Article
        fields=('article',)

class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm
    date_hierarchy = 'pub_date'
    empty_value_display = '-空-'
    fieldsets = [
        (None, {'fields': ('article_name', ('pub_date', 'article'),'tag_on')}),
    ]
    filter_horizontal = ('tag_on',)

admin.site.register(Tag)
admin.site.register(Article,ArticleAdmin)