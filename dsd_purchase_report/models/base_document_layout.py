# -*- coding: utf-8 -*-

from odoo import fields, models

class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'    

    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)
    
    x_akhlak_logo = fields.Binary(related='company_id.x_akhlak_logo', string='Logo Akhlak', readonly=False)

    x_myfield = fields.Char(related='company_id.x_myfield', string='My Field', readonly=False)
    