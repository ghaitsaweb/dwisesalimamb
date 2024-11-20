# -*- coding: utf-8 -*-
{
    'name': "DSD - Purchase Approval",

    'summary': """
       Approval for Purchase Document""",

    'description': """
        1. Approval RFQ
        2. Approval Purchase Order
        4. Config Approval
        
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase Order',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/purchase_reject_view.xml',
        'views/purchase_order.xml',
        'views/purchase_order_approval.xml',
        'views/res_config_settings.xml',
        'views/res_users.xml'
    ],
    'post_init_hook':'my_post_init_hook'
}
