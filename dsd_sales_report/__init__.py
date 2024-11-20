# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

from . import models
from . import report

def my_uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    #do thing
    record_id = env.ref('sale.action_report_saleorder').id
    so = env['ir.actions.report'].browse(record_id)
    so.report_name = 'sale.report_saleorder'