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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'    

    state = fields.Selection(selection_add=[("draft_rfq", "Draft RFQ"), ('draft',), ("to approve rfq", "To Approve RFQ"), ('draft',), ("to approve po", "To Approve PO"), ('purchase',), ("reject rfq", "Reject RFQ"), ("reject po", "Reject PO")], default='draft_rfq')
    
    reject_reason = fields.Text(string='Reject Reason', readonly=True)

    level_approval = fields.Integer(string="Current Level Approval", default=0)
    type_approval = fields.Char(string='Type Approval')
    current_group_approval = fields.Many2one('res.groups', string="Current Approval Group", readonly=True)
    approver= fields.Json()
    hide_button_approval_rfq = fields.Boolean(compute='_compute_current_group_approval', default=True)
    hide_button_approval_po = fields.Boolean(compute='_compute_current_group_approval', default=True)
    
    def write(self, vals_list):
        string = ""
        for c in vals_list:
            string = string + c
        if ('group_id' not in vals_list and 'name' not in vals_list and 'mail_reminder_confirmed' not in vals_list and 'access_token' not in vals_list and 'message_main_attachment_id' not in vals_list and 'po_no'  not in vals_list and 'approver' not in vals_list and 'reject_reason' not in vals_list and 'state' not in vals_list and 'current_group_approval' not in vals_list and 'level_approval' not in vals_list) and self.level_approval > 0:
            raise UserError("You can't Edit Approved Or Waiting Approval Document. " + string)
        else:
            if ('state' not in vals_list) and self.level_approval == 0 and self.state == 'reject rfq':
                self.state = 'draft_rfq'
            if ('state' not in vals_list) and self.level_approval == 0 and self.state == 'reject po':
                self.state = 'draft'
            return super(PurchaseOrder, self).write(vals_list)
    
    @api.depends('current_group_approval')
    def _compute_current_group_approval(self):
        
        if self.state == 'to approve rfq':
            for rec in self:
                rec.hide_button_approval_po = True
                rec.hide_button_approval_rfq = True
                users = rec.current_group_approval.users
                for recipient in users: 
                    if recipient.id == self.env.user.id:
                        rec.hide_button_approval_rfq = False
        elif self.state == 'to approve po':
            for rec in self:
                rec.hide_button_approval_rfq = True
                rec.hide_button_approval_po = True
                users = rec.current_group_approval.users
                for recipient in users: 
                    if recipient.id == self.env.user.id:
                        rec.hide_button_approval_po = False
        else:
            for rec in self:
                rec.hide_button_approval_rfq = True
                rec.hide_button_approval_po = True

    
    def action_submit_draft_quot(self):
        #jika tidak ada signature, maka gagalkan!
        if not self.env.user.x_approval_sign:
            raise UserError("Please submit E-Sign Approval in My Profile menu.")
        #get lowest level in approval quotation and fitted amount total
        domain = [('approval_type', '=', 'rfq'),('minimum_amount_total','<=', self.amount_total)]
        limited_records = self.env['purchase.order.approval'].search(domain, limit=1,order='level asc, minimum_amount_total desc') 
        #limited_records = self.env['sale.order.approval'].search(domain) 

        exist = False
        for row in limited_records:
            exist = True
            for order in self:
                order.state = "to approve rfq"
                order.current_group_approval = row.approval_id
                order.level_approval = row.level
                self.action_send_notification(row.approval_id)
                
        #if not defined approval quotation, so make state draft.
        if exist == False:
            for order in self:
                order.state = 'draft'

        
    
    def action_approve_rfq(self):
        #jika tidak ada signature, maka gagalkan!
        if not self.env.user.x_approval_sign:
            raise UserError("Please submit E-Sign Approval in My Profile menu.")
        #get one level upper in approval quotation
        for order in self:
        
            domain = [('approval_type', '=', 'rfq'),('level','=',order.level_approval),('minimum_amount_total','<=', self.amount_total)]
            limited_records = self.env['purchase.order.approval'].search(domain, limit=1,order='level asc, minimum_amount_total desc') 
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
                    
            domain = [('approval_type', '=', 'rfq'),('level','>',order.level_approval),('minimum_amount_total','<=', self.amount_total)]
            limited_records = self.env['purchase.order.approval'].search(domain, limit=1,order='level asc, minimum_amount_total desc') 

            exist = False
            for row in limited_records:
                exist = True
                for order in self:
                    order.state = "to approve rfq"
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
    
    def action_reject_rfq(self):
        for order in self:
            order.level_approval = None
            order.current_group_approval = None
            order.state = "reject rfq"
            order.action_send_approval_notification()

    #def _approval_allowed(self):
    #    """Returns whether the order qualifies to be approved by the current user"""
    #    self.ensure_one()
    #    #jika ada approval maka return False;
    #    domain = [('approval_type', '=', 'po'),('minimum_amount_total','<=', self.amount_total)]
    #    limited_records = self.env['purchase.order.approval'].search(domain, limit=1,order='level asc, minimum_amount_total desc') 
