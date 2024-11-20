# -*- coding: utf-8 -*-
{
    'name': "DSD - Stock Opname",

    'summary': """
       Stock Opname""",

    'description': """
        1. Stock Opname
        2. Approval Stock Opname
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/stock_opname_reject_view.xml',
        'views/stock_opname.xml',
        'views/stock_opname_approval.xml',
        'data/ir_sequence_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dsd_stock_opname/static/src/css/my.css'
        ]
    }
}
