from django import forms
from django.template.defaultfilters import striptags


class CrawlForm(forms.Form):
    url = forms.URLField()
    keyword = forms.CharField()


    def clean_keyword(self):
        keyword = self.cleaned_data['keyword']
        if striptags(keyword) != keyword:
            raise forms.ValidationError("You have some HTML code in there.")
        elif "()" in keyword or ";" in keyword:
            raise forms.ValidationError("You have code in there.")
        return keyword
