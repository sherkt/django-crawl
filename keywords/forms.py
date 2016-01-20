from django import forms

class CrawlForm(forms.Form):
    url = forms.CharField()
    keyword = forms.CharField()
