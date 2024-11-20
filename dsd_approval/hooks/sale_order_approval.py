from odoo import api, fields, models, _
from odoo.exceptions import (
    AccessError,
    UserError,
    RedirectWarning,
    ValidationError,
    Warning,
)

class SalesOrderApproval(models.Model):
    _name = "sale.order.approval"
    _description = "Sales Order Approval"

    name = fields.Char(string="Description", required=True, )
    approval_type = fields.Selection([("quotation","Sales Quotation"),("sale order","Sales Order"),("out invoice","Invoice")], string='Approval Type', required=True)
    level = fields.Integer(string="Level", required=True,default=1)
    approval_id = fields.Many2one('res.groups', string="Approval", required=True)
    
    
    _sql_constraints = [
        ('uniq_row', 'unique(level,approval_type)', 'Level approval and approval type already exist !')
    ]

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level <= 0:
                raise ValidationError("level must be greater than 0.")