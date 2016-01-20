from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<keyword_id>[0-9]+)/$', views.keyword_detail, name='keyword-detail'),
    url(r'^crawl/$', views.crawl, name='crawl'),
    url(r'^crawl/results/$', views.results, name='results'),
]
