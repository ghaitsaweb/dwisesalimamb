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
    