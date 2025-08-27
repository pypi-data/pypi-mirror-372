from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    instance_ids = fields.One2many('odoo.instance', 'partner_id', string='Instances')
