# python imports

# django imports
from django.shortcuts import HttpResponse, redirect
from django.contrib import messages

# 3rd party imports
from oscar.core.loading import get_class, get_classes
from openpyxl import Workbook

# internal imports
OrderReportGenerator = get_class('dashboard.reports', 'OrderReportGenerator')
ProductReportGenerator, UserReportGenerator = get_classes('dashboard.reports', ['ProductReportGenerator','UserReportGenerator'])
OpenBasketReportGenerator, SubmittedBasketReportGenerator = get_classes('dashboard.reports', ['OpenBasketReportGenerator','SubmittedBasketReportGenerator'])


class GeneratorRepository(object):

    generators = [
        OrderReportGenerator, ProductReportGenerator, SubmittedBasketReportGenerator
    ]

    def get_report_generators(self):
        return self.generators

    def get_generator(self, code, user):
        for generator in self.generators:
            if generator.code == code:
                return generator
        return None


def generate_excel(request, **kwargs):

    """
    Method to generate excel
    """

    try:

        wb = Workbook(write_only=True)
        ws = wb.create_sheet()

        for line in kwargs.get('excel_data'):
            ws.append(line)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s.xlsx' % (kwargs.get('filename'))

        wb.save(response)

        return response

    except:

        messages.error(request, 'Something went wrong.')
        return redirect('/dashboard')

