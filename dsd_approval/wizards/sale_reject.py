from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SaleOrderReject(models.TransientModel):
    _name = 'sale.reject'
    reject_reason = fields.Text(string='Reject Reason', required=True, )

    def action_reject_reason(self):
        for rec in self:
            so = rec.env['sale.order'].browse(rec.env.context.get('active_ids'))
            so.write({
                'reject_reason': rec.reject_reason,
                'approver': None,
            })
            return so.action_reject_so()


    def action_reject_quotation_reason(self):
        for rec in self:
            so = rec.env['sale.order'].browse(rec.env.context.get('active_ids'))
            so.write({
                'reject_reason': rec.reject_reason,
                'approver': None,
            })
            return so.action_reject_sq()
    
    def action_reject_out_invoice_reason(self):
        for rec in self:
            so = rec.env['account.move'].browse(rec.env.context.get('active_ids'))
            so.write({
                'reject_reason': rec.reject_reason,
                'approver': None,
            })
            return so.action_reject_out_invoice()