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
    # my regex pattern for words (with spaces), in case I want to reuse it
    pattern = re.compile("[\w '-]+")
    m = pattern.search(name)
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

    if not keyword:
        keyword = Keyword.objects.create(
            name=name.lower(),
        )

    info = scraper(page, name)

    density = calculate_density(info["keywordcount"], info["wordcount"], name)

    if not result:
        result = Result.objects.create(
            url = url.lower(),
            keyword = keyword,
            word_count = info["keywordcount"],
            density = density,
            title = info["title"],
        )
    elif result:
        result.word_count = info["keywordcount"]
        result.density = density
        result.last_activity = now()
        result.title = info["title"]
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

def calculate_density(nk, tw, keyword):
    #nk is keyword count
    #tw is total number of words
    #num_words below is number of words in keyword
    m = re.split(" ", keyword)
    num_words = len(m)

    # use basic calculation, but could do this:
    # density = 100 * (nk/(tw - (nk * (num_words-1))))
    # this takes into account inflation of total word count
    # if num_words = 1, then this is identical to basic calculation
    if tw > 0:
        return 100*(nk/tw)
    else:
        return 0

def scraper(page, keyword):
    tree = html.fromstring(page.content)
    soup = BeautifulSoup(page.content, "lxml")
    
    words = []
    for tag in ["p", "h1", "h2", "h3", "h4", "h5", "a"]:
        words = words + get_words(soup.body(tag))

    string_from_list = " ".join(words)
    m = re.findall(keyword, string_from_list, flags=re.IGNORECASE)

    try:
        title = soup.title.text
    except:
        title = None
    
    return dict(
        wordcount = len(words),
        keywordcount = len(m),
        title = title,
    )

def get_words(list):
    words = []
    pattern = re.compile("[\w'-]+")

    for element in list:
        words = words  + pattern.findall(element.text)
        
    return words
