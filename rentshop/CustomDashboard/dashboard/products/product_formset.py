# python imports

# django imports
from django.forms import modelform_factory, inlineformset_factory, formset_factory, modelformset_factory
from django.apps.registry import apps

# packages imports
from oscar.core.loading import get_class, get_model

# internal imports
from .product_forms import *

Product = get_model('catalogue', 'Product')
ProductCostEntries = get_model('catalogue', 'ProductCostEntries')


BaseProductCostEntriesSet_Create = formset_factory(ProductCostEntriesModelForm, extra=4)
BaseProductCostEntriesSet = modelformset_factory(ProductCostEntries, form=ProductCostEntriesModelForm, extra=4)