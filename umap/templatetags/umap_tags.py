import json
from copy import copy

import bleach as bl
from django import template
from django.conf import settings

from ..models import DataLayer, TileLayer
from ..views import _urls_for_js

register = template.Library()

ALLOWED_TAGS = bl.sanitizer.ALLOWED_TAGS + ["table", "tr", "td", "th", "tbody"]


@register.inclusion_tag('umap/css.html')
def umap_css():
    return {
        "STATIC_URL": settings.STATIC_URL
    }


@register.inclusion_tag('umap/js.html')
def umap_js(locale=None):
    return {
        "STATIC_URL": settings.STATIC_URL,
        "locale": locale
    }


@register.inclusion_tag('umap/map_fragment.html')
def map_fragment(map_instance, **kwargs):
    layers = DataLayer.objects.filter(map=map_instance)
    datalayer_data = [c.metadata for c in layers]
    map_settings = map_instance.settings
    if "properties" not in map_settings:
        map_settings['properties'] = {}
    map_settings['properties'].update({
        'tilelayers': [TileLayer.get_default().json],
        'datalayers': datalayer_data,
        'urls': _urls_for_js(),
        'STATIC_URL': settings.STATIC_URL,
        "allowEdit": False,
        'hash': False,
        'attributionControl': False,
        'scrollWheelZoom': False,
        'umapAttributionControl': False,
        'noControl': True,
        'umap_id': map_instance.pk,
        'onLoadPanel': "none",
        'captionBar': False,
        'default_iconUrl': "%sumap/img/marker.png" % settings.STATIC_URL,
        'slideshow': {}
    })
    map_settings['properties'].update(kwargs)
    prefix = kwargs.pop('prefix', None) or 'map'
    page = kwargs.pop('page', None) or ''
    unique_id = prefix + str(page) + "_" + str(map_instance.pk)
    return {
        "map_settings": json.dumps(map_settings),
        "map": map_instance,
        "unique_id": unique_id
    }


@register.simple_tag
def tilelayer_preview(tilelayer):
    """
    Return an <img> tag with a tile of the tilelayer.
    """
    output = '<img src="{src}" alt="{alt}" title="{title}" />'
    url = tilelayer.url_template.format(s="a", z=9, x=265, y=181)
    output = output.format(src=url, alt=tilelayer.name, title=tilelayer.name)
    return output


@register.filter
def notag(s):
    return s.replace('<', '&lt;')


@register.filter
def bleach(s):
    return bl.clean(s, tags=ALLOWED_TAGS)


@register.simple_tag(takes_context=True)
def paginate_querystring(context, page):
    qs = copy(context["request"].GET)
    qs["p"] = str(page)
    return qs.urlencode()


@register.filter
def ipdb(what):
    import ipdb
    ipdb.set_trace()
    return ''
