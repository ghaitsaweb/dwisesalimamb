# -*- coding: utf-8 -*-
{
    'name': "DSD - Sales Report",

    'summary': """
       customize report Sales""",

    'description': """
        customize report Sales
        
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','sale', 'dsd_sales_number'],

    # always loaded
    'data': [
        'report/print_template.xml',
        'report/sales_order.xml',
        'report/sales_reports.xml',
        'views/document_layout.xml',
    ],
    
    'uninstall_hook':'my_uninstall_hook'
}
