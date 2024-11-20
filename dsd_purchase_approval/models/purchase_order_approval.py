from odoo import api, fields, models, _
from odoo.exceptions import (
    AccessError,
    UserError,
    RedirectWarning,
    ValidationError,
    Warning,
)

class PurchaseOrderApproval(models.Model):
    _name = "purchase.order.approval"
    _description = "Purchase Order Approval"

    name = fields.Char(string="Description", required=True, )
    approval_type = fields.Selection([("rfq","RFQ"),("po","Purchase Order")], string='Approval Type', required=True)
    level = fields.Integer(string="Level", required=True,default=1)
    approval_id = fields.Many2one('res.groups', string="Approval", required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.company.currency_id.id)
    minimum_amount_total = fields.Monetary(string="Minimum Purchase Total Amount", required=True, default=1)
    
    _sql_constraints = [
        ('uniq_row', 'unique(level,approval_type,minimum_amount_total)', 'Level approval and approval type and  Minimum Purchase Total Amount already exist !')
    ]

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level <= 0:
                raise ValidationError("level must be greater than 0.")