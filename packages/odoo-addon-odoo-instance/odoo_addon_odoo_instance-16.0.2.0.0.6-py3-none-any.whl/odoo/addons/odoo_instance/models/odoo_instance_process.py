import logging

from odoo import fields, models, api


class OdooInstanceProcess(models.Model):
    _logger = logging.getLogger(__name__)
    _name = 'odoo.instance.process'
    _description = 'Instance Process'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    module_ids = fields.Many2many(
        "odoo.instance.module",
        "process_module_rel",
        "process_id",
        "module_id",
        string="Related Modules",
        search=['|', ('name', 'ilike', '%search%'),
                ('technical_name', 'ilike', '%search%')]
    )
    handbook_url = fields.Char(string="Handbook URL")
    odoo_version_id = fields.Many2one("odoo.version", string="Odoo Version", required=True)
    instance_ids = fields.Many2many(
        'odoo.instance',
        compute='compute_instance_ids',
        string='Instances',
        search='search_instance_ids'
    )

    def compute_instance_ids(self):
        for record in self:
            instance_ids = self.env['odoo.instance'].search([('process_ids', 'in', record.id)])
            record.instance_ids = instance_ids.ids

    @api.model
    def search_instance_ids(self, operator, value):
        instances = self.env['odoo.instance'].search([('name', operator, value)])
        return [('id', 'in', instances.process_ids.ids)]
