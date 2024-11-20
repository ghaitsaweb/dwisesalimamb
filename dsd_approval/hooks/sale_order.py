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


class SaleOrder(models.Model):
    _inherit = 'sale.order'    

    state = fields.Selection(selection_add=[("draft_quotation", "Draft Quotation"), ('draft',), ("to approve sq", "To Approve Quotation"), ('draft',), ("to approve so", "To Approve Order"), ('sale',), ("reject sq", "Reject Quotation"), ("reject so", "Reject Order")], default='draft_quotation')
    
    reject_reason = fields.Text(string='Reject Reason', readonly=True)

    level_approval = fields.Integer(string="Current Level Approval", default=0)
    type_approval = fields.Char(string='Type Approval')
    current_group_approval = fields.Many2one('res.groups', string="Current Approval Group", readonly=True)
    approver= fields.Json()
    hide_button_approval_sq = fields.Boolean(compute='_compute_current_group_approval', default=True)
    hide_button_approval_so = fields.Boolean(compute='_compute_current_group_approval', default=True)
    
    def write(self, vals_list):
        if ('approver' not in vals_list and 'reject_reason' not in vals_list and 'state' not in vals_list and 'current_group_approval' not in vals_list and 'level_approval' not in vals_list) and self.level_approval > 0:
            raise UserError("You can't Edit Approved Or Waiting Approval Document. ")
        else:
            if ('state' not in vals_list) and self.level_approval == 0 and self.state == 'reject sq':
                self.state = 'draft_quotation'
            if ('state' not in vals_list) and self.level_approval == 0 and self.state == 'reject so':
                self.state = 'draft'
            return super(SaleOrder, self).write(vals_list)
    
    @api.depends('current_group_approval')
    def _compute_current_group_approval(self):
        
        if self.state == 'to approve sq':
            for rec in self:
                rec.hide_button_approval_so = True
                rec.hide_button_approval_sq = True
                users = rec.current_group_approval.users
                for recipient in users: 
                    if recipient.id == self.env.user.id:
                        rec.hide_button_approval_sq = False
        elif self.state == 'to approve so':
            for rec in self:
                rec.hide_button_approval_sq = True
                rec.hide_button_approval_so = True
                users = rec.current_group_approval.users
                for recipient in users: 
                    if recipient.id == self.env.user.id:
                        rec.hide_button_approval_so = False
        else:
            for rec in self:
                rec.hide_button_approval_sq = True
                rec.hide_button_approval_so = True

    
    def action_submit_draft_quot(self):
        #get lowest level in approval quotation
        domain = [('approval_type', '=', 'quotation')]
        limited_records = self.env['sale.order.approval'].search(domain, limit=1,order='level') 
        #limited_records = self.env['sale.order.approval'].search(domain) 

        exist = False
        for row in limited_records:
            exist = True
            for order in self:
                order.state = "to approve sq"
                order.current_group_approval = row.approval_id
                order.level_approval = row.level
                self.action_send_notification(row.approval_id)
                
        #if not defined approval quotation, so make state draft.
        if exist == False:
            for order in self:
                order.state = 'draft'

        
    
    def action_approve_sq(self):
        #get one level upper in approval quotation
        for order in self:
        
            domain = [('approval_type', '=', 'quotation'),('level','=',order.level_approval)]
            limited_records = self.env['sale.order.approval'].search(domain, limit=1,order='level') 
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
                    
            domain = [('approval_type', '=', 'quotation'),('level','>',order.level_approval)]
            limited_records = self.env['sale.order.approval'].search(domain, limit=1,order='level') 

            exist = False
            for row in limited_records:
                exist = True
                for order in self:
                    order.state = "to approve sq"
                    order.current_group_approval = row.approval_id
                    order.level_approval = row.level
                    order.reject_reason = None
                    self.action_send_notification(row.approval_id)

            #if not exist, so make state draft. 
            if exist == False:          
                for order in self:
                    order.state = 'draft'
                    order.current_group_approval = None
                    order.reject_reason = None
                    order.action_send_approval_notification()
    
    def action_reject_sq(self):
        for order in self:
            order.level_approval = None
            order.current_group_approval = None
            order.state = "reject sq"
            order.action_send_approval_notification()

    def action_submit_to_so(self):
        #get lowest level in approval quotation
        domain = [('approval_type', '=', 'sale order')]
        limited_records = self.env['sale.order.approval'].search(domain, limit=1,order='level') 

        exist = False
        for row in limited_records:
            exist = True
            for order in self:
                order.state = "to approve so"
                order.current_group_approval = row.approval_id
                order.level_approval = row.level
                self.action_send_notification(row.approval_id)
                
                

        #if not defined approval quotation, so make state sale.
        if exist == False:
            for order in self:
                order.level_approval = None
                order.action_confirm()

    def action_reject_so(self):
        for order in self:
            order.level_approval = None
            order.current_group_approval = None
            order.state = "reject so"
            order.action_send_approval_notification()

    def action_approve_so(self):
        #get one level upper in approval quotation
        for order in self:
        
            domain = [('approval_type', '=', 'sale order'),('level','=',order.level_approval)]
            limited_records = self.env['sale.order.approval'].search(domain, limit=1,order='level') 
            approver = self.approver
            for row in limited_records:
                for order in self:
                    
                    if (approver == False):
                        my_json = {"content": []}
                        dict_data = {
                            "level":order.level_approval,
                            "text": row.name,
                            "user": self.env.user.id,
                            "state":"sale"
                        }
                        my_json["content"].append(dict_data)
                        approver = my_json
                    else:
                        dict_data = {
                            "level":order.level_approval,
                            "text": row.name,
                            "user": self.env.user.id,
                            "state":"sale"
                        }
                        approver["content"].append(dict_data)
                    order.approver = approver
                    
            domain = [('approval_type', '=', 'sale order'),('level','>',order.level_approval)]
            limited_records = self.env['sale.order.approval'].search(domain, limit=1,order='level') 

            exist = False
            for row in limited_records:
                exist = True
                for order in self:
                    order.state = "to approve so"
                    order.current_group_approval = row.approval_id
                    order.level_approval = row.level
                    order.reject_reason = None
                    self.action_send_notification(row.approval_id)
                    
                    

            #if not exist, so make state sale. 
            if exist == False:          
                for order in self:
                    order.action_confirm()
                    order.current_group_approval = None
                    order.reject_reason = None
                    order.action_send_approval_notification()

    def action_send_notification(self, group_name):
        #get lowest level for approval
        if self.state == 'to approve so':
            stype = "Order"
        else:
            stype = "Quotation"   

        
        po_msg = 'Sales {0} {1} waiting your approval.'.format(stype, self.name)

        message = """<p>Sales {0} Approval:</p><br/>
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
            'subject': "Sales {0} Approval".format(stype),
            'partner_ids': recipient_partners,
            'model': self._name,
            'res_id': self.id,
            'notification_ids': notification_ids,
        })

        return {}
        
    def action_send_approval_notification(self):
        #get lowest level for approval
        if self.state == 'reject so':
            action = "Rejected"
            stype = "Order"
        elif self.state == 'reject sq':
            action = "Rejected"
            stype = "Quotation"
        elif self.state == 'draft':
            action = "Approved"
            stype = "Quotation"
        elif self.state == 'sale':
            action = "Approved"
            stype = "Order"
        else:
            action = "Approved"
            stype = "Quotation"   

        
        po_msg = 'Sales {0} {1} {2}.'.format(stype, self.name, action)

        message = """<p>Sales {0} Approval:</p>
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
            'subject': "Sales {0} Approval".format(stype),
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
            "/web#model=sale.order&id="
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
    