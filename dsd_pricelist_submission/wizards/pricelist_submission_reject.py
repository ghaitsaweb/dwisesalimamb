from odoo import fields, models, api, _
from odoo.exceptions import UserError

class pricelistsubmissionReject(models.TransientModel):
    _name = 'pricelist.submission.reject'
    reject_reason = fields.Text(string='Reject Reason', required=True, )

    def action_reject_reason(self):
        for rec in self:
            so = rec.env['pricelist.submission'].browse(rec.env.context.get('active_ids'))
            so.write({
                'reject_reason': rec.reject_reason,
                'approver': None,
            })
            return so.action_reject()
    