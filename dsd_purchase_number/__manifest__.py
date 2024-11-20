# -*- coding: utf-8 -*-
{
    'name': "DSD - RFQ and PO Number",

    'summary': """
       request for quotation and purchase order number""",

    'description': """
        make RFQ and PO number in different sequence
        
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'views/purchase_views.xml',
    ]
}
