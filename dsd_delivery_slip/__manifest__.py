# -*- coding: utf-8 -*-
{
    'name': "DSD - Delivery Slip",

    'summary': """
       menambah field pengirim dan penerima pada printout delivery slip""",

    'description': """
        menambah field pengirim dan penerima pada printout delivery slip
        
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'report/report_deliveryslip.xml',
    ]
}
