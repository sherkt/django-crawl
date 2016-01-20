from django import template

from ..models import Result

register = template.Library()


@register.assignment_tag()
def get_result(id):
    result = Result.objects.filter(pk=id).first()
    return result
