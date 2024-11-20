# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import (
    UserError,
    Warning,
)

from datetime import timedelta, datetime, date


class ResUsers(models.Model):
    _inherit = 'res.users'    

    x_approval_sign = fields.Binary(string="E-Sign Approval")

    is_dsd_purchase_approval_installed = fields.Boolean(compute='_compute_is_dsd_purchase_approval_installed', default=False)

    def _compute_is_dsd_purchase_approval_installed(self):
    
        if self.env['ir.module.module'].search([('state', '=', 'installed'), ('name', '=', 'dsd_purchase_approval')]):
            self.is_dsd_purchase_approval_installed = True
        else:
            self.is_dsd_purchase_approval_installed = False
    