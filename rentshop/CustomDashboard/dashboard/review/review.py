# python imports

# django imports
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from django.shortcuts import HttpResponse
from django.contrib import messages

# packages imports
from oscar.apps.dashboard.reviews import views as review_view
from oscar.core.loading import *
from oscar.views import sort_queryset

# internal imports
CustomDashboardProductReviewForm = get_class('dashboard.forms', 'CustomDashboardProductReviewForm')
CustomProductReviewSearchForm = get_class('dashboard.forms', 'CustomProductReviewSearchForm')

Product = get_model('catalogue', 'Product')
ProductReview = get_model('reviews', 'productreview')


class CustomReviewUpdateView(review_view.ReviewUpdateView):

    """
    Oscar extended review FilteredProductListViewupdate view.
    """

    form_class = CustomDashboardProductReviewForm


class CustomReviewListView(review_view.ReviewListView):

    """
    Oscar extended reviews list method.
    """

    form_class = CustomProductReviewSearchForm

    def get(self, request, *args, **kwargs):

        """
        Default get method to return context
        :param request: default
        :param args: default
        :param kwargs: default
        :return: template
        """

        response = super(CustomReviewListView, self).get(request, **kwargs)
        self.form = self.form_class()

        return response

    def get_queryset(self):

        """
        Method to return review queryset.
        :return: queryset
        """

        queryset = self.model.objects.select_related('product', 'user').all()
        queryset = sort_queryset(queryset, self.request, ['score', 'total_votes', 'date_created'])
        queryset = queryset.order_by('-date_created')
        queryset = queryset.filter(product__is_deleted= False)
        self.desc_ctx = {
            'main_filter': _('All reviews'),
            'date_filter': '',
            'status_filter': '',
            'kw_filter': '',
            'name_filter': '',
        }

        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('title'):
            title = data.get('title')
            queryset = queryset.filter(title__icontains=title)

        if data.get('rating'):
            rating = data.get('rating')
            queryset = queryset.filter(score=rating)

        if data.get('status'):
            queryset = self.add_filter_status(queryset, data['status'])

        if data.get('date'):
            date = data.get('date')
            queryset = queryset.filter(date_created__date=date)

        if data.get('month'):
            month = data.get('month')
            queryset = queryset.filter(date_created__month=month)

        if data.get('year'):
            year = data.get('year')
            queryset = queryset.filter(date_created__year=year)

        if data.get('category'):

            category = data.get('category')
            product = Product.objects.filter(categories=category,is_deleted = False)
            queryset = queryset.filter(product__in=product)

        queryset = self.get_date_from_to_queryset(data['date_from'], data['date_to'], queryset)

        return queryset


class UpdateReviewStatus(View):

    def get(self, request, *args, **kwargs):

        try:

            data = request.GET
            new_filter_list = []

            reviews_list = data.getlist('review_id')
            review_status = data.get('review_status')

            for i in reviews_list:
                new_filter_list.extend(i.split(','))

            for i in new_filter_list:
                ProductReview.objects.get(id=i)

            ProductReview.objects.filter(id__in=new_filter_list).update(status=review_status)

            messages.success(request, 'Reviews updated successfully.')
            return HttpResponse('TRUE')

        except Exception as e:

            messages.error(request, 'Something went wrong.')
            return HttpResponse('IN_SERVER')
