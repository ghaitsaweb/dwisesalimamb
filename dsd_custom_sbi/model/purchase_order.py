# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import (
    UserError,
    Warning,
)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def print_po(self):
        if (self.date_approve == None):
            raise UserError("You can't Print PO before Approved. ")
        return self.env.ref('purchase.action_report_purchase_order').report_action(self)