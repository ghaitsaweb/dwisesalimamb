from odoo import api, SUPERUSER_ID

from . import models
from . import wizards

def my_post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    #do thing
    env.company.po_double_validation = 'one_step'
    so = env['res.config.settings'].browse(env.company.id)
    so.po_order_approval = False