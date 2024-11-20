# -*- coding: utf-8 -*-
{
    'name': "DSD - Proyek SBI",

    'summary': """
        Task Minor Untuk Proyek SBI dijadikan satu di modul ini
       """,

    'description': """
        1. disable printout rfq
    """,

    'author': "PT. Dwisesa Solusi Digitalindo",
    'website': "http://www.dwisesa.id",

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','purchase'],

    # always loaded
    'data': [
        'report/purchase_reports.xml',
        'views/purchase_views.xml',
    ],
    'assets': {
        'dsd_custom_sbi.assets_common': [
            'static/src/css/my.css'
        ]
    }
}
