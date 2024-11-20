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


class PricelistSubmission(models.Model):
    _name = 'pricelist.submission'    

    state = fields.Selection([("draft", "Draft"), ("waiting approval", "Waiting Approval"), ("done", "Done"), ("cancel", "Cancel"),("rejected", "Rejected")], default='draft')
    name = fields.Char(string='Submission Name.')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True, states={'done': [('readonly', True)]})
    
    pricelist_id = fields.Many2one(
        'product.pricelist', 'Pricelist', domain="[('active', '=', True)]",
        required=True, states={'done': [('readonly', True)],'waiting approval': [('readonly', True)],'rejected': [('readonly', True)], 'cancel': [('readonly', True)]}, check_company=True, ondelete='cascade')
    
    reject_reason = fields.Text(string='Reject Reason', readonly=True)

    level_approval = fields.Integer(string="Current Level Approval", default=0)
    current_group_approval = fields.Many2one('res.groups', string="Current Approval Group", readonly=True)
    approver= fields.Json()

    user_id = fields.Many2one(
        'res.users', 'Responsible', tracking=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('stock.group_stock_user').id)],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default=lambda self: self.env.user)
    
    product_lines = fields.One2many(
        comodel_name='pricelist.submission.line',
        inverse_name='pricelist_submission_id',
        string="Product Lines",
        copy=True, auto_join=True)
    
    hide_button_approval = fields.Boolean(compute='_compute_current_group_approval', default=True)
    
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
            return super(PricelistSubmission, self).write(vals_list)
        
    #@api.model_create_multi
    #def create(self, vals_list):
    #    for vals in vals_list:
    #        current_month = str(datetime.now().month)
    #        current_year = str(datetime.now().year)
    #        vals['name'] = 'Pricelist ' + self.env.company.name + ' ' + current_month + ' ' + current_year
    #
    #    return super().create(vals_list)
    
    def action_generate(self):
        existing = self.env['pricelist.submission.line'].search([('pricelist_submission_id', '=', self.id)])
        existing.unlink()
        #insert all product to line detail
        products = self.env['product.pricelist.item'].search([('pricelist_id', '=', self.pricelist_id.id)]) 
        for row in products:
            self.env['pricelist.submission.line'].create({
                    'pricelist_submission_id': self.id,
                    'pricelist_id': self.pricelist_id.id,
                    'date_start':row.date_start,
                    'date_end':row.date_end,
                    'min_quantity':row.min_quantity,
                    'applied_on':row.applied_on,
                    'categ_id':row.categ_id.id,
                    'product_tmpl_id':row.product_tmpl_id.id,
                    'product_id':row.product_id.id,
                    'base':row.base,
                    'base_pricelist_id':row.base_pricelist_id.id,
                    'compute_price':row.compute_price,
                    'fixed_price':row.fixed_price,
                    'percent_price':row.percent_price,
                    'price_discount':row.price_discount,
                    'price_round':row.price_round,
                    'price_surcharge':row.price_surcharge,
                    'price_min_margin':row.price_min_margin,
                    'price_max_margin':row.price_max_margin,
                    'name':row.name,
                    'state':self.state
                    })
            
        return True
    
    def posting(self):
        #delete row di pricelist terkait
        products = self.env['product.pricelist.item'].search([('pricelist_id', '=', self.pricelist_id.id)]) 
        products.write({'active': False})

        #insert all from submission
        for row in self.product_lines:
            self.env['product.pricelist.item'].create({
                    'pricelist_id': self.pricelist_id.id,
                    'date_start':row.date_start,
                    'date_end':row.date_end,
                    'min_quantity':row.min_quantity,
                    'applied_on':row.applied_on,
                    'categ_id':row.categ_id.id,
                    'product_tmpl_id':row.product_tmpl_id.id,
                    'product_id':row.product_id.id,
                    'base':row.base,
                    'base_pricelist_id':row.base_pricelist_id.id,
                    'compute_price':row.compute_price,
                    'fixed_price':row.fixed_price,
                    'percent_price':row.percent_price,
                    'price_discount':row.price_discount,
                    'price_round':row.price_round,
                    'price_surcharge':row.price_surcharge,
                    'price_min_margin':row.price_min_margin,
                    'price_max_margin':row.price_max_margin,
                    'name':row.name,
                    'active':True
                    })

        return True
    
    def action_submit(self):
        #get lowest level in approval quotation and fitted amount total
        domain = []
        limited_records = self.env['pricelist.submission.approval'].search(domain, limit=1,order='level asc') 
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
            limited_records = self.env['pricelist.submission.approval'].search(domain, limit=1,order='level asc') 
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
            limited_records = self.env['pricelist.submission.approval'].search(domain, limit=1,order='level asc') 

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
        stype = "Pricelist Submission"   
        
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
            stype = "Pricelist Submission"
        else:
            action = "Approved"
            stype = "Pricelist Submission"   

        
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
            "/web#model=pricelist.submission&id="
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
    