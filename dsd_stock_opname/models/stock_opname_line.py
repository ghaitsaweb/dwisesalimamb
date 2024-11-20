# -*- coding: utf-8 -*-
import json
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


class StockOpnameLine(models.Model):
    _name = 'stock.opname.line'    

    stock_opname_id = fields.Many2one('stock.opname', string="Stock Opname", required=True, index=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', related='stock_opname_id.company_id', store=False)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    lot_id = fields.Many2one(
        'stock.lot', 'Lot/Serial',
        states={'done': [('readonly', True)]}, domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    onhand_qty = fields.Float(
        'On Hand Quantity', required=True, readonly=True, store=True)
    counted_qty = fields.Float(
        'Counted Quantity', required=True)
    difference_qty = fields.Float('Difference Quantity', readonly=True)
    expired_date = fields.Datetime('Expired Date')
    notes = fields.Text('Notes')
    state = fields.Selection(related='stock_opname_id.state', store=True)
    applied = fields.Boolean(string="Applied", default=False)
    action = fields.Selection([("adjustment", "Adjustment"), ("scrap", "Scrap"),("none", "None")], default='none', track_visibility = 'onchange')

    @api.onchange('counted_qty')
    def counted_qty_on_change(self):

        for line in self:
                line.update({
                    'difference_qty': line.counted_qty - line.onhand_qty,
                    'applied':True
                })
    
    def action_adjustment(self):
        orders = self.mapped('stock_opname_id')
        for line in self:
            if(line.action != 'adjustment'):
                if(orders.state != 'draft'):
                    msg = line.product_id.name 
                    if(line.lot_id):
                        msg += " Lot " + line.lot_id.name
                    msg += " action changed from " + line.action + " to adjustment"
                    orders.message_post(body=msg) 
                line.update({
                    'action':'adjustment'
                })
                
    
    def action_scrap(self):
        orders = self.mapped('stock_opname_id')
        for line in self: 
            if(line.action != 'scrap'):
                if(orders.state != 'draft'):
                    msg = line.product_id.name 
                    if(line.lot_id):
                        msg += " Lot " + line.lot_id.name
                    msg += " action changed from " + line.action + " to scrap"
                    orders.message_post(body=msg) 
                line.update({
                    'action':'scrap'
                })
                

    def action_none(self):
        orders = self.mapped('stock_opname_id')
        for line in self:
            if(line.action != 'none'):
                if(orders.state != 'draft'):
                    msg = line.product_id.name 
                    if(line.lot_id):
                        msg += " Lot " + line.lot_id.name
                    msg += " action changed from " + line.action + " to none"
                    orders.message_post(body=msg)
                line.update({
                    'action':'none'
                })
                
    
    