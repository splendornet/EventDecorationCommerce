# python imports
from Crypto.Cipher import AES
import hashlib
from binascii import hexlify, unhexlify

# packages imports
from oscar.core.loading import get_model

# internal imports
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
OrderAllocatedVendor = get_model('order', 'OrderAllocatedVendor')
Partner = get_model('partner', 'Partner')
MultiDB = get_model('partner', 'MultiDB')
IndividualDB = get_model('partner', 'IndividualDB')


def pad(data):

    """
    ccavenue method to pad data.
    :param data: plain text
    :return: padded data.
    """

    length = 16 - (len(data) % 16)
    data += chr(length)*length
    return data


def unpad(data):

    """
    ccavenue method to unpad data.
    :param data: encrypted data
    :return: plain data
    """

    return data[0:-ord(data[-1])]


def encrypt(plain_text, working_key):

    """
    Method to encrypt cc-avenue hash.
    :param plain_text: plain text
    :param working_key: cc-avenue working key.
    :return: md5 hash
    """

    iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    plain_text = pad(plain_text)

    byte_array_wk = bytearray()
    byte_array_wk.extend(map(ord, working_key))

    enc_cipher = AES.new(hashlib.md5(byte_array_wk).digest(), AES.MODE_CBC, iv)
    hexl = hexlify(enc_cipher.encrypt(plain_text)).decode('utf-8')

    return hexl


def decrypt(cipher_text, working_key):

    """
    Method decrypt cc-avenue response.
    :param cipher_text: encrypted data
    :param working_key: working data
    :return: list
    """

    iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'

    encrypted_text = unhexlify(cipher_text)

    bytearray_working_key = bytearray()
    bytearray_working_key.extend(map(ord, working_key))

    dec_cipher = AES.new(hashlib.md5(bytearray_working_key).digest(), AES.MODE_CBC, iv)

    plain_data = unpad(dec_cipher.decrypt(encrypted_text).decode('utf-8'))

    plain_data_list = plain_data.split('&')

    final_pay_list = []
    for data in plain_data_list:

        final_pay_dict = {}
        final_pay_dict[data.split('=')[0]] = data.split('=')[1]

        final_pay_list.append(final_pay_dict)

    return final_pay_list


def allocate_vendor(order_number):

    """
    Method to allocate single vendor
    :param order_number: order number
    :return: flag
    """

    try:

        order = Order.objects.get(number=order_number)
        order_lines = Line.objects.filter(order=order)

        for line in order_lines:

            try:

                order_product = line.product
                order_product_category = order_product.categories.last()

                # if category in both databases.
                if MultiDB.objects.filter(category=order_product_category) and IndividualDB.objects.filter(
                        category=order_product_category):
                    continue

                # if in multi or not in indi
                if MultiDB.objects.filter(category=order_product_category) or not IndividualDB.objects.filter(
                        category=order_product_category):
                    continue

                indi_record = IndividualDB.objects.filter(category=order_product_category).last()
                individual_asp = indi_record.individual_asp.last()


                if not OrderAllocatedVendor.objects.filter(order_line=line):
                    OrderAllocatedVendor.objects.create(
                        order=order, order_line=line, order_number=order.number,
                        vendor=individual_asp, vendor_name=individual_asp.name,
                        product=order_product, product_category=order_product_category,
                        product_name=order_product.title, product_category_name=order_product_category.name
                    )

            except Exception as e:

                import os
                import sys
                print('-----------in exception----------')
                print(e.args)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

                continue

    except Exception as e:

        print('Error @ 137')

    return True