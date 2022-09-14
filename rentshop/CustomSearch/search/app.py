from oscar.apps.search.app import SearchApplication as CoreSearchApplication
from django.conf.urls import url
from haystack.views import search_view_factory
from oscar.apps.search import facets
from oscar.core.application import Application
from oscar.core.loading import get_class


class SearchApplication(CoreSearchApplication):
    name = 'search'
    #search_view = get_class('search.views', 'FacetedSearchView')
    search_form = get_class('search.forms', 'CustomSearchForm')

application = SearchApplication()