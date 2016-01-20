from django.shortcuts import render, redirect

from .models import Keyword, Result
from .forms import CrawlForm
from .util import get_page, save_results


def index(request):
    return render(request, 'keywords/index.html')

def keyword_detail(request, keyword_id):
    keyword = Keyword.objects.filter(pk=keyword_id).first()
    other_keywords = Keyword.objects.exclude(pk=keyword_id)
    context = {'keyword': keyword, 'other_keywords': other_keywords, }
    return render(request, 'keywords/keyword-detail.html', context)

def crawl(request):
    if request.method == 'POST':
        form = CrawlForm(request.POST)
        
        if form.is_valid():
            cd = form.cleaned_data
            
            page, error = get_page(cd["url"])
            if error:
                return render(request, 'keywords/crawl.html', dict(
                    form=form, error=error
                ))
            else:
                result = save_results(request, cd, page)
                
            return redirect('results')
    else:
        form = CrawlForm()
    return render(request, 'keywords/crawl.html', {'form': form})

def results(request):
    result_id = request.session.get("result_id")
    
    try:
        result = Result.objects.get(pk=result_id)
    except:
        context=dict(error="No result found.")
        return render(request, 'keywords/results.html', context)
    
    keyword = result.keyword
    allresults = Result.objects.filter(
        keyword=keyword,
        word_count__gt=0
    )
    context = {"result": result, "keyword": keyword, "allresults": allresults }
    return render(request, 'keywords/results.html', context)
