import requests
import re

from django.utils.timezone import now
from django.shortcuts import redirect

from lxml import html
from bs4 import BeautifulSoup

from .models import Keyword, Result


def get_page(url):
    # do a check on url:
    if not re.search("http", url):
        url = "http://" + url

    page = None
    error = None
    try:
        page = requests.get(url)
    except:
        error = "Error getting that page."
        return (page, error)
    
    if page.status_code != 200:
        error = "Bad status code: %s." % page.status_code
    elif not page.content:
        error = "No page content."

    return (page, error)


def save_results(request, data, page):
    name = data.get("keyword")
    url = data.get("url")

    # clean up the keyword a bit:
    m = re.search("[a-z ]+", name, flags=re.IGNORECASE)
    if m:
        name = m.group(0)
    
    if not url or not name:
        error = "Check inputs."
        return redirect("crawl")
    
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

    info = scraper(page, name)

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

    try:
        averagewords = wordcount / allresults.count()
        averagedensity = densitycount / allresults.count()
    except:
        averagewords = 0
        averagedensity = 0

    # update the averages for the keyword
    keyword.average_count = averagewords
    keyword.average_density = averagedensity
    keyword.last_activity = now()
    keyword.save()

    request.session["result_id"] = result.pk

    return result

def scraper(page, keyword):
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

def get_words(list):
    words = []
    for element in list:
        words = words  + re.findall("[a-zA-Z']+", element.text)
        
    return words
