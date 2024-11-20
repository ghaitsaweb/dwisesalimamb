# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import (
    AccessError,
    UserError,
    RedirectWarning,
    ValidationError,
    Warning,
)
from datetime import timedelta, datetime, date


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'    

    po_no = fields.Char(string='Purchase Order No.', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('state', 'draft') == 'draft':
                vals['name'] = self.env['ir.sequence'].next_by_code('new.rfq.running.no')
        return super(PurchaseOrder, self).create(vals_list)

    def button_confirm(self):
        result = super(PurchaseOrder, self).button_confirm() 
        for order in self:
            if order.po_no == False:
                order.po_no = self.env["ir.sequence"].next_by_code("new.po.running.no")
        
        return result
    
    def button_draft(self):
        for order in self:
            if order.write({'state' : 'draft'}):
                order.name = self.env["ir.sequence"].next_by_code("new.rfq.running.no")
        result = super(PurchaseOrder, self).button_draft()
        return result
    