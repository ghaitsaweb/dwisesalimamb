# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

from . import models
from . import report

def my_uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    #do thing
    record_id = env.ref('purchase.action_report_purchase_order').id
    so = env['ir.actions.report'].browse(record_id)
    so.report_name = 'purchase.report_purchaseorder'
    
    record_id = env.ref('	purchase.report_purchase_quotation').id
    so = env['ir.actions.report'].browse(record_id)
    so.report_name = 'purchase.report_purchasequotation'