from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PurchaseOrderReject(models.TransientModel):
    _name = 'purchase.reject'
    reject_reason = fields.Text(string='Reject Reason', required=True, )

    def action_reject_reason(self):
        for rec in self:
            so = rec.env['purchase.order'].browse(rec.env.context.get('active_ids'))
            so.write({
                'reject_reason': rec.reject_reason,
                'approver': None,
            })
            return so.action_reject_po()


    def action_reject_quotation_reason(self):
        for rec in self:
            so = rec.env['purchase.order'].browse(rec.env.context.get('active_ids'))
            so.write({
                'reject_reason': rec.reject_reason,
                'approver': None,
            })
            return so.action_reject_rfq()
    