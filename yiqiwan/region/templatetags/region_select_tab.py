from django.template import Library

from django.template.loader import render_to_string
register = Library()
@register.filter
def get_region_select_tab(request):
    return render_to_string('region/region_tabs.html')

