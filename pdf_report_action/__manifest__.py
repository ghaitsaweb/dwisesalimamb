# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
{
    'name': 'Dynamic Report Operations',
    'version': '16.0.1.0.0',
    'category': 'Productivity',
    'summary': """Perform multiple report operations in Sales/Purchase
    /Inventory/ Accounting""",
    'description': "Users can perform various actions such as printing, "
                   "downloading, and sharing reports of various records in "
                   "Sales, Purchase, Inventory, Accounting",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['sale_management', 'purchase', 'stock', 'account',],
    'data': [
        'security/ir.model.access.csv',
        'wizard/dynamic_action_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pdf_report_action/static/src/css/report_action.css',
            'pdf_report_action/static/src/js/report_action.js',
            'pdf_report_action/static/src/js/report_action_systray.js',
            'pdf_report_action/static/src/xml/report_action_systray.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,

}