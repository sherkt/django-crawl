import requests
import re

from lxml import html
from bs4 import BeautifulSoup

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.timezone import now

from .models import Keyword, Result
from .forms import CrawlForm

def index(request):
    return render(request, 'keywords/index.html')

def keyword_detail(request, keyword_id):
    keyword = Keyword.objects.filter(pk=keyword_id).first()
    other_keywords = Keyword.objects.exclude(pk=keyword_id)
    context = {'keyword': keyword, 'other_keywords': other_keywords, }
    return render(request, 'keywords/keyword-detail.html', context)

def crawl(request):
    form = CrawlForm
    return render(request, 'keywords/crawl.html', dict(form=form))

def results(request):
    name = request.POST.get("keyword")
    url = request.POST.get("url")

    if not url or not name:
        error = "Check inputs."
        return redirect("crawl")

    # do a check on url:
    if not re.search("http", url):
        url = "http://" + url
    
    keyword = Keyword.objects.filter(
        name__iexact=name
    ).first()

    result = Result.objects.filter(
        keyword__name__iexact=name,
        url__iexact=url
    ).first()

    if name and not keyword:
        keyword = Keyword.objects.create(
            name=name.lower(),
        )

    info = scraper(url, name)

    if info["keywordcount"] > 0: 
        density = 100*(info["keywordcount"]/info["wordcount"])
    else:
        density = 0

    if url and not result:
        result = Result.objects.create(
            url = url.lower(),
            keyword = keyword,
            word_count = info["keywordcount"],
            density = density,
        )
    elif result:
        result.word_count = info["keywordcount"]
        result.density = density
        result.last_activity = now()
        result.save()

    allresults = Result.objects.filter(
        keyword__name__iexact=name,
        word_count__gt=0
    )

    wordcount = 0
    densitycount = 0
    for x in allresults:
        wordcount = wordcount + x.word_count
        densitycount = densitycount + x.density

    averagewords = wordcount / allresults.count()
    averagedensity = densitycount / allresults.count()


    # update the averages for the keyword
    keyword.average_count = averagewords
    keyword.average_density = averagedensity
    keyword.last_activity = now()
    keyword.save()

    context = {"result": result, "keyword": keyword, "allresults": allresults }
    return render(request, 'keywords/results.html', context)

def scraper(url, keyword):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    
    soup = BeautifulSoup(page.content, "lxml")
    
    p_list = get_words(soup.body("p"))
    h1_list = get_words(soup.body("h1"))
    h2_list = get_words(soup.body("h2"))
    h3_list = get_words(soup.body("h3"))
    links_list = get_words(soup.body("a"))

    words = p_list + h1_list + h2_list + h3_list + links_list

    string_from_list = " ".join(words)
    m = re.findall(keyword, string_from_list, flags=re.IGNORECASE)
    
    return dict(
        wordcount = len(words),
        keywordcount = len(m),
    )
    
    return tree

def get_words(list):
    words = []
    for element in list:
        words = words  + re.findall("[a-zA-Z']+", element.text)
        
    return words
