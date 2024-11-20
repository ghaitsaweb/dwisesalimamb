from odoo import api, fields, models, _
from odoo.exceptions import (
    AccessError,
    UserError,
    RedirectWarning,
    ValidationError,
    Warning,
)

class PricelistSubmissionApproval(models.Model):
    _name = "pricelist.submission.approval"
    _description = "Pricelist Submission Approval"

    name = fields.Char(string="Description", required=True, )
    level = fields.Integer(string="Level", required=True,default=1)
    approval_id = fields.Many2one('res.groups', string="Approval Group", required=True)
    
    _sql_constraints = [
        ('uniq_row', 'unique(level,approval_id)', 'Level approval and approval group already exist !')
    ]

    @api.constrains('level')
    def _check_level(self):
        for record in self:
            if record.level <= 0:
                raise ValidationError("level must be greater than 0.")