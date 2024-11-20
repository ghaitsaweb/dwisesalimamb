# -*- coding: utf-8 -*-
{
    'name': "DSD - SO and SQ Number",

    'summary': """
       sales order and quotation number""",

    'description': """
        1. Add new SO and SQ number and the sequence
        
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales Order',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'views/sale_order.xml',
    ]
}
