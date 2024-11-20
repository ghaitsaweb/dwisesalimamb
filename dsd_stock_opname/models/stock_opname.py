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


class StockOpname(models.Model):
    _name = 'stock.opname'    
    _inherit = 'mail.thread'

    def _get_default_location_id(self):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None

    state = fields.Selection([("draft", "Draft"), ("waiting approval", "Waiting Approval"), ("done", "Done"), ("cancel", "Cancel"),("rejected", "Rejected")], default='draft', tracking=True)
    name = fields.Char(string='Stock Opname No.', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True, states={'done': [('readonly', True)]})
    
    warehouse_id = fields.Many2one(
        'stock.warehouse', 'Warehouse', domain="[('company_id', 'in', [company_id, False])]",
        required=True, states={'done': [('readonly', True)],'waiting approval': [('readonly', True)],'rejected': [('readonly', True)], 'cancel': [('readonly', True)]}, default=_get_default_location_id, check_company=True)
    
    location_id = fields.Many2one(
        'stock.location', 'Location', domain="[('usage', 'not in', ['view']),('warehouse_id', 'in', [warehouse_id])]",
        required=True, states={'done': [('readonly', True)],'waiting approval': [('readonly', True)],'rejected': [('readonly', True)], 'cancel': [('readonly', True)]}, check_company=True)
    
    date = fields.Datetime('Date', states={'done': [('readonly', True)],'waiting approval': [('readonly', True)],'rejected': [('readonly', True)], 'cancel': [('readonly', True)]})

    reject_reason = fields.Text(string='Reject Reason', readonly=True)

    staff = fields.Text(string='Staff', required=True)

    level_approval = fields.Integer(string="Current Level Approval", default=0)
    current_group_approval = fields.Many2one('res.groups', string="Current Approval Group", readonly=True)
    approver= fields.Json()

    user_id = fields.Many2one(
        'res.users', 'Responsible', tracking=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('stock.group_stock_user').id)],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default=lambda self: self.env.user)
    
    product_lines = fields.One2many(
        comodel_name='stock.opname.line',
        inverse_name='stock_opname_id',
        string="Product Lines",
        copy=True, auto_join=True, tracking=True)
    
    hide_button_approval = fields.Boolean(compute='_compute_current_group_approval', default=True)
    
    @api.onchange('warehouse_id')
    def warehouse_id_on_change(self):

        domain = {'location_id': [('warehouse_id', 'in', [self.warehouse_id.id]),('usage', 'not in', ['view'])]}

        return {'domain': domain, 'value': {'location_id': False}}

    @api.depends('current_group_approval')
    def _compute_current_group_approval(self):
        
        if self.state == 'waiting approval':
            for rec in self:
                rec.hide_button_approval = True
                users = rec.current_group_approval.users
                for recipient in users: 
                    if recipient.id == self.env.user.id:
                        rec.hide_button_approval = False
        else:
            for rec in self:
                rec.hide_button_approval = True
    
    def write(self, vals_list):
        string = ""
        for c in vals_list:
            string = string + c
        if ('approver' not in vals_list and 'reject_reason' not in vals_list and 'state' not in vals_list and 'current_group_approval' not in vals_list and 'level_approval' not in vals_list) and self.level_approval > 0:
            raise UserError("You can't Edit Approved Or Waiting Approval Document. " + string)
        else:
            if ('state' not in vals_list) and self.level_approval == 0 and self.state == 'rejected':
                self.state = 'draft'
            return super(StockOpname, self).write(vals_list)
        
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env["ir.sequence"].next_by_code("new.stock.opname.running.no")

        return super().create(vals_list)
    
    def action_generate(self):
        #insert all product to line detail
        products = self.env['product.product'].search([('available_in_pos', '=', True)]) 
        for row in products:
            #cek apakah sudah ada untuk produk ini
            existing = self.env['stock.opname.line'].search([('stock_opname_id', '=', self.id),('product_id', '=', row.id)])
            if(existing) :    
                existing.write({
                    'onhand_qty':row.qty_available,
                    'state':self.state
                    })
            else:
                self.env['stock.opname.line'].create({
                    'stock_opname_id': self.id,
                    'product_id':row.id,
                    'onhand_qty':row.qty_available,
                    'counted_qty':None,
                    'difference_qty':None,
                    'expired_date':None,
                    'notes':None,
                    'state':self.state
                    })
            
        return True
    
    def posting(self):
        #get first scrap location
        domain = [('scrap_location','=',True),('company_id','=',self.env.company.id)]
        scrap_location = self.env['stock.location'].search(domain, limit=1) 

        domain = [('scrap_location','=',False),('active','=',True),('replenish_location','=',False),('company_id','=',self.env.company.id),('usage','=','inventory'),('name','=',"Inventory adjustment")]
        adjustment_location = self.env['stock.location'].search(domain, limit=1) 
        
        #loop product_lines
        for row in self.product_lines:
            if(row.action == 'scrap'):
                for loc in scrap_location:
                    qty = row.difference_qty * -1
                    scrap = self.env['stock.scrap'].create({
                            'name':self.name,
                            'company_id': self.env.company.id,
                            'product_id':row.product_id.id,
                            'product_uom_id':row.product_id.uom_id.id,
                            'scrap_qty':qty,
                            'lot_id':row.lot_id.id,
                            'origin':self.name,
                            'location_id':self.location_id.id,
                            'scrap_location_id':loc.id,
                            })
                    scrap.do_scrap()
                        
            elif(row.action == 'adjustment'):
                for loc in adjustment_location:
                    qty = row.difference_qty
                    if(qty < 0):
                        qty = row.difference_qty * -1
                        #search quant
                        domain = [('product_id','=',row.product_id.id),('location_id', '=', self.location_id.id),('company_id', '=', self.env.company.id),('lot_id','=',row.lot_id.id)]
                        existing_quant = self.env['stock.quant'].search(domain, limit=1)
                        exist = False
                        for row_existing in existing_quant:
                            exist = True
                            row_existing.write({
                                'inventory_diff_quantity':row.difference_qty,
                                'inventory_date':self.date,
                            }) 
                            row_existing.action_apply_inventory()
                        if(exist == False):
                            quant = self.env['stock.quant'].create({
                                'company_id': self.env.company.id,
                                'product_id':row.product_id.id,
                                'location_id':self.location_id.id,
                                'lot_id':row.lot_id.id,
                                'quantity':row.counted_qty,
                                'inventory_date':self.date,
                                })
                            quant.action_apply_inventory()
                    else:
                        move = self.env['stock.move'].create({
                            'name':self.name,
                            'company_id': self.env.company.id,
                            'product_id':row.product_id.id,
                            'product_uom':row.product_id.uom_id.id,
                            'product_uom_qty':qty,
                            'location_id':loc.id,
                            'location_dest_id':self.location_id.id,
                            })

                    
                    
                        move._action_confirm()
                        move._action_assign()
                        move.move_line_ids.write({
                            'qty_done': qty,
                            'reference':self.name,
                            'lot_id':row.lot_id.id
                            }) 
                        move._action_done()

        return True
    
    def action_submit(self):
        #get lowest level in approval quotation and fitted amount total
        domain = []
        limited_records = self.env['stock.opname.approval'].search(domain, limit=1,order='level asc') 
        #limited_records = self.env['sale.order.approval'].search(domain) 

        exist = False
        for row in limited_records:
            exist = True
            for order in self:
                order.state = "waiting approval"
                order.current_group_approval = row.approval_id
                order.level_approval = row.level
                self.action_send_notification(row.approval_id)
                
        #if not defined approval quotation, so make state draft.
        if exist == False:
            for order in self:
                order.state = 'done'
                order.posting()
        
    
    def action_approve(self):
        #get one level upper in approval quotation
        for order in self:
        
            domain = [('level','=',order.level_approval)]
            limited_records = self.env['stock.opname.approval'].search(domain, limit=1,order='level asc') 
            approver = self.approver
            for row in limited_records:
                for order in self:
                    
                    if (approver == False):
                        my_json = {"content": []}
                        dict_data = {
                            "level":order.level_approval,
                            "text": row.name,
                            "user": self.env.user.partner_id.name,
                            "state":"draft"
                        }
                        my_json["content"].append(dict_data)
                        approver = my_json
                    else:
                        dict_data = {
                            "level":order.level_approval,
                            "text": row.name,
                            "user": self.env.user.partner_id.name,
                            "state":"draft"
                        }
                        approver["content"].append(dict_data)
                    order.approver = approver
                    
            domain = [('level','>',order.level_approval)]
            limited_records = self.env['stock.opname.approval'].search(domain, limit=1,order='level asc') 

            exist = False
            for row in limited_records:
                exist = True
                for order in self:
                    order.state = "waiting approval"
                    order.current_group_approval = row.approval_id
                    order.level_approval = row.level
                    order.reject_reason = None
                    self.action_send_notification(row.approval_id)

            #if not exist, so make state draft. 
            if exist == False:          
                for order in self:
                    order.state = 'done'
                    order.current_group_approval = None
                    order.reject_reason = None
                    order.action_send_approval_notification()
                    order.posting()
    
    def action_reject(self):
        for order in self:
            order.level_approval = None
            order.current_group_approval = None
            order.state = "rejected"
            order.action_send_approval_notification()

    def action_send_notification(self, group_name):
        #get lowest level for approval
        stype = "Stock Opname"   
        
        po_msg = '{0} {1} waiting your approval.'.format(stype, self.name)

        message = """<p>{0} Approval:</p><br/>
                    {1}
                    <br />
                    <a href="{2}">click here</a>
                """.format(stype, po_msg, self.get_full_url())
        recipient_partners = self.get_partners_by_group(group_name)
        notification_ids = [
            (0, 0, {
                'res_partner_id': partner_id[1],
                'notification_type': 'inbox'
                }
            ) for partner_id in recipient_partners if recipient_partners
        ]

        self.env['mail.message'].create({
            'message_type':"notification",
            'body': message,
            'subject': "{0} Approval".format(stype),
            'partner_ids': recipient_partners,
            'model': self._name,
            'res_id': self.id,
            'notification_ids': notification_ids,
        })

        return {}
        
    def action_send_approval_notification(self):
        #get lowest level for approval
        if self.state == 'rejected':
            action = "Rejected"
            stype = "Stock Opname"
        else:
            action = "Approved"
            stype = "Stock Opname"   

        
        po_msg = '{0} {1} {2}.'.format(stype, self.name, action)

        message = """<p>{0} Approval:</p>
                    <br/>
                    {1}
                    <br/>
                    <a href="{2}">click here</a>
                """.format(stype, po_msg, self.get_full_url())
        notification_ids = [
            (0, 0, {
                'res_partner_id': self.user_id.partner_id.id,
                'notification_type': 'inbox'
                }
            ) 
        ]

        self.env['mail.message'].create({
            'message_type':"notification",
            'body': message,
            'subject': "{0} Approval".format(stype),
            'partner_ids': [self.user_id.partner_id.id],
            'model': self._name,
            'res_id': self.id,
            'notification_ids': notification_ids,
        })

        return {}
        
    
    def get_full_url(self):
        self.ensure_one()
        base_url = self.sudo().env["ir.config_parameter"].get_param("web.base.url")
        #http://localhost:8069/web#model=sale.order&id=42
        params = (
            "/web#model=stock.opname&id="
            + str(self.id)
        )
        return base_url + params
    
    def get_partners_by_group(self, group_name):
        users = group_name.users
        recipient_partners = []
        for recipient in users: 
            recipient_partners.append(
                (4, recipient.partner_id.id)
            )
        return recipient_partners
    