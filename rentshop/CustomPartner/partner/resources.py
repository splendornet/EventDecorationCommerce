from import_export import resources
from CustomPartner.partner.models import Partner
from import_export.fields import Field

class Partner_Resource(resources.ModelResource):
    #id = Field(column_name='id')
    class Meta:
        model = Partner


        fields = {
            'name','user','pan_number','vat_number','telephone_number','email_id','address_line_1',
            'address_line_2',
            'country','state','city','pincode','categories'
        }

        # country = fields.Field(column_name='country_id', attribute='Country',
        #                        widget=ForeignKeyWidget(Country, 'country'))

        exclude = ('id',)
        export_order = ('name','email_id','pan_number','vat_number','telephone_number',
                        'address_line_1','address_line_2','country','state','city','pincode',
                        'categories')





        # import_id_fields = (
        #     'id'
        # )

class Partner_Blank_Resource(resources.Resource):

    name = Field(column_name='name')
    model = Partner

    # fields = {
    #         'name', 'pan_number', 'vat_number', 'telephone_number', 'email_id', 'address_line_1',
    #         'address_line_2',
    #         'country', 'state', 'city', 'pincode', 'categories'
    # }



################################################################################
################################################################################

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()