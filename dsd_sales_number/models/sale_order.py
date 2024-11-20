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


class SaleOrder(models.Model):
    _inherit = 'sale.order'    

    so_no = fields.Char(string='Sales Order No.', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code('new.quotation.running.no')
        return super(SaleOrder, self).create(vals_list)

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm() 
        for order in self:
            order.so_no = self.env["ir.sequence"].next_by_code("new.order.running.no")
        
        return result

    