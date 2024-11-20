# -*- coding: utf-8 -*-
{
    'name': "DSD - Purchase Report",

    'summary': """
       customize report Purchase""",

    'description': """
        customize report Purchase
        
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','purchase', 'dsd_purchase_number'],

    # always loaded
    'data': [
        'report/print_template.xml',
        'report/purchase_quotation.xml',
        'report/purchase_order.xml',
        'report/purchase_reports.xml',
        'views/document_layout.xml',
    ],
    'uninstall_hook':'my_uninstall_hook'
}
