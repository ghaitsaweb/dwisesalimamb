# -*- coding: utf-8 -*-
{
    'name': "DSD - Sales Approval",

    'summary': """
       Approval for Sales Document""",

    'description': """
        1. Approval Sales Quotation
        2. Approval Sales Order
        3. Approval Sales Invoice
        4. Config Approval
        
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales Order',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/sale_reject_view.xml',
        'views/sale_order.xml',
        'views/account_moves.xml',
        'views/sale_order_approval.xml',
        'views/res_users.xml'
    ]
}