#
    #    exist = True
    #    for row in limited_records:
    #        exist = False
#
    #    #check apakah dokume sudah approved ?
    #    #exist = True
    #    
    #    return exist

    def action_submit_to_po(self):
        #jika tidak ada signature, maka gagalkan!
        if not self.env.user.x_approval_sign:
            raise UserError("Please submit E-Sign Approval in My Profile menu.")
        #get lowest level in approval quotation
        domain = [('approval_type', '=', 'po'),('minimum_amount_total','<=', self.amount_total)]
        limited_records = self.env['purchase.order.approval'].search(domain, limit=1,order='level asc, minimum_amount_total desc') 

        self.button_confirm()

        exist = False
        for row in limited_records:
            exist = True
            for order in self:
                order.state = "to approve po"
                order.current_group_approval = row.approval_id
                order.level_approval = row.level
                self.action_send_notification(row.approval_id)
                
                

        #if not defined approval quotation, so make state sale.
        if exist == False:
            for order in self:
                order.level_approval = None

    def action_reject_po(self):
        for order in self:
            order.level_approval = None
            order.current_group_approval = None
            order.state = "reject po"
            order.action_send_approval_notification()

    def action_approve_po(self):
        #jika tidak ada signature, maka gagalkan!
        if not self.env.user.x_approval_sign:
            raise UserError("Please submit E-Sign Approval in My Profile menu.")
        #get one level upper in approval quotation
        for order in self:
        
            domain = [('approval_type', '=', 'po'),('level','=',order.level_approval),('minimum_amount_total','<=', self.amount_total)]
            limited_records = self.env['purchase.order.approval'].search(domain, limit=1,order='level asc, minimum_amount_total desc') 
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
                    
            domain = [('approval_type', '=', 'po'),('level','>',order.level_approval),('minimum_amount_total','<=', self.amount_total)]
            limited_records = self.env['purchase.order.approval'].search(domain, limit=1,order='level asc, minimum_amount_total desc') 

            exist = False
            for row in limited_records:
                exist = True
                for order in self:
                    order.state = "to approve po"
                    order.current_group_approval = row.approval_id
                    order.level_approval = row.level
                    order.reject_reason = None
                    self.action_send_notification(row.approval_id)
                    
                    

            #if not exist, so make state sale. 
            if exist == False:          
                for order in self:
                    order.current_group_approval = None
                    order.reject_reason = None
                    order.button_approve()
                    order.action_send_approval_notification()

    def action_send_notification(self, group_name):
        #get lowest level for approval
        if self.state == 'to approve po':
            stype = "Purchase Order"
        else:
            stype = "RFQ"   

        
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
        if self.state == 'reject po':
            action = "Rejected"
            stype = "Purchase Order"
        elif self.state == 'reject sq':
            action = "Rejected"
            stype = "RFQ"
        elif self.state == 'draft':
            action = "Approved"
            stype = "RFQ"
        elif self.state == 'sale':
            action = "Approved"
            stype = "Purchase Order"
        else:
            action = "Approved"
            stype = "RFQ"   

        
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
            "/web#model=purchase.order&id="
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
    