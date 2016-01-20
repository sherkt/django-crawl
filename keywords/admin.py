from django.contrib import admin

from .models import Keyword, Result

class KeywordAdmin(admin.ModelAdmin):
    list_display = ['name', 'average_count', 'average_density', ]
    readonly_fields = ['date_created', 'last_activity', ]

admin.site.register(Keyword, KeywordAdmin)

class ResultAdmin(admin.ModelAdmin):
    list_display = ['url', 'keyword', 'word_count', 'density', ]
    readonly_fields = ['date_created', 'last_activity', ]

admin.site.register(Result, ResultAdmin)
