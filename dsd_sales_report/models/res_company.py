# -*- coding: utf-8 -*-

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

class ResCompany(models.Model):
    _inherit = 'res.company'    
    
    x_akhlak_logo = fields.Binary(string="Logo Akhlak")

    is_dsd_purchase_report_installed = fields.Boolean(compute='_compute_is_dsd_purchase_report_installed', default=False)

    def _compute_is_dsd_purchase_report_installed(self):
    
        if self.env['ir.module.module'].search([('state', '=', 'installed'), ('name', '=', 'dsd_purchase_report')]):
            self.is_dsd_purchase_report_installed = True
        else:
            self.is_dsd_purchase_report_installed = False


