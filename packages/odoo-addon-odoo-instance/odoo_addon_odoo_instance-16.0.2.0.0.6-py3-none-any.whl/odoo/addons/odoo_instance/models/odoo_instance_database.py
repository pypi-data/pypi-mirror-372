from odoo import models, fields
class OdooInstanceDatabase(models.Model):
    _name = 'odoo.instance.database'
    _description = 'Odoo Database'

    name = fields.Char(string='Database Name', required=True)
    is_test = fields.Boolean(string='Is Test Database', default=False)
    instance_id = fields.Many2one('odoo.instance', string='Instance', ondelete='cascade')
