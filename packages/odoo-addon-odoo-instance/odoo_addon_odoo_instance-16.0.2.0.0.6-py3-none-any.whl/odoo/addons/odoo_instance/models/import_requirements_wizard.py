from odoo import models, fields


class ImportRequirementsWizard(models.TransientModel):
    _name = 'odoo.instance.import.requirements.wizard'
    _description = 'Import Requirements Wizard'

    requirements_txt = fields.Text(string='requirements.txt', required=True)

    def action_import(self):
        self.ensure_one()
        odoo_instance = self.env['odoo.instance'].browse(self._context.get('active_id'))
        odoo_instance.import_requirements_txt(self.requirements_txt)
