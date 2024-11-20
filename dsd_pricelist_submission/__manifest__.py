# -*- coding: utf-8 -*-
{
    'name': "DSD - Pricelist Submission",

    'summary': """
       Pricelist Submission""",

    'description': """
        1. Pricelist Submission
        2. Approval Pricelist Submission
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','product'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/pricelist_submission_reject_view.xml',
        'views/pricelist_submission.xml',
        'views/pricelist_submission_approval.xml',
    ]
}
