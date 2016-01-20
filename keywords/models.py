from django.db import models
from django.utils.timezone import now

class Keyword(models.Model):
    name = models.CharField(max_length=200, unique=True)
    average_count = models.PositiveIntegerField(default=0)
    average_density = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(default=now)
    
    def __str__(self):
        return u"%s" % (self.name)

    class Meta:
        ordering = ("name", )


class Result(models.Model):
    url = models.URLField(max_length=200)
    keyword = models.ForeignKey("keywords.Keyword")
    word_count = models.PositiveIntegerField()
    density = models.DecimalField(max_digits=5, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(default=now)
    
    def __str__(self):
        return u"%s" % (self.url)
    
    class Meta:
        ordering = ("keyword", "-word_count", "url", )
        unique_together = ("url", "keyword")
