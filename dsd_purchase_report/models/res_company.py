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

    x_myfield = fields.Char(string="My Custom Field")
    x_akhlak_logo = fields.Binary(string="Logo Akhlak")







