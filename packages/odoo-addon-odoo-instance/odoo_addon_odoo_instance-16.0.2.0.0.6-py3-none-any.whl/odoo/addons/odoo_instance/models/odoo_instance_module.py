import logging

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class OdooInstanceModule(models.Model):
    _name = 'odoo.instance.module'
    _description = 'Odoo Instance Module'

    name = fields.Char(string='Name', required=True)
    technical_name = fields.Char(string='Technical Name', required=True)
    is_odoo_module = fields.Boolean(string='Is Odoo Module', default=True)
    pypi_url = fields.Char(string='PyPI URL')
    version_ids = fields.One2many(
        'odoo.instance.module.version', 'module_id', string='Versions')
    odoo_version_id = fields.Many2one('odoo.version', string="Odoo Version")
    module_type = fields.Selection([
        ('core', 'Odoo Core'),
        ('OCA', 'OCA'),
        ('custom', 'Custom'),
        ('other', 'Other'),
        ('dep', 'Dependency')
    ], string='Module Type', default='custom')

    instance_ids = fields.Many2many(
        'odoo.instance', string='Instances',
        compute='_compute_instance_ids', readonly=True, store=True)

    process_ids = fields.Many2many(
        "odoo.instance.process",
        "process_module_rel",
        "module_id",
        "process_id",
        string="Processes"
    )

    @api.onchange('version_ids.instance_ids')
    @api.depends('version_ids.instance_ids')
    def _compute_instance_ids(self):
        for record in self:
            instance_ids = self.env['odoo.instance']
            for version in record.version_ids:
                instance_ids |= version.instance_ids
            record.instance_ids = instance_ids

    def fetch_pypi_information(self):
        package_info_url = f'https://pypi.org/pypi/{self.name}/json'
        response = requests.get(package_info_url)
        if response.status_code == 200:
            package_data = response.json()
            self.display_name = package_data['info']['name']
            self.is_odoo_module = 'odoo' in package_data['info']['keywords'].lower(
            )

class OdooInstanceModuleVersion(models.Model):
    _name = 'odoo.instance.module.version'
    _description = 'Odoo Instance Module Version'

    name = fields.Char(string='Version', required=True)
    module_id = fields.Many2one(
        'odoo.instance.module', string='Module', required=True, ondelete='cascade')
    instance_ids = fields.Many2many(
        "odoo.instance",
        "module_version_instance_rel",
        "version_id",
        "instance_id",
        string="Instances",
    )

    @api.model
    def archive_or_delete_unassociated_module_versions(self):
        unassociated_module_versions = self.search(
            [('instance_ids', '=', False)])
        unassociated_module_versions.unlink()
        
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context_instance_id = self._context.get("module_instance_ids")
        if context_instance_id:
            args.append(("instance_ids", "in", [context_instance_id]))

        return super(OdooInstanceModuleVersion, self).search(
            args, offset, limit, order, count
        )
