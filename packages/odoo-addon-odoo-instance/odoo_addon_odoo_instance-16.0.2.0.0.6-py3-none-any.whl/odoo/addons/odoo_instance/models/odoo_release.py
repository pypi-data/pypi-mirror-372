from odoo import models, fields


class OdooRelease(models.Model):
    _name = 'odoo.release'
    _description = 'Odoo Release'

    name = fields.Char(string='Release Name', required=True)
    release_date = fields.Date(string='Release Date', required=True)
    odoo_version_id = fields.Many2one('odoo.version', string='Odoo Version', required=True)
    odoo_instance_ids = fields.One2many('odoo.instance', 'odoo_release_id', string='Odoo Instances')
