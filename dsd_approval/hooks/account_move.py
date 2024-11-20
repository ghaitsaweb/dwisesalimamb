# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import groupby


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'utm.mixin']

    state = fields.Selection(selection_add=[("to approve out invoice", "To Approve Invoice"), ('posted',), ("reject out invoice", "Reject Invoice")], ondelete={'to approve out invoice': 'set default', 'reject out invoice':'set default'})
    approver= fields.Json()
    level_approval = fields.Integer(string="Current Level Approval", default=0)
    current_group_approval = fields.Many2one('res.groups', string="Current Approval Group", readonly=True)
    hide_button_approval = fields.Boolean(compute='_compute_current_group_approval', default=True)
    reject_reason = fields.Text(string='Reject Reason', readonly=True)
    
    def write(self, vals_list):
        string = ''
        for rec in vals_list:
            string = string + str(rec)
        if ('approver' not in vals_list and 'reject_reason' not in vals_list and 'access_token' not in vals_list and 'invoice_date' not in vals_list and 'needed_terms_dirty' not in vals_list and 'state' not in vals_list and 'current_group_approval' not in vals_list and 'level_approval' not in vals_list) and self.level_approval > 0 and self.move_type == 'out_invoice':
            raise UserError("You can't Edit Approved Or Waiting Approval Document. " + string)
        else:
            if ('state' not in vals_list) and self.level_approval == 0 and self.state == 'reject out invoice':
                self.state = 'draft'
            return super(AccountMove, self).write(vals_list)

    @api.depends('current_group_approval')
    def _compute_current_group_approval(self):
        
        if self.state == 'to approve out invoice':
            for rec in self:
                rec.hide_button_approval = True
                users = rec.current_group_approval.users
                for recipient in users: 
                    if recipient.id == self.env.user.id:
                        rec.hide_button_approval = False
        else:
            for rec in self:
                rec.hide_button_approval = True

    def action_submit_draft_out_invoice(self):
        #get lowest level in approval sales invoice
        domain = [('approval_type', '=', 'out invoice')]
        limited_records = self.env['sale.order.approval'].search(domain, limit=1,order='level') 
        #limited_records = self.env['sale.order.approval'].search(domain) 

        exist = False
        for row in limited_records:
            exist = True
            for order in self:
                order.state = "to approve out invoice"
                order.current_group_approval = row.approval_id
                order.level_approval = row.level
                self.action_send_notification(row.approval_id)
                
        #if not defined approval quotation, so make state draft.
        if exist == False:
            for order in self:
                order.action_post()

        
    
    def action_approve_out_invoice(self):
        #get one level upper in approval quotation
        for order in self:
        
            domain = [('approval_type', '=', 'out invoice'),('level','=',order.level_approval)]
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
                    
            domain = [('approval_type', '=', 'out invoice'),('level','>',order.level_approval)]
            limited_records = self.env['sale.order.approval'].search(domain, limit=1,order='level') 

            exist = False
            for row in limited_records:
                exist = True
                for order in self:
                    order.state = "to approve out invoice"
                    order.current_group_approval = row.approval_id
                    order.level_approval = row.level
                    self.action_send_notification(row.approval_id)

            #if not exist, so make state draft. 
            if exist == False:          
                for order in self:
                    #order.level_approval = None
                    order.current_group_approval = None
                    order.action_post()
                    order.action_send_approval_notification()
    
    def action_reject_out_invoice(self):
        for order in self:
            order.state = "reject out invoice"
            order.level_approval = None
            order.current_group_approval = None
            order.action_send_approval_notification()
            
    def action_send_notification(self, group_name):
        #get lowest level for approval
        if self.state == 'to approve so':
            stype = "Order"
        elif self.state == 'to approve out invoice':
            stype = "Invoice"
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
        if self.state == 'reject out invoice':
            action = "Rejected"
            stype = "Invoice"
        elif self.state == 'posted':
            action = "Approved"
            stype = "Invoice"
        else:
            action = "Approved"
            stype = "Invoice"   

        
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
            "/web#model=account.move&id="
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